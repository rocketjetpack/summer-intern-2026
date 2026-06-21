---
title: Objectives
---

# Week 4: Objectives

*Note: This is a largely conceptual week that takes what you have learned so far and builds it into design principles and a high level, architectural view of networks.*

*Note 2: There are a **lot** of acronyms this week. The [terminology](./terminology) page should define or contextualize most or all of them.*

This week builds a quantitative understanding of TCP congestion mechanics, starting with a single flow under controlled impairment, scaling to the synchronised collapse of many flows, and finishing with the fabric architecture decisions that determine whether a bottleneck exists at all.

By the end of the week you should be able to:

- **Explain the TCP connection lifecycle and congestion control.**  
  Congestion control exists to prevent the network from collapsing under load. Van Jacobson's 1988 paper describes a real, observed internet crisis where throughput dropped 100x because senders had no reliable way to infer network capacity from loss signals.

  TCP congestion control works by maintaining a *congestion window* (`cwnd`), which limits how many bytes a sender may have in flight without receiving an acknowledgement. In the goal of preventing loss induced by congestion, various TCP congestion controls generally aim to:
  - **Start slow:** begin data transmission conservatively, doubling the `cwnd` each round-trip until the first loss signal appears.
  - **AIMD (Additive Increase, Multiplicative Decrease):** increase `cwnd` by one MSS per RTT while the path is clear and no loss signals exist; halve it on a loss event.  
  - **Fast retransmit / fast recovery:** three duplicate ACKs signal a single lost segment; the sender retransmits it immediately and halves `cwnd` without waiting for a full timeout.

  *Questions to consider:*  
  - Why does AIMD use additive increase but multiplicative decrease, rather than being symmetric in both directions?  
  - If every sender on a congested link follows the same AIMD rules, what happens to their `cwnd` values over time (do they converge or diverge)?  
  - TCP uses packet loss as its primary congestion signal, but this loss can also be caused by bit errors on a wireless link rather than a full buffer. What does AIMD do in that case, and is it the right response?

- **Explain the Bandwidth-Delay Product (BDP) and why it governs TCP throughput.**  
  `BDP = bandwidth x RTT` is the pipe volume: the number of bytes in flight at any moment when a connection runs at full speed. A sender cannot saturate the link unless `cwnd` reaches the BDP. Any event that collapses `cwnd` (a loss, a timeout, a retransmit) costs proportionally more time to recover as RTT increases. A network with high latency hurts TCP throughput even on a perfectly reliable link with zero packet loss.

- **Apply the Mathis formula to predict TCP throughput degradation.**  
  The Mathis formula quantifies what loss and latency do to a single TCP flow:

  ```js
  tex.block`\text{throughput} \approx \frac{\text{MSS}}{\text{RTT}} \cdot \frac{C}{\sqrt{p}}`
  ```

  where:  
  - *p* is the loss rate (fraction of packets dropped)  
  - *C* is a constant that describes how efficiently a given congestion control algorithm uses available bandwidth in the presence of loss. 
  
  Throughput is inversely proportional to both RTT and the square root of *p*, and their effects multiply. Going from (10ms RTT, 0.1% loss) to (100ms RTT, 1.0% loss) is not a 2x penalty; it is approximately 31x.

  This formula is the central experiment in Lab 1. You will explore it visually, predict outcomes for four combinations of RTT and loss, and then measure them with `iperf3` to verify the prediction.

- **Explain incast collapse and why fan-in workloads are uniquely vulnerable.**  
  When many hosts simultaneously transmit data to a single receiver (a distributed storage read, an AI all-reduce, a MapReduce fan-in) all flows burst at once. This is a common traffic pattern in workflows like distributed storage (one host receiving data from many storage servers at once), AI/ML AllReduce functions, and fan-in MapReduce (among others).
  
   The switch buffer at the receiving host, or points of congestion in the network path leading to the receiving host, can fill in microseconds. TCP interprets the resulting frame drops as independent congestion signals and backs off synchronously across all senders. When the RTO fires, all senders restart simultaneously and collapse again. 

  There are only a few defences:
  - **Deep buffers:** delay the collapse, but at the cost of latency (bufferbloat).
  - **ECN:** signal congestion before the buffer fills so senders back off before drops occur.
  - **DCTCP:** react proportionally to ECN marks rather than halving `cwnd` on a single mark.
  - **Lossless transport (RDMA/InfiniBand):** eliminate the problem by ensuring no drops ever occur.

