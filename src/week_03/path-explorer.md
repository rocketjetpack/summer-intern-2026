---
title: "Code Lab: Path Explorer"
---

# Code Lab: Path Explorer

The required reading's ["IP Forwarding Revisited"](https://book.systemsapproach.org/internetworking/basic-ip.html) section covers **longest prefix match**. When a destination address matches more than one entry in a routing table, the router picks the most specific (longest) matching prefix to use. This lab follows a packet out onto the real internet, one hop at a time, so you can watch that decision get made over and over, by routers you don't control.

## Background: traceroute and TTL

Every IP packet carries a **TTL (time to live)** field. Each router that forwards the packet decrements TTL by 1; if a router would forward a packet whose TTL has reached 0, it instead drops the packet and sends back an **ICMP "Time Exceeded"** message to the original sender. **`traceroute`** — one of the oldest and most universal networking tools, present in some form on every OS — exploits exactly this: it sends probes with TTL=1, then TTL=2, then TTL=3, and so on, and reports who sends back the Time Exceeded at each step, until a probe finally reaches the destination. The result is a hop-by-hop map of the path your packets actually take.

## Background: private address space (RFC 1918)

Every address you've used so far in Labs 1-3 — `10.0.20.0/24`, `10.0.32.0/30`, and so on — comes from the ranges set aside by [**RFC 1918**](https://datatracker.ietf.org/doc/html/rfc1918) for private networks: `10.0.0.0/8`, `172.16.0.0/12`, and `192.168.0.0/16`. 

That doesn't mean you'll only see one private IP as a hop, though. Large networks route internally across many devices and subnets before traffic ever transits onto the public internet. It's completely normal for the first several hops of a trace to all be private addresses, each one a separate router inside your organization's network, before the addresses turn public. 

Importantly, you should never see RFC 1918 address space as a hop **after** the point where your trace transitions from your oganizations internal network onto the public internet. These RFC 1918 private IP spaces are never allocated on the internet, and no internet router will foward them. 

That would be a [Martian](https://en.wikipedia.org/wiki/Martian_packet) and/or [Bogon](https://en.wikipedia.org/wiki/Bogon_filtering), and would indicate that something *very unusual* is happening.

## Run it

Run `traceroute -n` against a few public destinations, e.g.:

```
traceroute -n 1.1.1.1
traceroute -n 8.8.8.8
traceroute -n google.com
```

*(`-n` skips reverse-DNS lookups for each hop, which makes the output faster and easier to read.) ...and pick a third destination of your choice.*

Read the output line by line. Each line is one hop: a **hop number**, an **IP address**, and **three round-trip times** — `traceroute` sends three probes per hop by default, one per column. A few things you'll likely run into:

- A hop showing `* * *` means none of the three probes for that hop got a reply — a router along the path isn't sending Time Exceeded messages, or something is rate-limiting/dropping them. This is normal and itself worth discussing: why might a network operator configure a router this way? What might this have to do with the Martians or Bogons referenced above?

- The RTTs for a single hop can vary noticeably between the three probes as different probes can take slightly different paths through complex networks.

- The last hop is your destination, its IP should match what you traced to. Not all networks are configured to allow route tracing beyond some chosen point in an organizations network. This often shows up as repeated "* * *" lines in the output until the maximum number of hops has been reached. Why might an organization construct their network to behave like this?

## Questions to investigate

- What's hop 1's address? Compare it to your default gateway (`ip route show default`). This is your own L2/L3 pivot point: your NIC ARPs for that address's MAC on your local link (pure L2), and from there, every further hop is a separate device making its own L3 forwarding decision — exactly like `sw1` and `rtr1` in [Lab 3](./lab3), just at internet scale and with routers you don't control.

- For each hop's IP, is it private (RFC1918) or public? You can check quickly from a Python REPL with the same module as [Subnet Helper](./subnet-helper): `ipaddress.ip_address("10.0.0.1").is_private`. At what hop does the path leave your private address space and enter the public internet?

- Trace to two different public destinations. Where do the paths diverge? Every router along each path is doing its own longest-prefix-match lookup (the "IP Forwarding Revisited" reading above) against its own forwarding table, not yours.

- How many hops does it take to leave your private address space? Does that match what you'd expect from your network's topology?

- Try this both from your workstation and from the ContainerLab server that you have access to. You may see very different routes depending on which system you start your trace from.
