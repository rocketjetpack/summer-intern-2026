---
title: Resources
---

# Week 9: Resources

Readings are grouped by the objective they support. If AS_PATH, session mechanics, or MP-BGP need a refresher first, they're on Week 8's [resources](../week_08/resources) page.

---

## Building a session, and RFC 8212 in practice

- **RFC 8212: [Default External BGP (EBGP) Route Propagation Behavior without Policies](https://datatracker.ietf.org/doc/html/rfc8212)**
  Worth a second read with a working session in front of you. [Lab 1](./lab1) triggers this rule directly and shows FRR's `(Policy)` marker for it.

## Transit accidents

- **Peter Dordal: [An Introduction to Computer Networks, chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html)**, section 15.3 (Transit Traffic)
  What transit is and what it costs a network that provides it unintentionally. [Lab 1](./lab1) Step 7 reproduces the accident directly.

## Prefix-lists and route-maps

- **FRR documentation: [Filtering](https://docs.frrouting.org/en/latest/filter.html)**
  The `ip prefix-list` / `ipv6 prefix-list` reference: syntax, sequence numbers, the `le`/`ge` length modifiers, and the implicit deny that ends every prefix-list. [Lab 2](./lab2) Steps 1 and 5 are built entirely from this page's vocabulary.

- **FRR documentation: [Route Map](https://docs.frrouting.org/en/latest/routemap.html)**
  How a `route-map` wraps prefix-list matches into a named policy a `neighbor ... route-map ... in` statement can reference. Skim for the `match`/`set` structure; Lab 2 only needs `match`.

## Longest-prefix-match, revisited

- **Week 3: [Path Explorer](../week_03/path-explorer)**, and the "IP Forwarding Revisited" reading it's built around
  The forwarding rule that makes [Lab 2](./lab2)'s specific-vs-default design work without any BGP tiebreaking at all: whichever route is more specific wins, regardless of which peer it came from.

## Full-mesh topology and MCLAG

- **ipSpace.net: [Multi-Chassis Link Aggregation](https://blog.ipspace.net/series/mlag/)**
  A vendor-neutral series on what MLAG/MCLAG actually does: two physical switches presenting as one logical device to whatever dual-homes to them, coordinated over a peer link. Read for the concept; [Lab 2](./lab2)'s peer link between `sw1` and `sw2` is addressed but does not run this protocol, which the lab states plainly.

---

## Tools

- **FRR 10.6.1** (`quay.io/frrouting/frr:10.6.1`): the routing suite for every container this week, pulled and pinned in [Lab 0](./lab0).
- **containerlab `kind: bridge`**: the node type behind Lab 2's cross-deployment hand-off, explained where it's used.
- **`ip route get` / `ip -6 route get`**: the kernel FIB lookup Lab 2 uses to prove routing behavior without needing anything to actually be reachable.
