---
title: Objectives
---

# Week 3 — Objectives

**Objective:** LLDP, IP addressing and subnetting; MAC vs. IP; L2 switching vs. L3 routing; what an "interface" and a "link" actually are.

By the end of the week you should be able to:

- **Explain what LLDP is and why it matters for topology.**  
  LLDP is a link-layer protocol *(what OSI layer is this?)* where each device periodically advertises "here's who I am and which of my interfaces this is" out of every interface it has. A device's LLDP neighbor table is therefore a direct, machine-readable answer to "what's on the other end of this physical link?"  
  *i.e., it's an edge in the topology graph, discovered automatically rather than assumed from a diagram.*

- **Explain IP addressing and subnetting.**  
  An IP address can be split into two parts: a network portion and a host portion. The subnet mask marks where that split between network and host portions happens.  
  
  Within each subnet, two addresses are reserved and never assigned to a host: the **network address** (every host bit set to `0`), which identifies the subnet itself, and the **broadcast address** (every host bit set to `1`), which is used to address *all* hosts on that subnet at once. Given a network address and subnet mask like `10.0.1.0/255.255.128.0`, be able to identify the network address, the broadcast address, and the range of usable host addresses in between.

- **Understand how subnet masks and CIDR notation relate.**  
  CIDR (Classless Inter-Domain Routing) is the modern mechanism to describe the network that an address is part of. The number after the slash *(the prefix length)* is just a count of how many leading bits of the subnet mask are `1`s. So `/17` and `255.255.128.0` are two ways of writing the exact same mask, because `255.255.128.0` in binary is seventeen `1`s followed by fifteen `0`s. As a stretch mental goal, aim to be able to convert fluently in both directions:
  - **Mask → prefix length:** count the `1` bits. `255.255.255.0` = `11111111.11111111.11111111.00000000` = 24 ones → `/24`.
  - **Prefix length → mask:** lay down that many `1` bits from the left, fill the rest with `0`s, then read it back in dotted-decimal. `/26` → `11111111.11111111.11111111.11000000` → `255.255.255.192`.
  
  The prefix length also tells you the size of a network. A network with a `/N` prefix has `2 ^ (32 - N)` addresses available (including Network and Broadcast addresses).

  For example:
  - `/24` → `2^(32-24) = 2^8 = 256` addresses (254 usable hosts).
  - `/30` → `2^(32-30) = 2^2 = 4` addresses (2 usable hosts) — just enough for a point-to-point link.
  - `/26` → `2^(32-26) = 2^6 = 64` addresses (62 usable hosts).
  - `/16` → `2^(32-16) = 2^16 = 65,536` addresses (65,534 usable hosts).

  *One very important gotcha here is that networks with a CIDR of /31 are very unique and composed of exactly 2 host IPs, no network IP, and no broadcast IP! This will be important when we get to BGP and any other point-to-point connections.*
  
  
- **Distinguish MAC addresses from IP addresses, and explain how ARP connects them.** A MAC address is a flat, link-layer identifier burned into a NIC — it has no notion of "network." An IP address is a hierarchical, routable, logical address assigned by configuration. ARP is the lookup that answers "I have an IP I want to reach on this link — what MAC do I send the frame to?" This is the same ARP you traced in Week 2, now placed in the addressing picture.

- **Explain the difference between L2 switching and L3 routing.** A switch forwards frames within a single broadcast domain by learning MAC-address-to-port mappings (its MAC address table). A router forwards packets *between* networks by consulting a routing table keyed on destination IP/subnet. Same general idea — "look up the destination, send out the right interface" — but at different layers, with different addresses, and different scopes (one network vs. many networks).

- **Explain longest prefix match.** A forwarding table can have more than one entry that matches a given destination — e.g. a `/24` route and a `0.0.0.0/0` default route both match any address in that `/24`. A router always prefers the most specific match: the entry with the *longest* prefix. This is the rule that decides, hop by hop, which way a packet actually goes — see the [Path Explorer](./path-explorer) code lab and the "IP Forwarding Revisited" section of this week's required reading.

- **Define "interface" and "link" precisely.** An interface is a device's addressed attachment point to a network — it has properties like a MAC address, possibly an IP address, a speed, a VLAN membership. A link is the connection *between* two interfaces (a cable, or a point-to-point relationship). Getting this distinction crisp now is what lets next week's topology graph make sense.


**Why it matters for the project:** the visualizer is fundamentally a topology — devices connected by links. This week you learn what those nodes and edges *actually are*: a node is a device with one or more addressed interfaces, and an edge is a link between two specific interfaces. The MAC/ARP/routing tables you inspect in the hands-on lab are the live data that *populates* that graph — this week is where the model and the data source for the model both come into focus.
