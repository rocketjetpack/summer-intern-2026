---
title: Terminology
---

# Week 7: Terminology

| Term / Acronym | Definition |
|---|---|
| **2001:db8::/32** | The IPv6 prefix reserved for documentation and examples ([RFC 3849](https://datatracker.ietf.org/doc/html/rfc3849)); never routed on the real Internet. All addresses in this week's labs come from it |
| **DAD** | Duplicate Address Detection: before using a new address, a node sends a Neighbor Solicitation for that address itself and only claims it if nobody answers |
| **GUA** | Global Unicast Address (`2000::/3`): globally routable IPv6 space, the counterpart of a public IPv4 address |
| **Link-Local** | An address in `fe80::/10`, automatically present on every IPv6 interface and valid only on its own link; never routed, and the substrate IPv6 routing protocols run their sessions and next-hops over |
| **NA** | Neighbor Advertisement: the ICMPv6 answer to a Neighbor Solicitation (message type 136); IPv6's ARP reply |
| **ND** | Neighbor Discovery ([RFC 4861](https://datatracker.ietf.org/doc/html/rfc4861)): the ICMPv6 protocol family replacing ARP, covering address resolution, DAD, and router discovery |
| **Neighbor Cache** | The IPv6 counterpart of the ARP table (`ip -6 neigh show`), with explicit per-entry trust states: `REACHABLE`, `STALE`, `DELAY`, `PROBE` |
| **NS** | Neighbor Solicitation: the ICMPv6 request asking which MAC owns an IPv6 address (message type 135), sent to the target's solicited-node multicast group rather than broadcast |
| **RA / RS** | Router Advertisement / Router Solicitation: the ND messages driving host autoconfiguration (SLAAC); recognize the names, deferred as a topic since the lab configures addresses deliberately |
| **SLAAC** | Stateless Address Autoconfiguration: hosts building their own addresses from RA-advertised /64 prefixes; the reason the 64-bit interface-identifier convention is load-bearing |
| **Solicited-Node Multicast** | The group `ff02::1:ff` + the last 24 bits of a unicast address; each node joins it per address, letting an NS reach only the node(s) it concerns instead of the whole segment |
| **ULA** | Unique Local Address (`fc00::/7`, in practice always starting `fd`): private, non-Internet-routable IPv6 space, the counterpart of RFC 1918 |
| **Zone ID** | The `%eth1` suffix required when using a link-local address in a command, resolving which link the address is valid on (`ping fe80::1%eth1`) |
