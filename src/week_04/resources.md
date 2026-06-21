---
title: Resources
---

# Week 4 — Resources

Readings are grouped by topic. Read the Required entries before starting Lab 1 or covering the corresponding topic in the objectives; Recommended entries deepen understanding but are not prerequisites.

---

## Before Lab 1: Loss × Latency Amplification

### Required

- **Van Jacobson & Michael Karels (1988) — [Congestion Avoidance and Control](https://ee.lbl.gov/papers/congavoid.pdf)**  
  The paper that saved the early internet. In 1986–88 the internet suffered repeated *congestion collapses* which saw throughput drop up to 1000× as packets failed to be delivered and senders retransmitted into an already-saturated network.

### Recommended

- **David D. Clark (1988) — [The Design Philosophy of the DARPA Internet Protocols](https://dl.acm.org/doi/pdf/10.1145/52324.52336)**  
  Clark's retrospective on why the internet's architecture is the way it is. Read alongside Jacobson: Clark explains *why* reliability was pushed to the endpoints (the end-to-end argument), which is the philosophical justification for TCP doing its own congestion control rather than relying on the network. Short, readable, and relevant to arguments still happening today.

- **Neal Cardwell et al. (2016) — [BBR: Congestion-Based Congestion Control](https://spawn-queue.acm.org/doi/pdf/10.1145/3012426.3022184)**  
  BBR abandons loss as the congestion signal and models the bottleneck bandwidth and propagation RTT directly. The motivation section is particularly good: it names the *failure modes* of CUBIC on high-BDP paths (bufferbloat, shallow buffers causing false loss signals) and grounds the design choice. Google deployed BBR across YouTube in 2016.

- **[Computer Networks: A Systems Approach — Chapter 5: End-to-End Protocols](https://book.systemsapproach.org/e2e.html)**  
  The textbook treatment of TCP flow control and congestion control. Sections 5.2 (TCP) and 5.4 (congestion control) cover the receiver window and `cwnd` together, which clarifies why there are two separate windows in the TCP send path.

---

## Incast Collapse

### Recommended

- **Alizadeh et al. (2010) — [Data Center TCP (DCTCP)](https://people.csail.mit.edu/alizadeh/papers/dctcp-sigcomm10.pdf)**  
  The paper that named and quantified the incast problem for data-centre storage workloads. 

- **Phanishayee et al. (2008) — [Measurement and Analysis of TCP Throughput Collapse in Cluster-based Storage Systems](https://www.usenix.org/legacy/event/fast08/tech/full_papers/phanishayee/phanishayee.pdf)**  
  The empirical paper that first named incast as a structural problem in distributed storage. Not a configuration failure, not a tuning issue, but an inherent consequence of traffic patterns and TCP's congestion response.

- **Appenzeller, Keslassy & McKeown (2004) — [Sizing Router Buffers](https://dl.acm.org/doi/epdf/10.1145/1030194.1015499)**  
  Argues that the conventional wisdom of sizing router buffers to the BDP is wrong when many flows share a link: the correct size is BDP/√N, where N is the number of flows. Data-centre switches use shallow buffers for exactly this reason — but shallow buffers make incast worse, not better, because less buffering means drops happen sooner.

### Optional
- **[ECN (Explicit Congestion Notification) — RFC 3168](https://www.rfc-editor.org/rfc/rfc3168)**  
  Skim Sections 1 (Introduction) and 5 (ECN-Capable Transport). ECN allows a router to set a "Congestion Experienced" bit in the IP header *before* the buffer fills and drops occur, giving endpoints a chance to back off without loss. Don't try to understand ECN with depth, just be aware that it exists and comprehend why it is present.

---

## Spine-Leaf Fabrics and ECMP

### Required

- **Al-Fares, Loukissas & Vahdat (2008) — [A Scalable, Commodity Data Center Network Architecture](https://cseweb.ucsd.edu/~vahdat/papers/sigcomm08.pdf)**  
  The paper that introduced the fat-tree topology to data-centre networking. Section 2 is the key section, but at only 12 pages it's not a long paper.

### Recommended

- **RFC 2992 — [Analysis of an Equal-Cost Multi-Path Algorithm](https://www.rfc-editor.org/rfc/rfc2992)**  
  Short (10 pages), readable, and precise. Defines per-flow hash-based ECMP, distinguishes it from per-packet ECMP.

- **[Clos Networks and Fat-Tree Topologies — Wikipedia](https://en.wikipedia.org/wiki/Clos_network)**  
  The foundation for non-blocking fabric design.

- **[Priority Flow Control — IEEE 802.1Qbb](https://en.wikipedia.org/wiki/IEEE_802.1Qbb)**  
  PFC is the Ethernet mechanism that makes a fabric lossless for RoCE. A PFC PAUSE frame tells an upstream sender to stop transmitting on a specific traffic class before the buffer overflows. *This is a connection to later topics of InfiniBand and RDMA, and not really pertinent this week. You will also see "flow control" referenced in many switch configurations this summer.*

---

## Querying LibreNMS (Lab 2)

### Recommended

- **[LibreNMS API Documentation — Devices](https://docs.librenms.org/API/Devices/)** and **[Ports](https://docs.librenms.org/API/Ports/)**  
  The two endpoints Lab 2 uses. Pay attention to the `columns` parameter (limits the response to fields you need) and the `_rate`/`_delta` suffixes on counter fields.

- **RFC 2863 — [The Interfaces Group MIB](https://www.rfc-editor.org/rfc/rfc2863)**  
  Defines `ifTable`, the standard SNMP counters (`ifSpeed`, `ifInOctets`/`ifOutOctets`, and related error/discard counters) that LibreNMS — and effectively every SNMP-based monitoring platform — is built on top of. You don't need to read it cover to cover; skim for the counter definitions Lab 2 reads.

- **[LibreNMS Documentation — 1 Minute Polling](https://docs.librenms.org/Support/1-Minute-Polling/)**  
  LibreNMS's default poller frequency is 5 minutes; this page covers the (more demanding) option to poll every 1 minute instead. Worth a skim before drawing conclusions from Lab 2's utilization step about what any fixed polling interval can and can't catch.

