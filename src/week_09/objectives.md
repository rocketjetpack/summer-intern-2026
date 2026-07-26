---
title: BGP Deep Dive II Objectives
---

# Week 9: Objectives

**Objective:** move from BGP concepts to BGP built by hand, at both toy and production scale, and learn that accepting a route across a boundary is always a decision, never a default. Week 8's [Basics page](../week_08/objectives) covers AS_PATH, the session FSM, and MP-BGP; have that material solid before starting.

By the end of this week you should be able to:

- **Bring a BGP session up from nothing, and know that `Established` alone proves nothing about routes.**

  *Readings: [RFC 8212](https://datatracker.ietf.org/doc/html/rfc8212); [Lab 1](./lab1) is this objective performed live.*

<details>
  <summary><strong>Typing BGP instead of reading about it</strong></summary>

  <p>
    Every session in [Lab 1](./lab1) is typed into a live router, not deployed from a file: <code>router bgp</code>, <code>neighbor ... remote-as</code>, <code>address-family</code>, <code>activate</code>. Watching a neighbor sit in <code>Active</code> while the far side is unconfigured, then watching it walk to <code>Established</code> the moment both ends agree, is a different kind of understanding than reading the FSM's state names on a page.
  </p>
</details>

<details>
  <summary><strong>Established is the beginning of the story, not the end</strong></summary>

  <p>
    RFC 8212 means a freshly established eBGP session accepts and advertises nothing until policy says otherwise. Lab 1 collides with this on purpose: two routers, a live session, and an empty BGP table, until <code>no bgp ebgp-requires-policy</code> (a lab-only shortcut, not a production practice) opens it up. A wrong <code>remote-as</code> produces a different failure entirely: a <strong>NOTIFICATION</strong>, <code>bad peer AS</code>, and a session that will never establish until the claim is corrected.
  </p>
</details>

  *Questions to consider:*

  - What's the practical difference, for someone troubleshooting at 2am, between a session stuck in `Active` and one repeatedly failing with a NOTIFICATION?

---

- **Recognize an accidental transit provider, and explain why it happens by default.**

  *Readings: Dordal's [BGP chapter](https://intronetworks.cs.luc.edu/current/html/bgp.html), section 15.3 (Transit Traffic), revisited from [Week 8](../week_08/resources); [Lab 1](./lab1) Step 7.*

<details>
  <summary><strong>BGP tells everyone everything, unless told not to</strong></summary>

  <p>
    A BGP speaker's default nature is to advertise every best path it holds to every established peer. Give one router two upstream sessions with no outbound policy, and it will pass each upstream's routes to the other, becoming free transit between two networks that never agreed to that arrangement. Lab 1's `rtr-org` does exactly this, and the AS_PATH it produces (<code>64500 64502</code>, read right to left) is the evidence.
  </p>
</details>

  *Questions to consider:*

  - The transit accident cost nothing in Lab 1's synthetic topology. What would it actually cost a real dual-homed network, in dollars or in risk, and to whom?

---

- **Read and write `prefix-list` and `route-map` policy, and know exactly what each piece is doing.**

  *Readings: FRR documentation, [Filtering](https://docs.frrouting.org/en/latest/filter.html) (prefix-lists) and [Route Map](https://docs.frrouting.org/en/latest/routemap.html); [Lab 2](./lab2) Steps 1 and 5.*

<details>
  <summary><strong>Four pieces, one pattern</strong></summary>

  <p>
    A <code>prefix-list</code> is a sequence of permit/deny rules matched against a prefix and, optionally, a range of acceptable lengths (<code>le</code>/<code>ge</code>); anything matching no rule hits an implicit deny. A <code>route-map</code> wraps one or more prefix-lists into a named policy a BGP neighbor statement can reference. Applied <code>in</code> under an <code>address-family</code>, it governs exactly one neighbor's exactly one direction, for exactly one family. Nothing here is exotic; it's the same four pieces, reused, every time.
  </p>
</details>

<details>
  <summary><strong>Asymmetric intent, asymmetric syntax</strong></summary>

  <p>
    "Only the default" needs a single <code>permit</code> line, because a prefix-list with any entry denies everything unmatched for free. "Everything except the default" needs two lines: deny the one exception, then explicitly re-permit the rest with a wide-open <code>le</code>. The line count isn't arbitrary; it's the direct cost of which side of the split is the exception.
  </p>
</details>

  *Questions to consider:*

  - Without writing it out, could you predict how many prefix-list lines "accept only prefixes shorter than /20" would need? What about "accept everything except one specific /24"?

---

- **Design a specific-versus-default acceptance split, and explain why longest-prefix-match makes it work without any BGP-level tiebreaking.**

  *Readings: Week 3's [Path Explorer](../week_03/path-explorer) and its longest-prefix-match reading, if you need the refresher; [Lab 2](./lab2)'s scenario section and Steps 3-5.*

<details>
  <summary><strong>Two sources, two roles, one design</strong></summary>

  <p>
    [Lab 2](./lab2) mirrors a real production pattern: a full-table public Internet feed that should contribute only a catch-all default, and a smaller, preferred feed (Internet2) whose specific routes should always win for the destinations it actually reaches. Because one source only ever offers a /0 and the other only ever offers longer prefixes, the kernel's own longest-prefix-match resolves the intended preference automatically, once each source is limited to the role it's supposed to play.
  </p>
</details>

<details>
  <summary><strong>Why the switches enforce it, not just trust it</strong></summary>

  <p>
    The upstream routers in Lab 2 advertise everything, unfiltered, to both switches. The acceptance policy exists entirely on the receiving end, on purpose: a network defends its own design rather than trusting an upstream to only ever send what it's supposed to, the same defense-in-depth instinct RFC 8212 is built on.
  </p>
</details>

  *Questions to consider:*

  - If the roles were reversed by mistake (the full table filtered to default-only came from the *smaller* feed instead), what would actually break, given that both sources are otherwise honest?

---

- **Take a working policy in one address family and rebuild it, correctly, in another.**

  *Readings: [Lab 2](./lab2) Steps 4-6.*

<details>
  <summary><strong>Reading a pattern is not the same as having built it</strong></summary>

  <p>
    [Lab 2](./lab2) hands you a complete, working IPv4 acceptance policy and has you deploy it as a worked example before asking you to build the IPv6 equivalent yourself: same design intent, same shape of prefix-list and route-map, translated one address family over. Every neighbor statement, prefix-list, and route-map for IPv6 is typed by you, checked against RFC 8212's `(Policy)` marker exactly the way Lab 1 first showed it.
  </p>
</details>

  *Questions to consider:*

  - Mechanically translating a policy (`ip` to `ipv6`, `/32` to `/128`) is fast but risks a specific kind of mistake a value that's syntactically valid in the new family but means something different. Where in Lab 2's IPv6 build did you have to stop translating and actually think?

---

- **Describe what a full-mesh dual-router, dual-switch design buys you, and where its honest limits are.**

  *Readings: [Lab 2](./lab2)'s scenario section and topology diagram.*

<details>
  <summary><strong>Redundancy without hairpinning</strong></summary>

  <p>
    Every router in Lab 2 connects to every switch. The payoff isn't classic BGP multipath (there's rarely a real tie between the two upstreams' offerings); it's that whichever switch traffic lands on, it has a direct, local session to both egress roles, without ever needing to transit its partner switch first.
  </p>
</details>

<details>
  <summary><strong>MCLAG named honestly, not implemented</strong></summary>

  <p>
    The two switches in Lab 2 share a direct peer link representing where a real MCLAG (multi-chassis link aggregation) control plane would run. FRR doesn't implement one; the link is real and addressed, but nothing on it behaves like a single logical switch. Naming a limitation is different from pretending it isn't there.
  </p>
</details>

  *Questions to consider:*

  - Lab 2 has you fail one upstream session and watch its routes fall back to the other's default. Sketch a failure this topology *doesn't* gracefully handle, and say what would need to change to cover it.

---

**Why it matters for the project:** [Lab 2](./lab2)'s scenario, two upstream feeds with an asymmetric acceptance policy behind a redundant switch pair, is not a simplification of the Week 10 production deployment. It is the design, at the scale a lab host can run. What you build this week, in FRR, is what gets rebuilt in Week 10 on the real Juniper edge.
