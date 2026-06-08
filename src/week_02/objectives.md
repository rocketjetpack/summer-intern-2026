---
title: Objectives
---

# Week 2 — Objectives

**Objective:** understand how packet-switched networks function — build the layered mental model (TCP/IP and OSI) and trace the "life of a packet," folding your existing ARP/DNS work into the bigger picture.

By the end of the week you should be able to:

- **Explain why networks move data in packets at all.** Contrast packet switching (data chopped into independently-routed chunks that share a link) with circuit switching (a dedicated path reserved for the whole conversation, like a phone call) — and why the packet-switched model is what lets a single link carry traffic from many unrelated conversations at once.
- **Describe encapsulation.** As data moves down the stack, each layer wraps the layer above's output in its own header (think nested envelopes — each layer only reads its own envelope and passes the rest along unopened). On the receiving end, the same thing happens in reverse, one header peeled off per layer.
- **Explain why networks are layered in the first place.** It's the same separation-of-concerns idea you've already met in OS or systems courses: a layer only needs to know the *interface* the layer below offers, not how that layer is implemented. That's what lets Wi-Fi, Ethernet, and cellular all carry the same IP traffic underneath.
- **Trace the life of a packet end to end**, in plain terms: an application hands data to the OS, which breaks it into segments, addresses and frames it, and puts it on the wire — and the receiving machine reverses every one of those steps to hand the original data back to its application.
- **Place your existing ARP and DNS work inside this picture.** Both are examples of "how do I find the next hop?" — DNS resolves a name to an address at the application layer, ARP resolves an address to a physical link-layer destination. Seeing them as instances of a general pattern (not two unrelated tools) is the goal.

None of this requires knowing *how* addressing, switching, or routing work internally yet — that's next week. This week is about the shape of the system: why it's chopped into packets, why it's layered, and what happens to one packet on its trip from sender to receiver.

**Why it matters for the project:** you can't visualize a network's health until you know what's flowing through it and at which layer a problem shows up. Every later week — addressing, transport, telemetry, optics — builds on this layered model; getting it solid now is what lets you later ask "is this an L2 problem or an L4 problem?" instead of guessing.
