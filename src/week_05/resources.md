---
title: Resources
---

# Week 5 — Resources

Readings are grouped by topic. Read the Required entries before starting the corresponding lab; Recommended entries deepen understanding but are not prerequisites.

---

## Before Lab 1: sFlow

### Required

- **[sFlow.org — sFlow Version 5](https://sflow.org/sflow_version_5.txt)**
  The canonical sFlow specification. You don't need to memorize the wire format — focus on the structure: a datagram carries one or more packet-flow-samples and/or counter-samples, and the device does no aggregation at all.

- **Nick Duffield (2004) — [Sampling for Passive Internet Measurement: A Review](https://www.stat.purdue.edu/~chuanhai/teaching/Stat598Q/papers/duffield_review.pdf)**
  Required before Lab 1. Covers the statistics behind sampled traffic measurement — what a 1-in-*N* sample tells you about the true population, and how confident you can be in that estimate. Directly grounds the [Sampling Estimator](./sampling-estimator) code lab.

### Recommended

- **[RFC 3176 — InMon Corporation's sFlow](https://www.rfc-editor.org/rfc/rfc3176)**
  The original sFlow informational RFC, predating the sFlow.org v5 spec. Useful historical context on the design motivation (ASIC-speed sampling with zero device-side aggregation).

---

## Before Lab 2: NetFlow / IPFIX

### Required

- **RFC 3954 — [Cisco Systems NetFlow Services Export Version 9](https://www.rfc-editor.org/rfc/rfc3954)**
  Skim for the structure: NetFlow v9 introduced flexible, *template*-based records (replacing v5's fixed format), which is the idea IPFIX later standardized.

- **RFC 7011 — [Specification of the IP Flow Information Export (IPFIX) Protocol](https://www.rfc-editor.org/rfc/rfc7011)**
  The IETF's vendor-neutral standardization of the NetFlow v9 model. Sections 1-3 cover the motivation and basic architecture (exporter, collector, templates); that's enough for this week.

### Recommended

- **Cristian Estan & George Varghese (2002) — [New Directions in Traffic Measurement and Accounting](https://www.cse.ucsd.edu/~varghese/PAPERS/sigcomm2002.pdf)**
  Motivates *why* exact flow-cache accounting is expensive: the cache has to track every distinct flow currently active, and a network with many small flows (or one under attack) can grow that cache far faster than a network carrying the same byte volume across fewer, larger flows. Connects directly to flow-table exhaustion as a denial-of-service technique — a preview of Week 10.

---

## Tools

### Recommended

- **[softflowd](https://github.com/irino/softflowd)** — the Linux NetFlow/IPFIX exporter used in Lab 2. Skim the README for `-T` (template fields) and `-t` (active/inactive timeout) flags before the lab.
- **[nfdump](https://github.com/phaag/nfdump)** — the NetFlow collector/query toolkit (`nfcapd` to receive, `nfdump` to query) used in Lab 2.
- **[goflow2](https://github.com/netsampler/goflow2)** — a single collector binary that decodes sFlow, NetFlow v9, and IPFIX; a reasonable choice to avoid running separate decoders per protocol in Lab 0/Lab 1.
- **[hsflowd](https://github.com/sflow/host-sflow)** — the host-based sFlow agent used in Lab 1.

*Note: exact package availability for these tools on the lab server's Alpine-based images should be confirmed when Lab 0 is built — some may need to be compiled from source or installed as static binaries rather than pulled via `apk add`, the same caveat as confirming the cEOS image tag in [Week 3 Lab 1](../week_03/lab1).*
