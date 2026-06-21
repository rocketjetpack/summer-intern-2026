---
title: Terminology
---

# Week 4 — Terminology

| Term / Acronym | Definition |
|---|---|
| **ACK** | Acknowledgement — a TCP control segment confirming receipt of bytes up to a given sequence number |
| **AIMD** | Additive Increase, Multiplicative Decrease — the core TCP congestion control law: increase `cwnd` by one MSS per RTT when the path is clear; halve it on a loss event |
| **AQM** | Active Queue Management — a class of router/switch queue disciplines that proactively signal congestion (via drop or ECN mark) before the buffer is completely full |
| **BBR** | Bottleneck Bandwidth and RTT — Google's congestion control algorithm that models the bottleneck bandwidth and propagation delay directly, rather than reacting to loss signals |
| **BDP** | Bandwidth-Delay Product — `bandwidth × RTT`; the number of bytes that fit "in flight" in the network at full utilisation |
| **CE** | Congestion Experienced — the ECN codepoint (binary `11` in the IP ToS field) set by a router to signal congestion to the receiver |
| **Clos** | A multi-stage switching fabric topology (named after Charles Clos, 1953) that achieves non-blocking throughput by providing multiple equal-cost paths between any input and output. The original design uses three stages: ingress (input), middle, and egress (output) — traffic enters on an ingress switch, crosses one of several middle switches, and exits on an egress switch. As long as enough middle-stage switches exist, any ingress port can always reach any egress port without contention, even when all ports are simultaneously active. |
| **CUBIC** | The default Linux TCP congestion control algorithm; uses a cubic function to grow `cwnd` after a loss, recovering faster than classic AIMD on high-bandwidth paths |
| **cwnd** | Congestion Window — the TCP sender's self-imposed limit on unacknowledged bytes in flight, used to implement congestion control |
| **CWR** | Congestion Window Reduced — a TCP flag the sender sets to acknowledge that it has reduced `cwnd` in response to an ECE signal |
| **DCQCN** | Data Center Quantized Congestion Notification — the RoCE congestion control mechanism; uses ECN marks to throttle RDMA senders before buffer overflow |
| **DCTCP** | Data Center TCP — a TCP variant that uses ECN to back off proportionally to the fraction of marked packets rather than halving on any single mark |
| **Discards** | Frames an interface dropped without forwarding them — typically because an egress queue was full. Visible as an SNMP interface counter (part of the standard `ifTable`, RFC 2863); a different signal from a TCP retransmit, which only the end host sees |
| **ECE** | ECN Echo — a TCP flag the receiver sets to tell the sender that a CE-marked packet was received |
| **ECMP** | Equal-Cost Multi-Path — a routing technique that distributes flows across multiple equal-cost paths using a hash of the packet's 5-tuple |
| **ECN** | Explicit Congestion Notification — an IP/TCP mechanism (RFC 3168) that allows a router to set a congestion signal in the IP header before the buffer fills and drops occur |
| **Fan-in** | A traffic pattern where many senders send to one receiver simultaneously. The receiver's ingress link or buffer becomes the shared bottleneck. Fan-in is the structural cause of incast collapse: the more senders, the worse the problem. Common workloads with fan-in patterns include distributed storage reads, MapReduce shuffles, and all-reduce in distributed ML training. |
| **Fan-out** | A traffic pattern where one sender distributes data to many receivers simultaneously. Common in broadcast or multicast scenarios, and in request distribution (a load balancer sending work to a pool of workers). Fan-out itself is not usually a congestion problem because each receiver sees only one sender. |
| **FIN** | Finish — the TCP flag used to signal the end of a data stream and begin connection teardown |
| **Folded Clos** | A Clos fabric where the ingress and egress stages are collapsed into a single tier of switches — the "leaf" layer — that connects both to hosts and to the middle-stage "spine" switches. Each leaf connects to every spine; return traffic folds back through the same spine tier rather than exiting through a separate egress tier. This halves the number of switch tiers required and is the standard architecture of modern datacenter spine-leaf fabrics. The fat-tree topology (Al-Fares 2008) is a specific folded Clos instantiation using commodity switches. |
| **Incast** | A specific failure mode caused by fan-in traffic at scale. When N senders all respond to a single receiver at the same instant (for example, a storage client requesting data striped across N nodes), all N flows burst simultaneously, filling the switch buffer in microseconds. TCP interprets the resulting drops as independent congestion signals and backs off synchronously. When the retransmit timer fires, all N senders restart at the same time and collapse the buffer again. Total throughput can fall far below what the link capacity would suggest, and the collapse worsens super-linearly as N grows. |
| **InfiniBand (IB)** | A high-speed interconnect standard used in HPC and AI clusters; provides credit-based lossless flow control and non-blocking Clos fabric specifications by design |
| **IP** | Internet Protocol — network layer protocol responsible for addressing and routing packets between hosts |
| **ISN** | Initial Sequence Number — a random number chosen by each side of a TCP connection during the handshake to prevent collisions with prior connections |
| **LAG** | Link Aggregation Group — bonding multiple physical links into a single logical interface (also called port-channel or EtherChannel); standardised as IEEE 802.3ad/LACP |
| **LACP** | Link Aggregation Control Protocol — the IEEE 802.3ad control protocol that negotiates and maintains a LAG between two directly-connected devices |
| **MSS** | Maximum Segment Size — the largest payload a TCP segment may carry, typically 1460 bytes (1500-byte Ethernet MTU minus 20-byte IP header minus 20-byte TCP header) |
| **MTU** | Maximum Transmission Unit — the largest frame a link layer can carry; 1500 bytes on standard Ethernet |
| **Open Clos** | A Clos fabric deployed in its natural three-stage form, where ingress, middle, and egress switches are physically distinct devices. The terms "input stage," "middle stage," and "output stage" map to distinct rows of hardware. Telephone switching systems and early large-scale fabrics used this layout. Less common in modern datacenters because it requires distinct hardware tiers. |
| **PFC** | Priority Flow Control — IEEE 802.1Qbb; an Ethernet mechanism that sends a PAUSE frame upstream on a per-traffic-class basis to prevent buffer overflow on a lossless fabric |
| **RDMA** | Remote Direct Memory Access — a mechanism allowing one host to read or write the memory of another without involving the remote CPU; requires a lossless, in-order network |
| **RoCE** | RDMA over Converged Ethernet — a protocol stack (RoCEv1/v2) that carries RDMA semantics over an Ethernet network; requires a lossless underlay (PFC + DCQCN) |
| **RTO** | Retransmission Timeout — the timer TCP uses to detect a lost segment when duplicate ACKs have not arrived; fires much more slowly than fast retransmit |
| **RTT** | Round-Trip Time — elapsed time from sending a segment to receiving its acknowledgement; the fundamental clock of TCP congestion control |
| **SNMP** | Simple Network Management Protocol — the protocol monitoring platforms like LibreNMS use to poll counters (utilization, errors, discards) from a device's interfaces. Polls happen on an interval (commonly every 5 minutes), so values are averages over that window, not instantaneous readings |
| **ssthresh** | Slow-Start Threshold — the `cwnd` value at which TCP switches from exponential slow-start growth to linear AIMD growth |
| **SYN** | Synchronise — the TCP flag used to initiate a connection and exchange initial sequence numbers |
| **TCP** | Transmission Control Protocol — connection-oriented, reliable, ordered byte-stream transport layer protocol |
| **UDP** | User Datagram Protocol — connectionless, unreliable, unordered transport layer protocol; no congestion control |
| **Utilization** | The fraction of an interface's `ifSpeed` actually in use, computed as `(bits/sec) / ifSpeed`. An interface-level signal visible to SNMP monitoring; sustained high utilization is a Mathis-style bottleneck candidate, but a multi-minute polling average can hide short, severe bursts (see incast) |
