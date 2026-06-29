---
title: Terminology
---

# Week 5 — Terminology

| Term / Acronym | Definition |
|---|---|
| **5-tuple** | Source IP, destination IP, source port, destination port, and protocol — the most common key used to identify a single flow |
| **Active Timeout** | A NetFlow/IPFIX flow cache setting: a still-running flow is exported periodically (e.g. every 60s) even though it hasn't ended, so long-lived flows don't wait forever to become visible |
| **Agent** | The device or process generating telemetry — the sFlow or NetFlow/IPFIX exporter role |
| **Collector** | The system receiving and decoding exported telemetry (sFlow datagrams or NetFlow/IPFIX flow records) |
| **Counter Sampling** | The sFlow mechanism that periodically pushes interface counters (similar in spirit to SNMP, but device-initiated rather than polled) |
| **Estimation Error** | The expected difference between a sampled estimate (e.g. sFlow's extrapolated total) and the true value; shrinks as the sampling rate increases (smaller *N*) |
| **Exporter** | A device configured to send flow telemetry to a collector; synonymous with "agent" in NetFlow/IPFIX terminology |
| **Flow** | A single "conversation" as defined by a telemetry system: typically a 5-tuple plus interface, byte/packet counts, and start/end time |
| **Flow Cache** | The table a NetFlow/IPFIX exporter maintains in memory, keyed by flow identity, accumulating counters until the flow is exported |
| **Flow Export** | The act of sending a completed or timed-out flow cache entry to a collector as a flow record |
| **Flow Record** | A single exported entry describing one flow: its key fields plus accumulated packet/byte counts and timestamps |
| **Ground Truth** | The actual, true value (e.g. total bytes transferred, as reported directly by `iperf3`) used to evaluate how accurate a sampled estimate is |
| **Inactive Timeout** | A NetFlow/IPFIX flow cache setting: a flow with no matching traffic for some period is considered ended and exported/evicted from the cache |
| **IPFIX** | IP Flow Information Export (RFC 7011) — the IETF-standardized, template-based successor to NetFlow v9; vendor-neutral and extensible |
| **NetFlow** | Cisco's flow export protocol; v5 has a fixed record format, v9 introduced flexible, template-based records (the basis for IPFIX) |
| **Packet Sampling** | The sFlow mechanism that selects a pseudorandom 1-in-*N* packet from the forwarding path and exports its header/metadata unprocessed |
| **Sampling Rate** | The 1-in-*N* ratio at which sFlow selects packets; smaller *N* means more samples (lower error, higher overhead) |
| **sFlow** | A sampling-based telemetry protocol (sFlow.org / originally RFC 3176) combining packet sampling and counter sampling, exported as raw, unaggregated UDP datagrams |
| **sFlow Agent** | The sFlow process running on the sampled device, responsible for selecting samples and sending datagrams to a collector |
| **sFlow Datagram** | A single UDP packet sent by an sFlow agent, containing one or more packet/counter samples |
| **Template (IPFIX)** | A record describing the field layout of subsequent flow records; sent once and referenced by ID, which is what makes IPFIX's record format extensible/flexible rather than fixed like NetFlow v5 |
| **Top Talkers** | The hosts or flows responsible for the largest share of traffic volume in a given window — a common flow-telemetry query |
