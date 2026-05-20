#!/usr/bin/env python3

import argparse
import atexit
import os
import signal
import subprocess
import sys
import time

# --------------------- Configuration ---------------------
INTERFACE = "wlan0"
INTERVAL = 60

BRIDGES = [
    "obfs4 1.2.3.4:1234 ABCDEF1234567890ABCDEF1234567890ABCDEF12 cert=abcdef1234567890abcdef1234567890abcdef1234567890abcdef12 iat-mode=0",
]

TRANSPORT = "obfs4"          # "obfs4" or "meek_lite"

TOR_SOCKS_PORT = 9050
TOR_TRANS_PORT = 9040
TOR_DNS_PORT = 5353
TOR_USER = "debian-tor"
# -------------------------------------------------------

tor_proc = None
iptables_rules_set = False
orig_mac = None


def log(msg):
    print(f"[*] {msg}")


def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, check=check,
                          capture_output=True, text=True)


def get_current_mac(iface):
    out = run(f"ip link show {iface}").stdout
    for line in out.splitlines():
        if "link/ether" in line:
            return line.strip().split()[1]
    raise RuntimeError(f"Could not read MAC from {iface}")


def randomize_mac(iface):
    log(f"Changing MAC on {iface}...")
    run(f"ip link set dev {iface} down")
    run(f"macchanger -r {iface}")
    run(f"ip link set dev {iface} up")

    if os.path.exists("/usr/sbin/dhclient"):
        run(f"dhclient -v {iface}", check=False)
    elif os.path.exists("/usr/bin/dhcpcd"):
        run(f"dhcpcd -k {iface}; dhcpcd {iface}", check=False)

    log(f"New MAC: {get_current_mac(iface)}")


def write_torrc(bridges, transport):
    torrc = f"""SocksPort {TOR_SOCKS_PORT}
TransPort {TOR_TRANS_PORT}
DNSPort {TOR_DNS_PORT}
UseBridges 1
ClientTransportPlugin {transport} exec /usr/bin/obfs4proxy
"""
    for bridge in bridges:
        torrc += f"Bridge {bridge}\n"

    if transport == "meek_lite":
        torrc = torrc.replace(
            f"ClientTransportPlugin {transport} exec /usr/bin/obfs4proxy",
            "ClientTransportPlugin meek_lite exec /usr/bin/obfs4proxy"
        )

    with open("/tmp/torrc.spoof", "w") as f:
        f.write(torrc)
    log("Tor configuration written.")


def start_tor():
    global tor_proc
    cmd = f"tor -f /tmp/torrc.spoof --RunAsDaemon 0"
    log("Starting Tor...")
    tor_proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for _ in range(30):
        time.sleep(2)
        if tor_proc.poll() is not None:
            _, err = tor_proc.communicate()
            raise RuntimeError(f"Tor exited early: {err.decode()}")

        log_output = run("tail -n 20 /var/log/tor/log", check=False).stdout
        if "Bootstrapped 100%" in log_output:
            log("Tor connected and ready.")
            return

    raise RuntimeError("Tor did not bootstrap in time.")


def setup_kill_switch():
    global iptables_rules_set
    log("Setting up kill-switch firewall...")

    run("iptables-save > /tmp/iptables.backup")
    run("iptables -F")
    run("iptables -t nat -F")
    run("iptables -t mangle -F")

    run("iptables -A OUTPUT -o lo -j ACCEPT")
    run(f"iptables -A OUTPUT -m owner --uid-owner {TOR_USER} -j ACCEPT")
    run(f"iptables -t nat -A OUTPUT -p tcp -m owner ! --uid-owner root -j REDIRECT --to-ports {TOR_TRANS_PORT}")
    run(f"iptables -t nat -A OUTPUT -p udp --dport 53 -m owner ! --uid-owner root -j REDIRECT --to-ports {TOR_DNS_PORT}")
    run("iptables -A OUTPUT -m owner ! --uid-owner root -j DROP")

    iptables_rules_set = True
    log("Kill-switch active.")


def restore_system_state():
    global iptables_rules_set, tor_proc
    log("Restoring system state...")

    if tor_proc:
        tor_proc.terminate()
        tor_proc.wait()
        log("Tor stopped.")

    if iptables_rules_set and os.path.exists("/tmp/iptables.backup"):
        run("iptables-restore < /tmp/iptables.backup", check=False)
        os.remove("/tmp/iptables.backup")
        log("Firewall restored.")
        iptables_rules_set = False

    if orig_mac:
        log(f"Restoring original MAC ({orig_mac})")
        run(f"ip link set dev {INTERFACE} down")
        run(f"ip link set dev {INTERFACE} address {orig_mac}")
        run(f"ip link set dev {INTERFACE} up")

    if os.path.exists("/tmp/torrc.spoof"):
        os.remove("/tmp/torrc.spoof")


def signal_handler(sig, frame):
    log("Signal received. Shutting down...")
    restore_system_state()
    sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(description="Macspoofie - MAC spoofing + Tor bridge runner with killswitch")
    parser.add_argument("-i", "--interface", default=INTERFACE,
                        help="Network interface (default: wlan0)")
    parser.add_argument("-t", "--interval", type=int, default=INTERVAL,
                        help="Seconds between MAC changes")
    parser.add_argument("-b", "--bridge", action="append", dest="bridges",
                        help="Bridge line (repeatable)")
    parser.add_argument("--transport", choices=["obfs4", "meek_lite"],
                        default=TRANSPORT)
    return parser.parse_args()


def main():
    global INTERFACE, INTERVAL, BRIDGES, TRANSPORT, orig_mac

    args = parse_args()
    INTERFACE = args.interface
    INTERVAL = args.interval
    if args.bridges:
        BRIDGES = args.bridges
    TRANSPORT = args.transport

    if os.geteuid() != 0:
        log("This script must be run as root!")
        sys.exit(1)

    atexit.register(restore_system_state)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    orig_mac = get_current_mac(INTERFACE)
    log(f"Original MAC: {orig_mac}")

    write_torrc(BRIDGES, TRANSPORT)
    start_tor()
    setup_kill_switch()

    log(f"Macspoofie running. MAC will change every {INTERVAL} seconds. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(INTERVAL)
            randomize_mac(INTERFACE)
    except KeyboardInterrupt:
        pass
    finally:
        restore_system_state()


if __name__ == "__main__":
    main()
