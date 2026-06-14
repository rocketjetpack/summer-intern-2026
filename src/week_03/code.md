---
title: Labs
---

# Week 3 — Labs

This week is your pivot from L2 to L3: you'll build a series of Containerlab topologies that take the same Arista cEOS switch from a pure L2 device to a device that's *also* a router, then extend that into a small multi-device network. Along the way you'll write a subnet-math helper, trace real paths across the public internet to see the same forwarding decisions made hop-by-hop outside the lab, and start modeling your topology as a graph — the foundation for the rest of the program's visualizer.

## 0. Build your host image

Before any of the Containerlab labs: work through the [Docker Lab](../tools/docker). It walks you through containers from first principles and ends with you building `nettools:week03` — the image every Linux host in Labs 1-3 runs.

## 1. [Lab 1: L2 Fundamentals](./lab1)

One switch, two hosts, one subnet/VLAN. Enable LLDP everywhere and validate plain L2 connectivity — MAC table, ARP, LLDP neighbors. No routing yet.

## 2. [Lab 2: The L2/L3 Pivot](./lab2)

Same switch, but now the two hosts sit in different VLANs/subnets — and the switch itself routes between them via SVIs and `ip routing`. This is the conceptual core of the week.

## 3. [Lab 3: Extended Topology](./lab3)

Add a dedicated router and a third host. Static routes connect `sw1`'s routing domain to `rtr1`'s, giving you a small multi-device network with both connected and static routes to inspect.

## 4. [Code Lab: Subnet Helper](./subnet-helper)

A Python `ipaddress`-based subnet helper, exercised against the addressing schemes from Labs 2 and 3.

## 5. [Code Lab: Path Explorer](./path-explorer)

Trace the path from your workstation to public internet destinations, hop by hop, and connect it back to the longest-prefix-match forwarding behavior from this week's reading.

## 6. [Project Increment: Topology Graph](./project)

Model Lab 3's topology as a `networkx` graph — the skeleton data structure the eventual visualizer renders.

## What's next

Once Labs 1-3 are working, head to the [Podman Lab](../tools/podman) to stand up a Prometheus + Grafana stack on your own workstation — the telemetry foundation you'll build on for the rest of the program.
