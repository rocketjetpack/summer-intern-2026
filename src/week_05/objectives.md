---
title: Objectives
---

# Week 5: Objectives

*Note: This week introduces a fourth vantage point on the same network. Week 2 looked at individual packets, Week 3 looked at per-hop forwarding tables, and Week 4 looked at TCP-internal state (`cwnd`, retransmits) versus interface-level SNMP counters. This week's vantage point is the **flow**: who talked to whom, and how much.*

By the end of the week you should be able to:

- **Define a flow and explain why it's a different unit of observation than a packet or an interface counter.**
  A flow is everything a telemetry system groups together as "one conversation": typically with:
  - 5-tuple (source IP, destination IP, source port, destination port, protocol)
  - the interface it entered/exited on 
  - byte/packet count
  - start/end time. 
  
  A flow record answers "who talked to whom, how much, for how long" — a question neither a single packet capture nor an interface counter can answer on its own.

- **Explain sFlow: sampling instead of accounting.**
  sFlow takes two independent samples on a switch/router:
  - **Packet sampling:** a pseudorandom 1-in-*N* packet is selected from the forwarding path and its header (plus a small payload slice) is shipped off unprocessed.
  - **Counter sampling:** interface counters are pushed periodically, much like SNMP polling but initiated by the device rather than pulled by a collector.

  Critically, the device does **no aggregation**, it just timestamps and forwards raw samples by UDP. All of the statistical extrapolation (how many total packets/bytes did this represent?) happens on the collector. This is why sFlow is cheap enough to run in hardware ASICs at very high line rates: the device-side cost is constant regardless of how many distinct flows exist.

  *Questions to consider:*
  - If a switch is forwarding 1,000,000 packets/sec and sampling at 1-in-1000, how many samples/sec does it actually need to export? How does that change if traffic triples?
  - What happens to sFlow's accuracy for flows of a variety of sizes, from very small flows to elephant flows?

- **Explain NetFlow/IPFIX: accounting instead of sampling.**
  NetFlow (and its standardized successor, IPFIX, [RFC 7011](https://datatracker.ietf.org/doc/html/rfc7011)) takes the opposite approach: the device maintains a **flow cache**. This is a table keyed by the flow's identifying fields, accumulating packet/byte counts as matching traffic arrives. A flow record is exported when the flow naturally ends (TCP FIN/RST), or when it hits an **active timeout** (exported periodically even though it's still running) or an **inactive timeout** (no traffic seen for some period, so the entry is considered closed). Unless deliberately configured to sample, every packet is accounted for.

  This exactness isn't free: the flow cache consumes device memory and CPU proportional to the number of *concurrent, distinct* flows, not the packet rate. A device with thousands of short-lived flows works much harder than one carrying the same byte volume across a handful of long-lived ones.

  *Questions to consider:*
  - Two devices carry identical total traffic, but one sees 100 long-lived flows and the other sees 100,000 short-lived ones. Which one's flow cache works harder, and why?
  - A flow record only appears once the flow ends or times out. What does this mean for how quickly NetFlow/IPFIX can tell you about an attack or failure *in progress*?

- **Reason about sampling error.**
  sFlow's packet sampling is a random process: each sample is independent and selected with probability 1/*N*. Given the number of samples actually observed, you can estimate the true packet/byte count and put a confidence bound on that estimate using ordinary sampling statistics. Lower sampling rates (smaller *N*, e.g. 1-in-10) cost more device/collector overhead but tighten that bound; higher rates (larger *N*, e.g. 1-in-10000) are nearly free but the estimate gets noisier, especially for low-volume flows. This is the central exercise of Lab 1 and the [Sampling Estimator](./sampling-estimator) code lab where you will predict the error bound before you measure, then check your prediction against real samples.

- **Compare sFlow and NetFlow/IPFIX as a deliberate trade-off, not a "better/worse" choice.**

  | | sFlow | NetFlow / IPFIX |
  |---|---|---|
  | **Accuracy** | Statistical estimate, has known error | Exact (unless deliberately sampled) |
  | **Device cost** | Constant, independent of flow count | Proportional to concurrent flow count |
  | **Timeliness** | Near-real-time (samples stream continuously) | Delayed until flow end/timeout |
  | **Best for** | High line-rate ASICs, broad traffic visibility | Exact accounting, billing, anomaly/DDoS detection |

  Lab 1 and Lab 2 run identical traffic through both mechanisms so you can observe this trade-off directly rather than just read about it.

- **Identify practical uses for flow telemetry.**
  Top-talkers analysis (which hosts/conversations consume the most bandwidth), anomaly and DDoS detection (a sudden explosion in distinct flows or a single flow's byte count is a classic signal), and traffic-matrix data for capacity planning. These considerations are the kind of fabric-design questions introduced in [Week 4](../week_04/objectives).

---

## Vantage Points, Continued

Week 4 made the point that TCP-internal state (`ss -tip`) and SNMP interface counters answer different questions and neither is "more correct." Flow telemetry is a third axis on that same idea: it doesn't see TCP's congestion window, and it doesn't average over a multi-minute polling interval. Flow level data tells you *who* is using the link, which neither previously introduced vantage point can.

sFlow and SNMP also share a structural weakness, just along different axes. SNMP polling averages **over time** (e.g: a five-minute mean can hide a sub-second burst entirely). sFlow samples have a similar weakness: at 1-in-1000, a real but small flow may simply never get picked by the sampler. Both are forms of the same underlying trade off: you cannot observe everything, so you trade completeness for cost, and which option you choose to trade away determines what kind of event you can miss.

*Forward reference: flow telemetry (especially NetFlow/IPFIX's exact, per-flow counts) is a standard input to the anomaly and DDoS detection techniques planned for Week 10 (Network Security Fundamentals).*
