---
title: Resources
---

# Week 3 — Resources

## Required Readings

- [Computer Networks: A Systems Approach — 3.3 Internet (IP)](https://book.systemsapproach.org/internetworking/basic-ip.html) — the core reading for this week: global addressing, subnetting and classless addressing (CIDR), datagram forwarding, and ARP, all in one section. Pay particular attention to **"IP Forwarding Revisited"**, which covers **longest prefix match** — how a router picks between multiple matching forwarding-table entries. The [Path Explorer](./path-explorer) code lab is built around this idea.
- [Beej's Guide to Networking Concepts](https://beej.us/guide/bgnet0/html/) — read the IPv4 addressing/subnet-mask chapters and the dedicated "IP Subnets and Subnet Masks" chapter, plus the link-layer/Ethernet (MAC addresses) and ARP chapters. Covers network and broadcast addresses (the all-`0`s and all-`1`s host-bit cases) in detail. Same Python-friendly, low-jargon style as Week 2's reading.
- Cloudflare Learning Center: [What is a subnet?](https://www.cloudflare.com/learning/network-layer/what-is-a-subnet/) — short, plain-English explanation of subnet masks, why networks get carved up, and what the network and broadcast addresses at each end of a subnet are for.
- Cloudflare Learning Center: [What is routing?](https://www.cloudflare.com/learning/network-layer/what-is-routing/) — companion piece: how a router uses a routing table to pick a path, the L3 half of this week's L2-vs-L3 distinction.
- [Link Layer Discovery Protocol — Wikipedia](https://en.wikipedia.org/wiki/Link_Layer_Discovery_Protocol) — how devices announce themselves to their directly-connected neighbors, and why that's the basis for automated topology discovery.

## Recommended Readings

- [Inter VLAN Routing by Layer 3 Switch — GeeksforGeeks](https://www.geeksforgeeks.org/computer-networks/inter-vlan-routing-layer-3-switch/) — SVIs vs. router-on-a-stick; read this before Lab 2, where you'll configure a switch to do exactly this.  
- [Computer Networks: A Systems Approach — 3.4 Routing](https://book.systemsapproach.org/internetworking/routing.html) — a deeper, more rigorous treatment of routing tables and routing algorithms, if you want to go beyond the Cloudflare overview.
- Practical Networking: [Virtual Local Area Networks (VLANs)](https://www.practicalnetworking.net/stand-alone/vlans/) — the clearest walkthrough of *why* VLANs exist and how access vs. trunk ports work; read this before Lab 2 if VLANs are new to you.
- [Containerlab Quick Start](https://containerlab.dev/quickstart/) — you'll need this for Labs 1-3; skim it now so the lab steps make sense.

## Docker

Containerlab runs each lab node as a Docker container, so a little Docker familiarity goes a long way. Work through the [Docker Lab](../tools/docker) before Lab 1 — it builds `nettools:week03`, the host image Labs 1-3 use for every Linux node. Or go straight to the source:

- [What is a container? (Docker Docs)](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/) — the core concept in a few minutes.
- [Get started (Docker Docs)](https://docs.docker.com/get-started/) — a hands-on first run with Docker, useful if you've never used it before.
- [`docker container` CLI reference](https://docs.docker.com/reference/cli/docker/container/) — full reference for `ps`, `exec`, `logs`, and friends.
