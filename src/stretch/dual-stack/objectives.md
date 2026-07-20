---
title: "Dual-Stack: Objectives"
---

# Dual-Stack Operations: Objectives

*Note: this stretch topic covers running IPv4 and IPv6 side by side, which is how nearly every production network (including the one the Week 10 deployment touches) actually operates. Work through [Week 7's IPv6 Basics](../../week_07/basics) and [Lab 1](../../week_07/lab1) first; everything here assumes them.*

By the end of this topic you should be able to:

- **Treat dual stack as two of everything.**  
  Dual stack means both address families running natively on the same infrastructure, and the load-bearing mental model is that they are two complete, independent networks: separate addressing, routing, filtering, and failure modes, with nothing shared and nothing translated. A router can forward IPv4 flawlessly while IPv6 through the same interfaces is completely broken, and no counter on either stack will mention the other's problem. One Linux wrinkle to recognize: a service bound to the IPv6 wildcard accepts IPv4 clients too, and logs them as v4-mapped addresses (`::ffff:10.7.1.10`). [Lab 1](./lab1) puts one in front of you.

  *Readings: [RFC 4213](https://datatracker.ietf.org/doc/html/rfc4213) section 2, where dual stack is formally defined (the tunneling half of the document is historical context).*

  *Questions to consider:*
  - A firewall change request says "open port 8443 to the app servers." In a dual-stack network, what's the follow-up question, and what happens silently if nobody asks it?
  - If the two stacks share no state, what does "the network is up" mean? What would monitoring have to check?

- **Predict which family a connection uses, and what happens when the preferred one is broken.**  
  When a name resolves to both families, default rules order the candidates (IPv6 generally first when usable) and pick a scope-matched source address for whichever destination is tried. The dangerous failure is broken-but-configured IPv6, where a naive client hangs on the preferred family before ever trying the IPv4 that works; Happy Eyeballs fixes it by racing the families with a small head start. [Lab 1](./lab1)'s main event has you break IPv6 on purpose and measure the damage yourself.

  *Readings: [RFC 6724](https://datatracker.ietf.org/doc/html/rfc6724) sections 2 and 5 for the selection rules; [RFC 8305](https://datatracker.ietf.org/doc/html/rfc8305), short and unusually readable, for the Happy Eyeballs race.*

  *Questions to consider:*
  - Why is completely absent IPv6 so much cheaper to fall back from than black-holed IPv6? What does each case return to the client, and when?
  - If Happy Eyeballs hides IPv6 breakage from users, whose job does it become to notice it, and with what tools? (Week 5's flow telemetry is a fair answer.)

**Why it matters for the project:** the Week 10 deployment adds IPv6 BGP alongside working IPv4 on production routers. That is exactly the two-independent-networks situation above: the new configuration's blast radius on IPv4, and how anyone would even notice an IPv6-only fault, are questions this topic gives you the tools to answer.
