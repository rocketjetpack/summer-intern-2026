---
title: Labs
---

# Week 7: Labs

No image build and no new packages this week: everything runs on the existing `nettools:week05` (its iproute2, ping, and tcpdump are all IPv6-capable). The only host prerequisite is that IPv6 isn't administratively disabled on the ContainerLab host; Lab 1 opens with the one-line check.

One lab and one code lab, both in service of the same goal: making everything on the [IPv6 Basics](./basics) page something you've touched rather than something you've read.

Lab 1 requires `sudo` on the ContainerLab host (ContainerLab itself, plus a forwarding sysctl).

## 1. [Lab 1: IPv6 Addressing & Neighbor Discovery](./lab1)

A deliberately unaddressed topology: find the link-locals the kernel already made, fail a ping correctly (zone IDs), capture NS/NA and Duplicate Address Detection with tcpdump, watch the neighbor cache's trust states decay, then build global addressing and finish with a static route via a link-local next-hop.

**Tools:** `ip -6`, `ping`, `traceroute -6`, `tcpdump`.

## 2. [Code Lab: IPv6 Address Anatomy](./address-anatomy)

Before (or alongside) Lab 1: an interactive dissector for any IPv6 address: expansion, RFC 5952 canonical form, scope classification, prefix/interface-ID split at any boundary, and the solicited-node multicast derivation Lab 1 captures on the wire.

---

*Comfortable with the basics? Two stretch topics build directly on this week: [Dual-Stack Operations](../stretch/dual-stack/objectives) runs IPv6 alongside IPv4 and breaks it on purpose, and [OSPFv3](../stretch/ospfv3/objectives) hands the routing over to a protocol, with a head start on the BGP weeks as the payoff.*
