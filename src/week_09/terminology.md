---
title: Terminology
---

# Week 9: Terminology

| Term / Acronym | Definition |
|---|---|
| **Acceptance Policy** | The set of rules (prefix-lists and route-maps, applied inbound) governing which routes a router keeps from a given neighbor; the central design concept of Lab 2 |
| **Bad Peer AS** | The NOTIFICATION reason FRR sends when a peer's OPEN message claims an ASN that doesn't match the configured `remote-as`; the session cannot establish until the mismatch is corrected |
| **Bridge (containerlab `kind: bridge`)** | A containerlab node type that attaches a link to a pre-existing host Linux bridge instead of another container; the mechanism Lab 2 uses to let two independently-deployed topologies share a network segment |
| **DENY-DEFAULT / ONLY-DEFAULT** | Lab 2's own prefix-list names, not FRR keywords: `ONLY-DEFAULT` permits just the default route (one line, implicit deny covers everything else); `DENY-DEFAULT` denies just the default and explicitly re-permits everything else (two lines) |
| **Full Table** | A BGP feed carrying (an approximation of) every globally routed prefix, as opposed to a partial or default-only feed; Lab 2's `isp1` represents one |
| **Graceful Degradation** | A failure mode where losing a preferred, specific route doesn't black-hole traffic, because a less-specific route (typically a default) still covers the same destinations, just less optimally |
| **`le` / `ge`** | Prefix-list modifiers narrowing a match to a range of prefix lengths (`le` = at most this long, `ge` = at least this long); a prefix longer than a `le` value simply fails to match, silently, with no error |
| **Longest-Prefix-Match** | The forwarding rule (Week 3) that picks the most specific matching route when several exist for a destination; the mechanism that makes Lab 2's specific-vs-default design work without any BGP-level tiebreaking |
| **MCLAG** | Multi-Chassis Link Aggregation: a vendor-specific control-plane feature letting two physical switches present as one logical device to a downstream peer. Lab 2's `sw1`-`sw2` peer link represents where this would run; FRR does not implement the control plane, so the link is real but the feature isn't |
| **NOTIFICATION** | The BGP message that ends a session on a fatal disagreement (a bad peer AS, a malformed OPEN); Lab 1 triggers one on purpose |
| **Prefix-List** | An ordered sequence of permit/deny rules matched against a prefix (optionally narrowed by `le`/`ge`); anything matching no rule hits an implicit deny |
| **Route-Map** | A named policy object referencing one or more prefix-lists (via `match`), applied to a BGP neighbor in a specific direction (`in`/`out`) and address family |
| **`(Policy)`** | The marker FRR's `show bgp summary` prints in place of a prefix count when RFC 8212's default-deny is blocking a session with no configured import/export policy |
| **Transit** | Carrying traffic between two other networks, neither of which is you; Lab 1's `rtr-org` becomes one by accident once RFC 8212's default-deny is lifted with no further policy in place |
