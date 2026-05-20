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
sudo python3 macspoofie.py -i wlan0 -t 60 \
  -b "obfs4 Your Real Bridge Here" \
  --transport obfs4
```

```bash
git clone https://github.com/Spiderssh/Macspoofie.git
```

## Notes
- Replace the placeholder bridge with real bridges from the Tor Project or a trusted source.
- The script must be run with sudo.
- Press Ctrl+C to stop cleanly.
Stay anonymous.

## LICENSE 
MIT License

Copyright (c) 2026 Spiderssh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
