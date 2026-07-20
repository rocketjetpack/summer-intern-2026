---
title: "OSPFv3: Objectives"
---

# OSPFv3 & Dynamic Routing: Objectives

*Note: this stretch topic is your first hands-on dynamic routing protocol. It isn't on the week-by-week schedule, but it pairs naturally with the weeks 8-10 BGP arc: OSPFv3 is an IGP, BGP is the EGP, and the two halves of that split are easiest to understand together. Before starting, work through Week 7's [IPv6 Basics](../../week_07/basics) and [Lab 1](../../week_07/lab1); link-local addressing in particular is assumed everywhere here.*

By the end of this topic you should be able to:

- **Explain what a dynamic routing protocol is, and the IGP/EGP split that organizes all of them.**
  Week 3's static routes have two failure modes that compound with scale: every topology change means editing every affected router by hand, and no static route notices when its next-hop dies. A **dynamic routing protocol** fixes both: routers continuously describe reachability to each other, each router computes best paths from what it hears, and when something changes they recompute. The time between a failure and restored forwarding is **convergence**, and it is a number you can measure and engineer, which [Lab 1](./lab1) does directly.

  Routing protocols divide into two families, and the split is the single most useful piece of taxonomy for the whole back half of the program:
  - **IGPs** (Interior Gateway Protocols: OSPF, IS-IS) run *inside* one administrative domain, where everyone trusts everyone and the goal is simply the shortest, fastest path.
  - **EGPs** (Exterior Gateway Protocols: BGP, effectively the only one) run *between* administrative domains, where the parties are different organizations with different interests, and the goal is policy: what you're willing to carry, what you advertise, and whom you prefer.

  This topic teaches an IGP. The program's weeks 8 through 10 teach the EGP.

  *Questions to consider:*
  - Your organization and an ISP interconnect. Why would neither side want to just merge into one shared OSPF domain, even though it would technically work?
  - What does "administrative domain" mean concretely for the production network the Week 10 deployment touches?

- **Explain the link-state idea: same map, independent math.**
  OSPF is a **link-state** protocol. Each router floods small descriptions of its own local connectivity (**LSAs**, link-state advertisements) to every other router in the area. Collected together, these form the **link-state database (LSDB)**, and the defining property is that *every router's LSDB is identical*: everyone holds the same complete map. Each router then independently runs Dijkstra's shortest-path-first (**SPF**) algorithm over that map, rooted at itself, to compute its own routing table.

  The older alternative, distance-vector (RIP is the classic example), has routers exchange only summaries ("I can reach X at cost 3") and trust their neighbors' arithmetic. Link-state's same-map property is what makes it converge fast and resist loops: disagreements can only exist during the brief window when a new LSA hasn't finished flooding.

  Path selection uses **cost**, a per-interface value summed along each path; lowest total wins. Cost conventionally derives from interface bandwidth, which connects directly back to Week 6: the link speeds and optics studied there are what an IGP's metrics are ultimately describing. When two paths tie, both get installed, and that is exactly the ECMP behavior Week 4 covered, now seen from the control plane's side.

  *Questions to consider:*
  - "Every router has an identical LSDB" is a checkable claim, not a slogan. How would you verify it on three real routers? (Lab 1 has you do it.)
  - If a router briefly has a stale LSDB during flooding, what's the worst thing that can happen to a packet in transit, and why does it self-correct?

