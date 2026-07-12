---
title: Resources
---

# Week 7: Resources

Readings are grouped by the objective they support. Read them before the lab; the last group belongs to Lab 1 itself.

---

## Why IPv6 exists

- **Red Hat: [What you need to know about IPv6](https://www.redhat.com/en/blog/what-you-need-know-about-ipv6)**
  One accessible read that covers most of the Basics page by itself: the exhaustion backstory, hex notation and `::` compression, and the address-type taxonomy (global unicast, link-local, ULA, multicast). If you read only one thing before Lab 1, read this.

- **Wikipedia: [IPv4 address exhaustion](https://en.wikipedia.org/wiki/IPv4_address_exhaustion)**
  The full history with dates and numbers: the 2011 IANA depletion, the per-registry run-out timeline, and NAT's role as the mitigation that bought two extra decades.

## Reading and writing the notation

- **RFC 4291: [IP Version 6 Addressing Architecture](https://datatracker.ietf.org/doc/html/rfc4291)**, sections 2.1 and 2.2
  The primary source for the notation and address model. Dry but short at this depth; the Red Hat article above is the gentle version of the same material.

- **RFC 5952: [A Recommendation for IPv6 Address Text Representation](https://datatracker.ietf.org/doc/html/rfc5952)**
  The canonical-form rules (lowercase, longest zero run compressed, leftmost on ties). The [Code Lab](./address-anatomy) implements exactly these.

## Prefixes and address planning

- **APNIC Blog: [IPv6 architecture and subnetting guide for network engineers and operators](https://blog.apnic.net/2023/04/04/ipv6-architecture-and-subnetting-guide-for-network-engineers-and-operators/)**
  How allocations get carved up in the field: hierarchical plans split one hex digit at a time, a /64 for every VLAN or segment, and worked examples from two real production networks. If the department/VLAN example on the Basics page left you with questions, the answers are here.

- **RFC 4291**, section 2.3 (continuing from above): how prefixes are written.

- **RFC 6177: [IPv6 Address Assignment to End Sites](https://datatracker.ietf.org/doc/html/rfc6177)**
  How much space an end site should receive (/48, /56) and why the answer is sized in years of growth rather than counts of devices.

- **RFC 3849: [IPv6 Address Prefix Reserved for Documentation](https://datatracker.ietf.org/doc/html/rfc3849)**
  Three pages on `2001:db8::/32`, where every address in this week's labs comes from.

## Scopes, link-locals, and zone IDs

- **RFC 4291**, sections 2.4 and 2.5 (continuing from above): the scope taxonomy and the interface-identifier model.

- **APNIC Blog: [What's the deal with IPv6 link-local addresses?](https://blog.apnic.net/2020/03/30/whats-the-deal-with-ipv6-link-local-addresses/)**
  Why link-locals are a designed-in feature rather than IPv4's 169.254 failure symptom, and why using one requires naming the interface (the zone ID you'll hit in Lab 1's first steps).

## For Lab 1: Neighbor Discovery

- **RFC 4861: [Neighbor Discovery for IP version 6](https://datatracker.ietf.org/doc/html/rfc4861)**, section 3 (protocol overview) and section 7.2 (address resolution)
  The ARP-replacement mechanics Lab 1 captures with tcpdump: NS/NA, solicited-node multicast, the neighbor cache states, and Duplicate Address Detection. The rest of the document is reference material; those two sections are enough.

---

## Tools

- **`ip -6` / `ping` / `traceroute -6` / `tcpdump`**: everything Lab 1 needs is already in `nettools:week05`; the iproute2, ping, and tcpdump builds there are all IPv6-capable. No new image and no new packages this week.
