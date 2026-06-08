---
title: "2026 Network Engineering Internship
stoc: true
---

# 2026 Network Engineering Intern
June 2026 - August 2026

## Overall Goal

My goal with the structure of this internship is to build each week upon the previous topics. Each week will include some reading material to provide a foundation for exploring the weeks topics. In addition, each week will feature some number of lab exercises. Some of these will be doable on your laptop or workstation, and some will require elevated access on one of the lab servers that will be made available for your use.

## Project

I've tried to frame each weeks topics such that they can provide some relevence to your project if you find it relevent.

Rather than building your project in a rush at the end, I encourage you to build it incrementally as we go, focusing on how each week relates to your end goal. Early phases should focus on the data structure... what data do you need to collect, how does it get collected, where and how does it get stored (if it gets stored at all)?
 
| Stage | Weeks | What gets built |
|-------|-------|-----------------|
| 0 — Know what to measure | 1–3 | A living "metric catalog": what counters/fields indicate trouble, and why |
| 1 — Collect | 4 | A Python collector that polls interface counters (utilization, errors, discards) |
| 2 — Optical | 5 | Collector extended with transceiver/optical metrics + first "red flag" logic for potential problems |
| 3 — Fabric | 6–7 | InfiniBand/RDMA counters folded into one unified data model |
| 4 — Store & dashboard | 8 | Time-series storage (Prometheus/InfluxDB) + a Grafana dashboard or other presentation layer |
| 5 — Topology view | 9 | Interactive topology graph: nodes = devices, edges = links, colored by load, flagged on errors |
 
A single Python data schema (device → interface/port → timestamped sample) is introduced mid-summer and can be reused for Ethernet, optical, and InfiniBand sources.


## Weekly Pattern
 
The following weekly pattern is just a suggestion. You are welcome to work at your own pace.
 
| Day | Focus | Details |
|-----|-------|---------|
| **Mon** | Readings + planning | Assigned readings (~2–4 hrs), with a short written "what I learned / what confused me" note. Catch up for weekly planning. |
| **Tue–Wed** | Hands-on labs | Hands-on labs, with questions to hopefully spur additional research. Optional readings. |
| **Thu–Fri** | Project work | Code lab + that week's project increment. |
| **Fri (30 min)** | Check-in | If you would like to demo project status, please feel welcome. |


