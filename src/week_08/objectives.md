---
title: BGP Basics
---

# Week 8: BGP Basics

**Objective:** understand what BGP is, why the Internet routes with it, and how it carries IPv6, then bring up real eBGP sessions between FRR routers yourself. Week 3's routing tables and Week 7's IPv6 addressing are the only background assumed.

By the end of this page you should be able to:

- **Explain what an Autonomous System (AS) is, and why routing between them is its own problem.**

  *Readings: Kentik's [BGP Routing: An In-Depth Tutorial](https://www.kentik.com/kentipedia/bgp-routing/), the opening sections on autonomous systems; Dordal's [An Introduction to Computer Networks, chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html), the chapter introduction.*

<details>
  <summary><strong>What is an Autonomous System (AS)?</strong></summary>

  <p>
    An <strong>Autonomous System (AS)</strong> is a collection of IP networks that are managed
    by a single organization and share a common routing policy.
  </p>

  <p>
    Examples of Autonomous Systems include:
  </p>

  <ul>
    <li>An Internet Service Provider (ISP)</li>
    <li>A cloud provider such as AWS, Azure, or Google Cloud</li>
    <li>A large university</li>
    <li>A large enterprise or government organization</li>
  </ul>

  <p>
    Every AS is assigned a unique <strong>Autonomous System Number (ASN)</strong>, which is
    used to identify it when exchanging routing information with other organizations.
  </p>
</details>

<details>
  <summary><strong>Internal and External Routing Protocols</strong></summary>

  <p>
    Routers need a way to learn how to reach different networks. The protocol they use depends
    on whether they are communicating <strong>inside</strong> their own Autonomous System or
    <strong>between</strong> different Autonomous Systems.
  </p>

  <h4>Interior Gateway Protocols (IGPs)</h4>

  <p>
    <strong>IGPs</strong> are used within a single Autonomous
    System. Since all of the routers belong to the same organization, they work together to
    find the best path through the network.
  </p>

  <p>Common IGPs include:</p>

  <ul>
    <li>OSPF (Open Shortest Path First)</li>
    <li>IS-IS (Intermediate System to Intermediate System)</li>
  </ul>

  <h4>Exterior Gateway Protocols (EGPs)</h4>

  <p>
    <strong>Exterior Gateway Protocols (EGPs)</strong> are used to exchange routing information
    between different Autonomous Systems. On today's Internet, the protocol used for this is
    <strong>BGP (Border Gateway Protocol)</strong>.
  </p>

  <p>
    Unlike IGPs, BGP is not focused on finding the shortest path. Instead, it allows each
    organization to control which routes it advertises, which routes it accepts, and which
    paths it prefers to use.
  </p>

  <p>
    Together, tens of thousands of Autonomous Systems use BGP to form the global Internet.
  </p>
</details>


*Questions to consider:*

  - Your organization and its ISP each run their own interior routing. What routing information needs to cross the boundary between them, and what should not cross it?

---

