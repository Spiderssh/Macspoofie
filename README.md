# Macspoofie

A simple but effective tool that periodically spoofs your MAC address, launches Tor using bridges with obfuscation, and enables a strict firewall kill-switch to prevent any leaks.

## Features

- Random MAC address every 60 seconds (via macchanger)
- Runs Tor with custom bridges and pluggable transports (obfs4 / meek_lite)
- iptables kill-switch — forces all non-root traffic through Tor
- Automatic cleanup on exit (restores original MAC and firewall)

## Requirements

- Linux (Ubuntu/Debian recommended)
- `macchanger`
- `tor`
- `obfs4proxy`
- Root privileges

```bash
sudo apt update
sudo apt install macchanger tor obfs4proxy
```

```bash
sudo python3 macspoofie.py
```

```bash
-i, --interface     Interface to spoof (default: wlan0)
-t, --interval      MAC change interval in seconds (default: 60)
-b, --bridge        Add a bridge line (can be used multiple times)
--transport         obfs4 or meek_lite (default: obfs4)
```

```bash
sudo python3 macspoofie.py -i wlan0 -t 90 \
  -b "obfs4 Your Real Bridge Here" \
  --transport obfs4
```

## Notes
- Replace the placeholder bridge with real bridges from the Tor Project or a trusted source.
- The script must be run with sudo.
- Press Ctrl+C to stop cleanly.
Stay anonymous.