- **Describe the OSPFv3 adjacency lifecycle and what "Full" actually means.**
  OSPF routers discover each other by multicasting **hello** packets (to `ff02::5`, the all-OSPF-routers group). Two neighbors then walk a visible state machine: `Down`, `Init`, `2-Way`, `ExStart`, `Exchange`, `Loading`, and finally `Full`, which means precisely that the two routers have synchronized their LSDBs. On multi-access networks the routers also elect a Designated Router (DR) and backup (BDR) to keep flooding efficient; you'll see those roles in Lab 1's neighbor output.

  OSPFv3 ([RFC 5340](https://datatracker.ietf.org/doc/html/rfc5340)) is OSPF adapted for IPv6, and it leans on Week 7's material directly: adjacencies form over **link-local** addresses (no global addressing required for the protocol itself), configuration attaches to interfaces rather than to network statements, and the **router ID** remains a 32-bit dotted-quad value. On an IPv6-only router that ID is just an opaque name that happens to look like an IPv4 address; it identifies, it does not route.

  Failure detection has two modes, and the difference drives Lab 1's finale. When a link loses carrier, the adjacency drops immediately and reconvergence is fast. But a *silent* failure (a switch in the middle dies, an optic degrades one way) produces no carrier loss; the neighbor is only declared dead after the **dead interval** passes with no hellos heard. Try the arithmetic:

  ```js
  const helloInt = view(Inputs.range([1, 30], {step: 1, value: 10, label: "Hello interval (s)"}));
  const deadInt = view(Inputs.range([2, 120], {step: 1, value: 40, label: "Dead interval (s)"}));
  ```

  ```js
  const missedHellos = Math.floor(deadInt / helloInt);
  const healthy = deadInt > helloInt;
  display(html`
    <div style="background:#f8f8f8;border-left:4px solid ${healthy ? "#1565c0" : "#c62828"};padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
      A silent failure goes undetected for up to <strong>${deadInt} seconds</strong>:
      the neighbor must miss <strong>${missedHellos}</strong> consecutive hellos before being declared down.<br>
      Every packet routed toward the dead neighbor during that window is lost.
      ${healthy ? "" : html`<br><strong>Warning:</strong> a dead interval at or below the hello interval means one late hello kills a healthy adjacency. Real configs keep dead at 3-4x hello.`}
    </div>
  `);
  ```

  FRR's defaults are hello 10s, dead 40s: a silent failure can black-hole traffic for most of a minute. Lab 1 has you measure that window and then shrink it. Production networks running fast timers eventually hit the floor of what hello packets can do and reach for **BFD** (Bidirectional Forwarding Detection), a dedicated sub-second liveness protocol that IGPs and BGP both subscribe to; it appears on the Juniper gear in Week 10.

  *Questions to consider:*
  - Why is the dead interval a multiple of the hello interval rather than equal to it? What failure mode does the slack absorb?
  - Two neighbors are configured with different hello intervals. OSPF refuses to form the adjacency at all rather than trying to cope. Why is refusing safer than coping?

- **Trace a route from protocol to RIB to FIB.**
  A route learned by OSPF doesn't teleport into the kernel. The protocol daemon hands it to the **RIB** (Routing Information Base), the router's collection of candidate routes from every source: connected interfaces, static configuration, each routing protocol. When multiple sources offer the same prefix, the RIB picks by **administrative distance**, a per-source trust ranking (connected beats static beats OSPF beats BGP, in FRR's defaults). Only the winner gets installed into the **FIB** (Forwarding Information Base), the table the kernel actually forwards packets with.

  In Lab 1 you'll see the same route in both places: `show ipv6 route` inside FRR's `vtysh` shows the RIB with its protocol markings, and `ip -6 route` in the container shows what zebra installed into the kernel FIB. One detail to watch for: the OSPF-learned routes' next-hops are **link-local addresses**. Dynamic routing in IPv6 genuinely runs on the fe80 space Week 7 started with.

  This vocabulary is permanent. Weeks 8 through 10 discuss BGP almost entirely in terms of what enters the RIB, what wins, and what reaches the FIB.

  *Questions to consider:*
  - A static route and an OSPF-learned route exist for the same prefix. Which wins by default, and when might an operator deliberately exploit that during maintenance?
  - Why maintain a RIB/FIB split at all, instead of letting each protocol write directly into the kernel?

---

## Putting It Together

IPv6's link-local layer gives any two connected routers a working channel before any global addressing exists, and OSPFv3 is built directly on top of that fact: adjacencies form over link-locals, and the routes it computes even use link-locals as next-hops. Meanwhile the map OSPF distributes, and the costs SPF minimizes, describe exactly the physical links whose speeds and optics Week 6 measured, and the equal-cost ties it installs are Week 4's ECMP seen from above. Static routing answered "where do packets go" with a human's memory of the network. A link-state IGP answers it with a live, self-correcting map.

## The BGP Bridge

BGP is the other half of the IGP/EGP split introduced above, and it reuses this entire mental toolkit: neighbor relationships that walk a state machine to an established session, reachability exchanged as advertisements, candidate routes competing in the RIB, winners installed to the FIB. What changes is the goal: OSPF asks "what's shortest," BGP asks "what's allowed, and what do we prefer." Two details come back almost immediately in the BGP weeks: internal BGP sessions ride between the /128 loopbacks whose reachability an IGP maintains, and the FRR containers from Lab 1 carry a `bgpd=no` line in their daemons file that the BGP labs flip to `yes`.