- **Identify traffic matrices and predict likely bottlenecks.**
  Given a workload description (web serving, enterprise applications, distributed storage, AI training, backup replication), identify the dominant traffic patterns and predict where congestion is most likely to occur.  

- **Distinguish TCP-internal congestion signals from interface-level ones, and know what each can and can't see.**  
  `cwnd`, retransmits, and RTT live entirely on the end host's TCP stack — visible via `ss -tip`, invisible to anything watching the network from outside. Interface utilization lives on the switch/router port itself, polled via SNMP — visible to a monitoring platform, but with no notion of any individual flow's `cwnd` or retransmit count. Neither view is more "correct"; they answer different questions, and conflating them (treating a busy interface as proof of TCP retransmits, or the reverse) is a common operational mistake.

  A related limitation: SNMP-based monitoring (e.g. LibreNMS) typically polls each device on an interval of several minutes, then reports an *average* over that window. A link can show a moderate average while a sub-second incast burst saturates and drains its buffer dozens of times within the same polling window — the average hides exactly the failure mode this week is about. Lab 2 gets hands-on with a real monitoring API (devices, interface counters) and includes a simple utilization calculation as one example of turning raw counters into a meaningful number.

- **Describe spine-leaf fabric architecture and the role of ECMP.**  
  Spine-leaf (a folded Clos topology) is the dominant modern datacenter fabric design. Every leaf switch connects to every spine switch with equal-cost paths. ECMP distributes flows across spines by hashing the 5-tuple (source IP, destination IP, source port, destination port, protocol). The oversubscription ratio, which is total leaf downlink bandwidth divided by total leaf uplink bandwidth, determines the worst-case contention when all hosts transmit simultaneously.

  Oversubscription is an engineering trade-off, not a design flaw. Web traffic is bursty and uncorrelated, so a 4:1 ratio is usually acceptable in practice. Distributed ML training, RDMA workloads, and distributed storage all produce correlated, bulk, synchronised traffic that can hit the oversubscription limit simultaneously. Fabric design must account for the actual traffic matrix, not its average.

- **Contrast ECMP with LAG-based multi-path forwarding.**  
  ECMP (routed, per-flow hash) scales to arbitrary fabric sizes and requires no per-link protocol overhead. Its limitation is the elephant-flow problem: a single large TCP flow always hashes to one path and can never use more than one spine. A 100 Gbps flow on a fabric with two 100 Gbps spine uplinks still gets only 100 Gbps.

  LAGs (Link Aggregation Groups, 802.3ad/LACP) bond multiple physical links into a single logical interface. Although some implementations support per-packet distribution, most production LAGs also use hashing and therefore share the same elephant-flow limitations as ECMP. LAGs require LACP negotiation, and cannot extend beyond directly-connected devices, both complicate network design. The shift from LAG-dominated campus designs to routed ECMP datacenter fabrics is the architectural story the Al-Fares fat-tree paper tells.

  *Note: The important take-away here is that leveraging LAGs and/or ECMP are design considerations with non-overlapping pro's and con's.*

