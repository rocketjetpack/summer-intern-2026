---
title: Resources
---

# Week 8: Resources

Readings are grouped by the objective they support. Two of them recur all week: Kentik's tutorial is the approachable narrative, and Dordal's open textbook chapter is the academic treatment of the same ground. Neither needs to be read cover to cover; the sections below are the assignment.

---

## Autonomous systems and the IGP/EGP split

- **Kentik: [BGP Routing: An In-Depth Tutorial](https://www.kentik.com/kentipedia/bgp-routing/)**
  Start here. The opening sections cover what an AS is, what ASNs are, and why inter-domain routing is a policy problem rather than a shortest-path problem. The whole tutorial is worth finishing over the course of the week; it touches nearly everything on the Basics page.

- **Peter Dordal: [An Introduction to Computer Networks, chapter 15 (BGP)](https://intronetworks.cs.luc.edu/current/html/bgp.html)**, chapter introduction
  A free, actively maintained university textbook. The introduction frames the interior/exterior split memorably: interior routing is "neat and mathematical," exterior routing is "messy and arbitrary." Sections of this chapter appear against several objectives below.

## What BGP is: path vector, TCP, AS_PATH

- **RFC 4271: [A Border Gateway Protocol 4 (BGP-4)](https://datatracker.ietf.org/doc/html/rfc4271)**, sections 1 and 3
  The protocol's defining document. Section 1 is a two-page introduction and section 3 (Summary of Operation) is the readable core: speakers, sessions, the routing information bases, and what an UPDATE means. The rest of the document is reference material; resist reading it linearly.

- **Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html)**, section 15.1 (AS-paths)
  How the AS_PATH is built hop by hop and why reading your own ASN in a received path means "loop, discard."

## eBGP versus iBGP

- **Kentik's [tutorial](https://www.kentik.com/kentipedia/bgp-routing/)**, the eBGP/iBGP section
  The distinction, plus why iBGP peers are typically loopbacks rather than physical interfaces.

- **Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html)**, section 15.9 (BGP for Interior Routing)
  When BGP shows up *inside* a network, and what it does there that an IGP can't. Directly relevant here: the production network runs eBGP internally, edge routers to core switches.

- **RFC 6996: [Autonomous System (AS) Reservation for Private Use](https://datatracker.ietf.org/doc/html/rfc6996)**
  Two pages: the private ASN ranges that make internal eBGP designs possible without registry-assigned numbers.

## The session: states, messages, timers

- **RFC 4271**, section 4 (Message Formats)
  OPEN, UPDATE, KEEPALIVE, NOTIFICATION: four message types, each a couple of pages. Section 8 holds the full finite state machine if you want the formal version; recognizing the state names is the goal at this depth.

## Reading the table: best path, RIB, FIB

- **FRR documentation: [BGP](https://docs.frrouting.org/en/latest/bgp.html)**, the Route Selection section
  The decision sequence FRR actually runs, in order. Notice how far down the list AS_PATH length sits and how many policy knobs precede it; next week is about those knobs.

- **Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html)**, section 15.6 (BGP Path Attributes)
  The attribute vocabulary (NEXT_HOP, LOCAL_PREF, MED) at textbook depth. Skim for recognition now; Week 9 leans on it hard.

## BGP and IPv6

- **RFC 2545: [Use of BGP-4 Multiprotocol Extensions for IPv6 Inter-Domain Routing](https://datatracker.ietf.org/doc/html/rfc2545)**
  Four pages, the primary source: how IPv6 reachability rides BGP, and the rule that gives a next-hop both a global and a link-local address for directly connected peers.

- **RFC 4760: [Multiprotocol Extensions for BGP-4](https://datatracker.ietf.org/doc/html/rfc4760)**, sections 1-3
  The address-family mechanism itself: how one protocol came to carry routes for anything. The reason `address-family ipv6 unicast` and `activate` exist in FRR BGP configuration.

## Policy defaults and transit

- **RFC 8212: [Default External BGP (EBGP) Route Propagation Behavior without Policies](https://datatracker.ietf.org/doc/html/rfc8212)**
  Short and consequential: an eBGP speaker with no configured policy should accept nothing and advertise nothing. FRR implements this, and the first time you bring up an eBGP session you will meet it: Established, yet not one route exchanged until policy (or an explicit opt-out) says otherwise.

- **Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html)**, sections 15.3 (Transit Traffic) and 15.10 (BGP Relationships)
  What transit is, and the customer/provider/peer relationship taxonomy that decides who advertises what to whom. A dual-homed network that leaks each upstream's routes to the other has accidentally become a transit provider between its own ISPs; these sections explain why that accident costs real networks real money.

- **FRR documentation: [BGP](https://docs.frrouting.org/en/latest/bgp.html)**
  The configuration reference for the FRR BGP work in this arc: `router bgp`, `neighbor`, `address-family ipv6 unicast`, `network`, and the `show bgp` family.

## The production context

- **Wikipedia: [Internet2](https://en.wikipedia.org/wiki/Internet2)**
  The national research and education network: one of the two external feeds the Week 10 production deployment peers with, alongside a commodity Internet provider. [Internet2's own site](https://internet2.edu/) has the current network map and member list.