- **Describe what BGP actually is and how it moves routes.**

  *Readings: [RFC 4271](https://datatracker.ietf.org/doc/html/rfc4271) section 1 and section 3 (Summary of Operation); Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html) section 15.1 on AS-paths.*

<details>
  <summary><strong>A path-vector protocol</strong></summary>

  <p>
    BGP advertises each prefix together with the full list of ASes the advertisement has
    traversed: the <strong>AS_PATH</strong>. Each AS prepends its own number when passing a
    route along, so the path grows hop by hop.
  </p>

  <p>
    A router that sees its own ASN already in a received path rejects the route. That one rule
    is BGP's loop prevention, and the same list doubles as its everyday path-selection
    tiebreaker: shorter is better.
  </p>
</details>

<details>
  <summary><strong>Sessions ride ordinary TCP</strong></summary>

  <p>
    BGP runs over a plain <strong>TCP connection on port 179</strong>, and only between
    neighbors that were explicitly configured on both ends.
  </p>

  <p>
    There is no discovery and no multicast hello. If nobody types <code>neighbor</code>,
    nothing peers. This fits the trust model: an eBGP neighbor is another organization, and
    that relationship is arranged by people before it is configured on routers.
  </p>
</details>


*Questions to consider:*

  - What does running over TCP give BGP for free that a protocol with its own packet format has to build itself?
  - AS_PATH prevents loops by listing every AS traversed. What does that same list conveniently give an operator who wants to choose between two routes to the same prefix?

---

- **Tell eBGP and iBGP apart, and say when each is used.**

  *Readings: Kentik's [tutorial](https://www.kentik.com/kentipedia/bgp-routing/), the eBGP versus iBGP section; Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html) section 15.9 for how BGP gets used interior to a network.*

<details>
  <summary><strong>eBGP: between autonomous systems</strong></summary>

  <p>
    A session between routers in <strong>different</strong> ASes is <strong>external BGP
    (eBGP)</strong>. It usually runs between directly connected routers, and it prepends the
    local ASN as routes cross the AS boundary.
  </p>

  <p>
    An AS boundary is often an organizational boundary (you and your ISP), but it does not
    have to be. Private ASNs let one organization draw AS boundaries <em>inside</em> its own
    network and run eBGP across them, trading an IGP's shortest-path automation for eBGP's
    explicit policy control and simple loop prevention. The production network you will work
    with does exactly this: the edge routers advertise routes to the core switches over eBGP.
  </p>

  <p>
    This week's lab and the production deployment this arc leads to are both eBGP.
  </p>
</details>

<details>
  <summary><strong>iBGP: same AS on both ends</strong></summary>

  <p>
    A session between routers in the <strong>same</strong> AS is <strong>internal BGP
    (iBGP)</strong>. Its classic job: an AS with more than one border router needs the routes
    learned at one edge to reach the other edges with their BGP attributes intact, and
    re-injecting them into the IGP would lose that information.
  </p>

  <p>
    iBGP carries them across the inside instead, without modifying AS_PATH, typically between
    router loopback addresses that an IGP keeps reachable. It is one answer to "the network
    behind the border grew past one router"; internal eBGP between private ASNs, as above, is
    another.
  </p>
</details>


*Questions to consider:*

  - An AS has border routers A and B. A packet enters at A, destined for a prefix that was learned over B's external session. What does A need to know for that packet to make it, and which protocol family (IGP or iBGP) supplies each piece?

---

- **Follow a BGP session from Idle to Established.**

  *Readings: [RFC 4271](https://datatracker.ietf.org/doc/html/rfc4271) section 4 for the four message types; section 8 has the full state machine if you want the formal version, but recognizing the state names is enough for now.*

<details>
  <summary><strong>The session states</strong></summary>

  <p>
    Two configured neighbors walk a visible state machine: <code>Idle</code>,
    <code>Connect</code>/<code>Active</code> (still trying to open the TCP connection),
    <code>OpenSent</code> and <code>OpenConfirm</code> (introductions exchanged, capabilities
    and timers negotiated), and finally <code>Established</code>: the only state in which
    routes flow.
  </p>
</details>

<details>
  <summary><strong>Four message types, two timers</strong></summary>

  <p>
    BGP has exactly four message types: <strong>OPEN</strong> (introduce yourself: ASN, router
    ID, hold time), <strong>UPDATE</strong> (advertise and withdraw routes),
    <strong>KEEPALIVE</strong> (proof of life), and <strong>NOTIFICATION</strong> (a fatal
    error, always followed by closing the session).
  </p>

  <p>
    Liveness rests on two timers: the <strong>keepalive interval</strong> (FRR default 60s) and
    the <strong>hold time</strong> (FRR default 180s, negotiated down to the lower of the two
    sides' OPEN values). Miss keepalives until the hold time expires and the session drops,
    withdrawing every route it carried.
  </p>
</details>

<details>
  <summary><strong>Mini-lab: try the timer arithmetic</strong></summary>

```js
const keepalive = view(Inputs.range([1, 120], {step: 1, value: 60, label: "Keepalive interval (s)"}));
const holdTime = view(Inputs.range([3, 540], {step: 3, value: 180, label: "Hold time (s)"}));
```

```js
const missed = Math.floor(holdTime / keepalive);
const healthy = holdTime >= 3 * keepalive;
display(html`
  <div style="background:var(--theme-background-alt,#f8f8f8);border-left:4px solid ${healthy ? "#1565c0" : "#c62828"};padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    A silently failed peer keeps its routes installed for up to <strong>${holdTime} seconds</strong>:
    the session survives <strong>${missed}</strong> missed keepalive${missed === 1 ? "" : "s"} before the hold timer expires.<br>
    Until then, traffic keeps forwarding toward a dead neighbor.
    ${healthy ? "" : html`<br><strong>Warning:</strong> a hold time under 3x keepalive means one delayed packet can kill a healthy session. Convention keeps hold at 3x keepalive, and both FRR and most vendors default exactly there.`}
  </div>
`);
```

</details>

*Questions to consider:*

  - `show bgp summary` reports a neighbor in state `Active`. The name sounds healthy. What is actually happening, and what two or three misconfigurations would you check first?
  - Why does a NOTIFICATION always terminate the session instead of letting the peers talk past the error?

---

- **Read a BGP table and trace a route into the forwarding table.**

  *Readings: the [FRR BGP documentation](https://docs.frrouting.org/en/latest/bgp.html), the Route Selection section; Dordal [chapter 15](https://intronetworks.cs.luc.edu/current/html/bgp.html) section 15.6 on path attributes.*

<details>
  <summary><strong>The BGP table and the best path</strong></summary>

  <p>
    A router's BGP table holds <strong>every</strong> path it has learned for each prefix, from
    every neighbor. That is deliberate: the alternatives are what policy chooses between, and
    they make failover fast when the best path is withdrawn.
  </p>

  <p>
    For each prefix, BGP marks one path best. With no policy configured, the everyday
    tiebreaker is <strong>shortest AS_PATH</strong>. The full decision list is longer, and next
    week is about bending it on purpose.
  </p>
</details>

<details>
  <summary><strong>From best path to forwarding: RIB and FIB</strong></summary>

  <p>
    The best path then competes in the <strong>RIB</strong> (Routing Information Base), the
    router's collection of candidate routes from every source: connected interfaces, static
    configuration, each routing protocol. Sources are ranked by <strong>administrative
    distance</strong> (in FRR: connected 0, static 1, eBGP 20).
  </p>

  <p>
    The winner is installed into the <strong>FIB</strong> (Forwarding Information Base), the
    table the kernel actually forwards with. On an FRR router you can see one route at all
    three stages: <code>show bgp ipv6 unicast</code> (the BGP table), <code>show ipv6
    route</code> (the RIB), and <code>ip -6 route</code> (the kernel FIB).
  </p>
</details>

<details>
  <summary><strong>Mini-lab: two candidate paths for the same prefix</strong></summary>

Watch the tiebreaker work:

```js
const lenA = view(Inputs.range([1, 8], {step: 1, value: 2, label: "Path via neighbor A: ASes in AS_PATH"}));
const lenB = view(Inputs.range([1, 8], {step: 1, value: 4, label: "Path via neighbor B: ASes in AS_PATH"}));
```

```js
const mkPath = (n, base) => Array.from({length: n}, (_, i) => base + i).join(" ");
const pathA = mkPath(lenA, 64510);
const pathB = mkPath(lenB, 64520);
const verdict = lenA === lenB
  ? "Tie on AS_PATH length: selection falls through to later tiebreakers (oldest path, lowest router ID)."
  : `Neighbor ${lenA < lenB ? "A" : "B"} wins: ${Math.min(lenA, lenB)} ASes beats ${Math.max(lenA, lenB)}.`;
display(html`
  <div style="background:var(--theme-background-alt,#f8f8f8);border-left:4px solid #1565c0;padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    via A:&nbsp;&nbsp;AS_PATH <strong>${pathA}</strong><br>
    via B:&nbsp;&nbsp;AS_PATH <strong>${pathB}</strong><br><br>
    ${verdict}
  </div>
`);
```

</details>

*Questions to consider:*

  - The same prefix is reachable through a static route and an eBGP route. Which forwards the traffic, and what number decided it?
  - BGP keeps the losing paths in its table instead of discarding them. What happens the moment the best path is withdrawn, and how does keeping the losers make that faster?

---

- **Explain how BGP carries IPv6.**

  *Readings: [RFC 2545](https://datatracker.ietf.org/doc/html/rfc2545), four pages, the primary source for IPv6-over-BGP; [RFC 4760](https://datatracker.ietf.org/doc/html/rfc4760) sections 1-3 for the address-family mechanism itself.*

<details>
  <summary><strong>The multiprotocol extensions</strong></summary>

  <p>
    BGP-4 predates wide IPv6 use, and IPv6 arrived not as a new protocol version but as the
    <strong>multiprotocol extensions</strong> (RFC 4760): the UPDATE message gained attributes
    that can carry reachability for any <strong>address family</strong>, and RFC 2545 defines
    the IPv6 rules.
  </p>

  <p>
    A session and the routes it carries are therefore separate dimensions: the TCP connection
    can run over IPv6 while the address families negotiated on it decide what routes flow. In
    FRR, each neighbor must be explicitly activated per family.
  </p>
</details>

<details>
  <summary><strong>Link-local next-hops, again</strong></summary>

  <p>
    An IPv6 route's next-hop field can carry two addresses, a global one and a link-local one,
    and for directly connected peers the link-local is what gets used.
  </p>

  <p>
    That means the routes BGP installs in the kernel have <code>fe80::</code> next-hops: the
    same behavior you built by hand with a static route in Week 7's Lab 1, now performed
    automatically by a protocol.
  </p>
</details>


*Questions to consider:*

  - One TCP session can, in principle, carry both IPv4 and IPv6 route exchange. Many operators still run one session per address family. What failure would couple the two families together on a shared session?
  - Why is a link-local next-hop actually preferable to a global one on a direct router-to-router link? (Week 7 Lab 1's Step 6 question is worth re-reading with BGP eyes.)

---

**Why it matters for the project:** this is the protocol the production Internet2 connection speaks. The coming weeks build this up in ContainerLab exactly before you build it in production: eBGP sessions carrying real IPv6 routes between the organization's edge and the internal switch core. At the end of this you will have provided IPv6 reachability for a production network over IPv6 through the public internet and Internet2.
