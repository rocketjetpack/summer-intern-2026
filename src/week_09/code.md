---
title: Labs
---

# Week 9: Labs

No image build this week: every router runs the FRR image pulled and pinned in [Lab 0](./lab0). All three labs require the ContainerLab host and `sudo`.

## 1. [Lab 0: Prepare the FRR Router Image](./lab0)

Pull and verify `quay.io/frrouting/frr:10.6.1`, and write the `daemons` file (`bgpd=yes`) every other lab this week bind-mounts in.

**Tools:** `docker`.

## 2. [Lab 1: Your First eBGP Peerings (IPv6)](./lab1)

Three routers, three ASes, every line of BGP typed live: a session stuck in `Active`, the OPEN/KEEPALIVE handshake on tcpdump, an RFC 8212 collision, a wrong-ASN NOTIFICATION, an accidental transit provider, and a route traced from the BGP table through the RIB to a kernel FIB entry with a link-local next-hop.

**Tools:** `containerlab`, `vtysh`, `ip -6`, `tcpdump`, `ping`.

## 3. [Lab 2: Selective Route Acceptance at a Dual-Edge Boundary](./lab2)

Production-scale BGP: two upstream feeds (a full public-Internet table and an Internet2 subset), unfiltered, behind a redundant pair of switches. A working IPv4 acceptance policy is handed to you as a worked example; you build the identical IPv6 policy yourself, prove the design with `ip route get`/`ip -6 route get`, and fail an upstream to watch graceful degradation.

**Tools:** `containerlab`, `vtysh`, `ip route get` / `ip -6 route get`.
