---
title: IPv6 Basics
---

# Week 7: IPv6 Basics

**Objective:** understand why IPv6 exists, how its addresses are written and read, and how to recognize what kind of address you're looking at. If you can follow Week 3's IPv4 subnetting, you have all the background you need.

By the end of this page you should be able to:

- **Explain why IPv6 exists.**  
  IPv4's 32-bit space ran out: the free pool was exhausted in 2011, and NAT has been the workaround holding the Internet together since. IPv6's answer is a 128-bit space large enough that addresses simply stop being scarce.

  *Readings: Red Hat's [What you need to know about IPv6](https://www.redhat.com/en/blog/what-you-need-know-about-ipv6); Wikipedia's [IPv4 address exhaustion](https://en.wikipedia.org/wiki/IPv4_address_exhaustion) for the full history.*

  *Questions to consider:*
  - The IPv4 free pool ran out in 2011, yet the IPv4 Internet has kept growing for well over a decade since. When an organization wants to expand their usable IPv4 space, what options does that organization have for obtaining more space? What concerns might an organization looking for space have about the history of a specific block of address space they are considering?

  - A server behind NAT can't accept an inbound connection without special arrangements. What kinds of applications does that quietly make harder to build?

- **Read and write the notation, including the compression rules.**  
  Eight groups of 16 bits, written in hex, separated by colons. Two rules produce the short forms: leading zeros drop within a group, and one run of all-zero groups collapses to `::`. Here is one address, written both ways:

  ```
  2001:0db8:0000:0000:0000:0000:0acd:0017   full form
  2001:db8::acd:17                          the same address, compressed
  ```

  The [Code Lab](./address-anatomy) is the practice ground.

  *Readings: [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) section 2; [RFC 5952](https://datatracker.ietf.org/doc/html/rfc5952) for the canonical short form.*

  *Questions to consider:*
  - Why does `::` only get to appear once per address? What would `2001::db8::1` be ambiguous between?
  - Expand `2001:db8:0:1::1` to its full eight groups by hand, then check yourself in the code lab.

- **Split any address at its prefix boundary.**  
  Slash notation works exactly like Week 3's CIDR, and the near-universal convention is a /64 split: network prefix in the top half, interface identifier in the bottom. One detail to get right from the start: a /64 is assigned to a **network segment** (a VLAN, a link), never to a device. A device holds individual addresses drawn from its segment's /64.

  *This is a widely confusing topic as a /48 contains 1,208,925,819,614,629,174,706,176 addresses (2^80) and very few engineers genuinely understand how large IPv6 space is. It is generally best to not think of individual addresses, but to think of how a network is segmented into logical groups.*

  An example site allocation follows. A site that receives `2001:db8:acad::/48` has 16 bits of subnet space to structure before the /64 boundary, and field practice is to carve them one hex digit (4 bits) at a time so the plan stays readable:

  ```
  2001:db8:acad::/48        the site
  2001:db8:acad:1000::/52   Accounting              (first digit of group 4 = department)
  2001:db8:acad:2000::/52   Engineering
  2001:db8:acad:2001::/64   Engineering lab VLAN    (last three digits = segment)
  2001:db8:acad:2002::/64   Engineering office VLAN
  ```

  Sixteen possible departments could each be allocated a unique /52, each holding 4,096 possible /64 segments, and the whole hierarchy reads straight off the hex digits. Documentation examples, including every address in this week's labs, come from `2001:db8::/32`.

  *Readings: APNIC Blog's [IPv6 architecture and subnetting guide for network engineers and operators](https://blog.apnic.net/2023/04/04/ipv6-architecture-and-subnetting-guide-for-network-engineers-and-operators/) for how this is done in the field; [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) section 2.3; [RFC 6177](https://datatracker.ietf.org/doc/html/rfc6177) on how much space an end site should get; [RFC 3849](https://datatracker.ietf.org/doc/html/rfc3849) on the documentation prefix.*

  *Questions to consider:*
  - In the example plan, what prefix would a new Engineering VLAN get? What would hiring a 17th department break, and what would you change about the plan to accommodate it?

- **Recognize an address's scope on sight.**  
  The leading bits classify an address: link-local (`fe80::/10`), global unicast (`2000::/3`), unique local (`fc00::/7`, which in practice always starts `fd`), multicast (`ff00::/8`), loopback (`::1`). There is no broadcast in IPv6 at all; well-known multicast groups do broadcast's old jobs.

  *Readings: [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) section 2.4; the address-type walkthrough in Red Hat's [What you need to know about IPv6](https://www.redhat.com/en/blog/what-you-need-know-about-ipv6) covers the same ground more gently.*

  *Questions to consider:*
  - Classify these addresses: `fe80::1`, `2001:db8::5`, `ff02::1`, `fd00:12::9`, `::1`.

  - IPv4's 169.254 link-locals usually mean something went wrong. IPv6's are mandatory on every interface by design. What might the designers have wanted them for? (Lab 1 shows you.)

- **Expect several addresses per interface, and name the link when link-locals are involved.**  
   In IPv6, the question "what's the address of that interface" stops being a well-formed question as many interfaces will have a link-local address as well as one or more global addresses. And because the same link-local can legitimately exist on many links, commands that use one need a zone ID: `ping fe80::1%eth1`. Lab 1 has you hit this requirement and explain why the failure without it is correct.

  *Readings: APNIC Blog's [What's the deal with IPv6 link-local addresses?](https://blog.apnic.net/2020/03/30/whats-the-deal-with-ipv6-link-local-addresses/); [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) section 2.5 on interface identifiers.*

  *Questions to consider:*
  - Why can `fe80::1` exist on hundreds of links in the same network without conflict, when a duplicated IPv4 address would be a mistake anywhere?

  - A colleague asks "what's the IP of that server?" What's the more precise question in an IPv6 world?

**Why it matters for the project:** almost every address in the weeks 8-10 BGP arc is an IPv6 address, and the Week 10 production deployment is an IPv6 BGP stack on real Juniper hardware. [Lab 1](./lab1) and the [Code Lab](./address-anatomy) make everything on this page concrete, and when you're comfortable here, two stretch topics extend it: [Dual-Stack Operations](../stretch/dual-stack/objectives) for running IPv6 alongside IPv4, and [OSPFv3](../stretch/ospfv3/objectives) for your first dynamic routing protocol.