- **Stretch: Explain UDP and when it is the right transport.**  
  UDP provides no delivery guarantee, no ordering, no congestion control, and no connection state. It can be the right transport choice when the application can tolerate loss, when latency matters more than reliability (gaming, VoIP), or when the application implements its own reliability. 
  
  *Note: In fact, many modern web video services use the [QUIC protocol](https://peering.google.com/#/learn-more/quic) developed by Google, which runs over UDP but reimplements reliability and congestion control in user space.*

---

## Architecture: Putting It Together

The topics this week are not independent skills to be checked off a list. They are constraints that a network architect must satisfy simultaneously, and they pull against each other in ways that make the design problem interesting.

TCP's congestion behaviour sets the floor for what the network must provide. The Mathis formula tells you what a single flow will actually achieve given a specific RTT and loss rate. Incast collapse tells you what happens when you scale that to dozens or hundreds of flows hitting the same bottleneck at the same instant. These are not edge cases to be tuned away; they are structural properties of TCP that your architecture either accommodates or runs into.

The fabric decisions follow from the traffic. Oversubscription ratio is not a cost-cutting measure with a hidden performance penalty; it is a deliberate architectural choice whose consequences depend entirely on what you plan to run on the network. A 4:1 oversubscribed spine-leaf works well for web serving, where traffic from thousands of clients is statistically unlikely to all converge on the same uplink at the same moment. The same 4:1 fabric fails badly for distributed ML training, where the all-reduce communication pattern is explicitly synchronised and saturates every uplink at exactly the same time, every training step. The architecture is the same. The traffic matrix is different. The outcome is completely different. What is a completely viable and reliable design for one organization could be disastrously failure prone for an organization with different traffic patterns.

ECMP vs LAG is a similar trade-off, but at the level of individual flows. ECMP scales to arbitrary topology depth and works without any per-link protocol, but it cannot split a single flow across multiple paths. If your workload produces elephant flows, ECMP gives you a lot of paths but each elephant occupies one entirely. LAGs can distribute frames within a single flow, but only works between directly connected devices while adding operational complexity. Most modern datacenter designs choose ECMP at the fabric layer and accept the elephant-flow limitation because the alternative, chaining LAGs across multiple hops, does not scale financially or architecturally.

The deeper point is that all of these decisions interact:  
- Choosing a non-blocking spine-leaf topology removes oversubscription as a failure mode, but does not protect against incast collapse at the receiver while potentially multiplying the cost of networking cables, transceivers, and switches.  
- Adding ECN and AQM at the fabric layer helps with incast but requires endpoint software support to be effective.  
- Choosing RDMA and a lossless fabric removes the TCP retransmit problem entirely, but introduces a new set of constraints around PFC propagation and deadlock avoidance.  

There is no single architecture that makes all of the problems disappear; there are only trade-offs chosen with a specific workload and cost target in mind.

This is what network architecture actually is: understanding the needs of an organization or project, being able to predict how the design would behave under load, and selecting the control-plane and transport mechanisms that keep the network stable when the load is as bad as it can be, not just when it is average.

---

## The Week 8 Bridge

Every concept this week has a direct counterpart in Week 8 (InfiniBand, RDMA, RoCE). Understanding the problem here makes the engineering choices there legible:

| Week 4 concept | Why it matters | Week 8 counterpart |
|---|---|---|
| **Mathis formula:** any loss causes multiplicative throughput collapse | RDMA has no retransmit capability; any loss stalls or fails the operation | RoCE requires **zero loss**; DCQCN signals congestion before any drop via ECN |
| **BDP:** latency amplifies the cost of loss | Datacenter RTTs must stay below 1ms or per-flow throughput collapses at scale | IB and RoCE fabrics target 1-10µs RTT; lossless paths eliminate the RTT penalty term |
| **Incast:** synchronised fan-in exhausts switch buffers | All-reduce in distributed training is precisely N-to-1 fan-in, synchronised | InfiniBand uses **credit-based flow control**: a sender cannot transmit until the receiver grants a credit, so buffers never fill and drops never happen |
| **ECN:** signals congestion before the drop | Back off before the problem rather than after | **DCQCN** uses ECN to throttle RoCE senders; PFC is the backstop before the buffer actually overflows |
| **Non-blocking Clos:** architecture eliminates the shared bottleneck | Correlated traffic patterns violate the statistical multiplexing assumption | IB fabrics are **generally non-blocking**; RoCE deployments target non-blocking or near-non-blocking underlay with PFC/DCQCN compensating for oversubscription |
| **SNMP polling averages over minutes** | A multi-minute average can't see a microsecond-scale incast burst | Lossless fabrics react **per-packet** (ECN/PFC) instead of waiting on a polling cycle |
