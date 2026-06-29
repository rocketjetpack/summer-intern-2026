---
title: "Lab 2: NetFlow/IPFIX — Exact Flow Accounting"
---

# Lab 2: NetFlow/IPFIX — Exact Flow Accounting

# NOTE: THIS LAB IS STILL BEING VALIDATED

**Before proceeding, complete [Lab 0](./lab0). This lab reuses Lab 1's topology** — same four nodes, same addressing — but `rtr1` runs `softflowd` instead of `hsflowd`, building an exact flow cache instead of sampling, and `collector` runs `nfcapd`/`nfdump` instead of `goflow2`.

**This lab should be done on the lab host configured for you to have privileged access to.**

## Topology

![Week 5 topology: host1 (10.5.1.10/24) and host2 (10.5.2.10/24) connected through rtr1, which also connects to collector (10.5.9.10/24) on a third interface](./topology.svg)

Identical to [Lab 1](./lab1)'s topology and addressing.

## Step 0: Prepare and deploy

```bash
mkdir -p $HOME/container-lab/week05/lab2
cd $HOME/container-lab/week05/lab2
```

Reuse Lab 1's topology file (copy it or symlink it) — it's unchanged for this lab:

```bash
cp ../lab1/lab1.clab.yml lab2.clab.yml
sed -i 's/week05-lab1/week05-lab2/' lab2.clab.yml
containerlab deploy -t lab2.clab.yml
docker exec -it clab-week05-lab2-host1 ping -c 3 10.5.2.10
```

## Step 1: Start the NetFlow collector

```bash
docker exec -it clab-week05-lab2-collector mkdir -p /data/netflow
docker exec -d clab-week05-lab2-collector nfcapd -D -l /data/netflow -p 9995 -t 30
```

`-t 30` rolls capture files every 30 seconds instead of the 5-minute default, so you don't have to wait a full polling window to query results during the lab. `-p 9995` is an arbitrary but conventional NetFlow collector port.

## Step 2: Start the exporter on `rtr1`

`softflowd` binds to one interface per process. Run it on `eth1` only — `rtr1` forwards every `host1↔host2` packet from one transit interface to the other, so `eth1` alone already sees the full bidirectional conversation. Running a second instance on `eth2` would generate a *second* flow record for the same forwarded traffic, double-counting it once you sum byte/packet counts in Step 4 — the same trap as tapping both interfaces in [Lab 1](./lab1):

```bash
docker exec -d clab-week05-lab2-rtr1 softflowd -i eth1 -n 10.5.9.10:9995 -v 9 -t maxlife=20 -t expint=5
```

- `-v 9` — export as NetFlow v9 (template-based, the basis for IPFIX).
- `-t maxlife=20` — **active timeout**: a still-running flow is force-exported every 20 seconds even if it hasn't ended.
- `-t expint=5` — how often (in seconds) the exporter checks the cache for timed-out flows.

*Check `softflowd -h` for the exact timeout-name syntax on your installed version — these flags have changed slightly across releases.*

## Step 3: Generate traffic and capture ground truth

```bash
docker exec -d clab-week05-lab2-host2 iperf3 -s
docker exec -it clab-week05-lab2-host1 iperf3 -c 10.5.2.10 -t 60 -i 10
```

As in Lab 1, capture exact ground truth directly from `rtr1`:

```bash
docker exec -it clab-week05-lab2-rtr1 ip -s link show eth1
```

## Step 4: Query the flow records

```bash
docker exec -it clab-week05-lab2-collector nfdump -R /data/netflow -o long
```

You should see multiple records for the **same** `host1↔host2` flow — not one. With a 60-second `iperf3` run and a 20-second active timeout, the flow gets force-exported roughly every 20 seconds even though `iperf3` never closed the connection.

**Questions:**
- Sum the byte/packet counts across all the records belonging to this one flow. How closely does that sum match the exact count from `ip -s link show eth1` in Step 3? (It should match far more closely than Lab 1's sFlow extrapolation did — there's no sampling here.)
- Why does a flow that's still actively transferring data get exported at all, before it ends? What would you miss if you only ever looked at flows *after* they closed?

## Step 5: Top talkers

```bash
docker exec -it clab-week05-lab2-collector nfdump -R /data/netflow -s ip/bytes -n 5
```

This aggregates by IP and sorts by bytes — the basic "who's using the most bandwidth" query mentioned in [objectives.md](./objectives). With only `host1` and `host2` active, the result should be unsurprising; the value of this query is in a network with many concurrent flows, which is closer to what Step 6 explores.

## Step 6: Inactive timeout and a quieter flow

Stop the `iperf3` transfer (let it finish or `Ctrl-C` it) and wait about 15 seconds — long enough to cross softflowd's default inactive/general timeout — then query again:

```bash
docker exec -it clab-week05-lab2-collector nfdump -R /data/netflow -o long
```

**Question:** Is there a new record marking the flow as finished, distinct from the periodic `maxlife`-driven exports you saw while it was running? What field in the record tells you whether a flow ended because of an **active timeout**, an **inactive timeout**, or a TCP FIN?

## Step 7: Compare against Lab 1

| | Lab 1 (sFlow) | Lab 2 (NetFlow/IPFIX) |
|---|---|---|
| Byte/packet count vs. ground truth | Estimated, with measurable error | Exact (sum across active-timeout-split records) |
| Visibility while the flow is running | Continuous (samples stream in real time) | Only at active-timeout intervals (here, every 20s) |
| `rtr1` state required | None — stateless sampling | One flow-cache entry per active flow, held until export |

**Question:** If `rtr1` suddenly carried 50,000 short-lived flows instead of one long one, which lab's approach would put more load on `rtr1` itself? Which would put more load on `collector`? (Revisit Estan & Varghese in [resources.md](./resources) if you want the deeper argument — this is also the structural reason flow-table exhaustion is a viable denial-of-service technique, a preview of Week 10.)

## Step 8: Clean up

```bash
containerlab destroy -t lab2.clab.yml --cleanup
```
