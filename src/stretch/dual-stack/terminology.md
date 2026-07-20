---
title: "Dual-Stack: Terminology"
---

# Dual-Stack Operations: Terminology

*IPv6 addressing terms (link-local, scopes, ND, and the rest) live in [Week 7's terminology](../../week_07/terminology); this table covers the dual-stack vocabulary.*

| Term / Acronym | Definition |
|---|---|
| **Default Address Selection** | The [RFC 6724](https://datatracker.ietf.org/doc/html/rfc6724) rules deciding which candidate destination a client tries first (IPv6 generally preferred when usable) and which of its own addresses it sources from (matching scope: global to global, not ULA to global) |
| **Dual Stack** | Running IPv4 and IPv6 natively side by side ([RFC 4213](https://datatracker.ietf.org/doc/html/rfc4213)): two complete, independent networks on the same wires, with separate addressing, routing, filtering, and failure modes |
| **Happy Eyeballs** | The [RFC 8305](https://datatracker.ietf.org/doc/html/rfc8305) connection strategy: instead of waiting for the preferred address family to time out, race both with a small head start (typically 250ms) and use whichever connects first |
| **V4-Mapped Address** | An IPv4 client as seen by a dual-stack IPv6 socket: `::ffff:` followed by the dotted-quad (e.g. `::ffff:10.7.1.10`). A logging/API representation on the host, not an address that appears in packets on the wire |
