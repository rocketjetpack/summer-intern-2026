---
title: Labs
---

# Week 5 — Labs

Both labs use the `nettools:week05` image and the same four-node topology (`host1`, `rtr1`, `host2`, `collector`) — start with Lab 0 to build the image before deploying either topology. `rtr1` plays the exporter role throughout: it forwards traffic between `host1` and `host2` and exports flow telemetry for that traffic to `collector`.

Two labs build a single argument: identical `iperf3` traffic, measured two different ways. Lab 1 samples it statistically (sFlow); Lab 2 accounts for it exactly (NetFlow/IPFIX). Each lab measures the same kind of traffic so the accuracy/overhead/timeliness trade-off from the objectives is something you observe directly, not just read about.

Both labs require `sudo` on the ContainerLab host (ContainerLab itself, plus interface/forwarding configuration on `rtr1`).

## Why a Linux host as the exporter, not a switch?

`rtr1` is a Linux container, not an Arista cEOS switch, and that's a deliberate choice, not just lab convenience. Real networks export sFlow/NetFlow/IPFIX from software running on a Linux host more often than the "telemetry only comes from switch hardware" mental model suggests:

- **Switch/router hardware sometimes just doesn't support the protocol you need.** One write-up tested several commercial firewalls (Sophos XG, Juniper vSRX, Palo Alto, Fortigate) while trying to deploy IPFIX and found none offered usable IPFIX export — most supported only the older NetFlow v9, or buried IPFIX behind extra licensing. They exported flow data from a Linux box running `pmacct`'s `nfprobe` instead. ([LoginSoft — IPFIX Data Export](https://www.loginsoft.com/post/ipfix-data-export-from-research-to-successful-log-collection))
- **Virtualized traffic may never touch a physical switch ASIC at all.** VM-to-VM traffic on the same hypervisor host can stay entirely inside a software vSwitch — a host agent (the same role `hsflowd`/`softflowd` play on `rtr1` here) is the only thing positioned to see it. ([sFlow.com — Comparing sFlow and NetFlow in a vSwitch](https://blog.sflow.com/2011/10/comparing-sflow-and-netflow-in-vswitch.html))
- **Hardware-based export has its own real limitations**, the ones this week's objectives describe in the abstract: NetFlow's flow cache lives in a fixed-size hardware table, so a sudden flood of new flows (a DDoS, a scan) can exhaust it and spike control-plane CPU; sFlow's fixed sampling rate means small flows are statistically unlikely to ever be picked, while large flows dominate the samples. (See Cisco's [NetFlow and sFlow key concepts guide](https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/netflow/configuration/b-netflow-configuration-ios-xr-8000/netflow-sflow-key-concepts.html) for a vendor's own framing of this.)
- **[pmacct](https://github.com/pmacct/pmacct)** is the production-grade analog of the smaller `hsflowd`/`softflowd` tools used in these labs — a single Linux package that can act as an sFlow/NetFlow/IPFIX probe, collector, and analyzer at once, and it's widely deployed in exactly this "Linux box as exporter" role.

None of this makes switch/router-based export unusual — it's still the most common deployment for physical, wired infrastructure, and Lab 1's optional stretch goal has you configure `sflow` on the Arista cEOS switch directly. But starting on a Linux host, where you have full visibility into the agent's behavior and exact ground-truth counters to compare against, makes the accuracy/overhead trade-off in these two labs much easier to observe cleanly.

## 1. [Lab 1: sFlow — Sampling and Estimation](./lab1)

`rtr1` runs `hsflowd`, sampling 1-in-*N* packets crossing it and pushing raw samples to `collector` over UDP. You'll decode the samples, extrapolate a total-traffic estimate from the sampling rate, and compare it against `iperf3`'s own ground-truth throughput — then vary the sampling rate and watch the accuracy/overhead trade-off move.

**Tools:** `hsflowd`, `sflowtool`/`goflow2`, `iperf3`.

## 2. [Lab 2: NetFlow/IPFIX — Exact Flow Accounting](./lab2)

Same topology, `rtr1` now runs `softflowd` instead, building an exact flow cache and exporting records to `collector`'s `nfcapd` listener. You'll query the results with `nfdump` (top talkers, flow duration, exact byte counts), observe a long flow split by the active timeout, and directly compare the result against Lab 1's sFlow estimate on the same traffic.

**Tools:** `softflowd`, `nfcapd`/`nfdump`, `iperf3`.

## 3. [Code Lab: Sampling Estimator](./sampling-estimator)

Before (or alongside) Lab 1: an interactive explorer for the statistics behind 1-in-*N* packet sampling — predict the expected estimation error for a given sampling rate and traffic volume before you measure it for real.
