---
title: Labs
---

# Week 4 — Labs

Lab 1 uses the `nettools:week04` image — start with Lab 0 to build it before deploying any topology. Lab 2 does not use ContainerLab at all; it queries a live external API instead.

Two labs build a single argument: a single flow under controlled impairment, measured on infrastructure you built yourself (Lab 1), then real congestion signals on infrastructure you don't control (Lab 2). Each lab ends with a callout connecting the observation to Week 8.

Lab 1 requires `sudo` — `tc` (Linux traffic control), ContainerLab, and certain network observation tools need root. Lab 2 requires no root access, just Python 3, `requests`, and an API key.

## 1. [Lab 1: Loss × Latency Amplification](./lab1)

The Mathis formula — `throughput ≈ (MSS / RTT) × (C / √p)` — predicts that loss and latency interact multiplicatively on TCP throughput: doubling both RTT and loss rate doesn't halve throughput, it reduces it by roughly 4×. This lab makes that prediction concrete. An interactive Observable chart lets you explore the formula, then a 2×2 iperf3 experiment on a ContainerLab bottleneck link validates it against measurement.

**Tools:** Observable Framework (interactive chart), `tc-netem`, `iperf3`, `ss -tip`.

## 2. [Lab 2: Querying Network Data with the LibreNMS API](./lab2)

A short, broad introduction to pulling real operational data out of the organization's LibreNMS instance via its REST API: device inventory and interface counters, including a simple utilization calculation. Less a single experiment than three small exercises in authenticating, querying, and joining records from a monitoring platform — a different vantage point than Lab 1's end-host view.

**Tools:** LibreNMS API, Python `requests`.

