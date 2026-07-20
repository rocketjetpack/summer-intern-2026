---
title: "OSPFv3: Terminology"
---

# OSPFv3 & Dynamic Routing: Terminology

*IPv6 addressing terms (link-local, ND, solicited-node multicast, and the rest) live in [Week 7's terminology](../../week_07/terminology); this table covers the routing-protocol vocabulary.*

| Term / Acronym | Definition |
|---|---|
| **/127** | The recommended prefix length for router-to-router point-to-point links ([RFC 6164](https://datatracker.ietf.org/doc/html/rfc6164)): exactly two addresses, the IPv6 counterpart of IPv4's /31, and a defense against neighbor-cache exhaustion on infrastructure links |
| **Adjacency** | A fully synchronized OSPF neighbor relationship; two routers are adjacent once they reach the `Full` state and hold identical LSDBs |
| **Administrative Distance** | The trust ranking a RIB uses when multiple sources offer the same prefix; in FRR's defaults, connected routes beat static routes, which beat OSPF, which beats iBGP |
| **BFD** | Bidirectional Forwarding Detection: a dedicated sub-second liveness protocol that routing protocols (IGPs and BGP alike) subscribe to for failure detection far faster than hello timers allow |
| **Convergence** | The time between a topology change and every router forwarding correctly again; a measurable, engineerable number, not an abstraction |
| **Cost** | OSPF's per-interface metric, summed along a path; SPF selects the lowest total. Conventionally derived from interface bandwidth |
| **Dead Interval** | How long an OSPF router waits without hearing hellos before declaring a neighbor down (FRR default: 40s); the detection floor for silent failures |
| **Distance-Vector** | The routing protocol family (RIP is the classic example) where routers exchange summaries of reachability and trust their neighbors' arithmetic, rather than sharing a full map |
| **DR / BDR** | Designated Router / Backup Designated Router: elected per multi-access network segment to keep LSA flooding efficient; visible in `show ipv6 ospf6 neighbor` output |
| **EGP** | Exterior Gateway Protocol: a routing protocol run *between* administrative domains, where policy matters more than shortest path. BGP is the EGP in practice |
| **FIB** | Forwarding Information Base: the table the kernel actually forwards packets with; populated from the RIB's winning routes (`ip -6 route` shows it on Linux) |
| **Hello Interval** | How often an OSPF router multicasts hello packets to `ff02::5` (FRR default: 10s); must match between neighbors or the adjacency will not form |
| **IGP** | Interior Gateway Protocol: a routing protocol run *inside* one administrative domain, optimizing for shortest path. OSPF and IS-IS are the common ones |
| **Link-State** | The routing protocol family where every router floods its local connectivity to all others, so each holds an identical complete map and computes paths independently |
| **LSA** | Link-State Advertisement: one router's flooded description of a piece of its local connectivity; the unit of information a link-state protocol exchanges |
| **LSDB** | Link-State Database: the collected set of all LSAs in an area, identical on every router in that area by design |
| **OSPFv3** | OSPF adapted for IPv6 ([RFC 5340](https://datatracker.ietf.org/doc/html/rfc5340)): per-interface configuration, adjacencies over link-locals, same link-state machinery as OSPFv2 |
| **RIB** | Routing Information Base: the collection of candidate routes from every source (connected, static, each protocol), from which administrative distance picks winners for the FIB |
| **Router ID** | A 32-bit dotted-quad value identifying an OSPF router. On an IPv6-only router it is an opaque name that merely looks like an IPv4 address |
| **SPF** | Shortest Path First: Dijkstra's algorithm, run independently by each router over the shared LSDB, rooted at itself |
