---
title: "Code Lab: Subnet Helper"
---

# Code Lab: Subnet Helper

Using Python's [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) module, build a small subnet helper. Given a CIDR string (e.g. `"10.0.20.0/24"`), your helper should be able to:

- Report the **network address** and **broadcast address** (`.network_address`, `.broadcast_address`).
- List the **usable host addresses** (`.hosts()` — note this already excludes the network and broadcast addresses).
- Test whether a given IP address is a **member** of the subnet (`ip_address in ip_network`).

Try it against the addressing from [Lab 2](./lab2) and [Lab 3](./lab3):

- Does the helper's idea of "usable hosts" for `10.0.20.0/24` and `10.0.21.0/24` match the SVI and host addresses you actually assigned?
- What does your helper report for the `/30` transit link between `sw1` and `rtr1` in Lab 3? How many usable hosts does it find, and does that match what you'd expect for a point-to-point link (recall the `/31` gotcha from `objectives.md`)?
