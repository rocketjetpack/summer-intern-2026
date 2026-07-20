---
title: Terminology
---

# Week 8: Terminology

| Term / Acronym | Definition |
|---|---|
| **AS** | Autonomous System: a network under one administrative control with one coherent routing policy (an ISP, a university, a cloud provider); the unit the Internet's routing is organized around |
| **ASN** | AS Number: the number identifying an AS in BGP. Originally 16-bit, extended to 32-bit by [RFC 6793](https://datatracker.ietf.org/doc/html/rfc6793). The range 64496-64511 is reserved for documentation ([RFC 5398](https://datatracker.ietf.org/doc/html/rfc5398)); all ASNs in this week's labs come from it |
| **Address Family** | The kind of routes a BGP session carries (IPv4 unicast, IPv6 unicast, and others), negotiated per session via the multiprotocol extensions; in FRR each neighbor is activated per family |
| **Administrative Distance** | The RIB's trust ranking between route sources when several offer the same prefix; FRR defaults: connected 0, static 1, eBGP 20, OSPF 110, iBGP 200 |
| **AS_PATH** | The BGP attribute listing every AS an advertisement has traversed, prepended at each AS boundary; provides loop prevention (reject a path containing your own ASN) and the everyday best-path tiebreaker (shorter wins) |
| **BGP** | Border Gateway Protocol, version 4 ([RFC 4271](https://datatracker.ietf.org/doc/html/rfc4271)): the path-vector EGP that routes between autonomous systems; in practice, the routing protocol of the Internet |
| **eBGP** | External BGP: a session between routers in different ASes, normally directly connected; prepends the local ASN when passing routes across. The AS boundary is often organizational (you and your ISP) but need not be: private-ASN designs run eBGP inside one network, as the production network does between its edge routers and core switches |
| **EGP / IGP** | Exterior vs Interior Gateway Protocol: the split between routing *between* administrative domains (BGP, policy-driven) and routing *inside* one (OSPF, IS-IS, shortest-path-driven) |
| **Established** | The final BGP session state, the only one in which routes are exchanged; everything before it (`Idle`, `Connect`, `Active`, `OpenSent`, `OpenConfirm`) is connection setup and negotiation |
| **FIB** | Forwarding Information Base: the table the kernel actually forwards packets with (`ip -6 route`); holds only each prefix's winning route |
| **Hold Time / Keepalive** | BGP's liveness timers: KEEPALIVEs flow every keepalive interval (FRR default 60s), and a peer silent past the hold time (FRR default 180s, negotiated to the lower of the two OPENs) is declared down, withdrawing its routes |
| **iBGP** | Internal BGP: a session between routers in the same AS, used to carry externally learned routes across the inside of an AS without losing their BGP attributes; typically runs between loopbacks kept reachable by an IGP |
| **MP-BGP** | Multiprotocol BGP ([RFC 4760](https://datatracker.ietf.org/doc/html/rfc4760)): the extensions letting one BGP speak for multiple address families; how BGP-4 carries IPv6 ([RFC 2545](https://datatracker.ietf.org/doc/html/rfc2545)) |
| **NLRI** | Network Layer Reachability Information: the prefixes an UPDATE message advertises; RFC-speak worth recognizing because FRR counts routes in "pfx" (prefix) columns and logs |
| **NOTIFICATION** | The BGP error message; always fatal to the session that sends or receives it (for example `Bad Peer AS` when the configured and actual remote ASNs disagree) |
| **Private ASN** | AS numbers reserved by [RFC 6996](https://datatracker.ietf.org/doc/html/rfc6996) (64512-65534, plus a 32-bit range) for networks that don't need globally unique numbers; what makes internal eBGP designs possible without consuming registry ASNs |
| **Path Vector** | The routing-protocol family BGP belongs to: advertisements carry the full path of ASes traversed rather than a numeric cost, so loop detection and policy both read straight off the path |
| **Peer / Neighbor** | The router on the far end of a configured BGP session; BGP has no discovery, so every peer is the result of someone typing a `neighbor` statement |
| **RIB** | Routing Information Base: the router's collection of candidate routes from all sources (connected, static, each protocol), arbitrated by administrative distance; `show ipv6 route` in FRR |
| **Transit** | Carrying traffic between two other ASes, neither of which is you; what a customer buys from an ISP, and what a dual-homed organization must take care not to give its upstreams for free |
| **UPDATE** | The BGP message that advertises routes (prefixes plus attributes such as AS_PATH and next-hop) and withdraws dead ones; a session at rest exchanges only KEEPALIVEs |
