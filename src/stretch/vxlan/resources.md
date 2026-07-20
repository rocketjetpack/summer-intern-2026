---
title: Resources
---

# VXLAN: Resources

Readings are grouped by topic. Read the Required entries before starting the corresponding lab; Recommended entries deepen understanding but are not prerequisites.

---

## Before Lab 1: VXLAN Flood-and-Learn

### Required

- **RFC 7348: [Virtual eXtensible Local Area Network (VXLAN): A Framework for Overlaying Virtualized Layer 2 Networks over Layer 3 Networks](https://datatracker.ietf.org/doc/html/rfc7348)**
  The canonical VXLAN specification. Section 3 (frame format) and Section 4 (VTEP behavior, including flood-and-learn and head-end replication) are the sections this topic's objectives and lab draw on directly. You don't need to memorize the wire format; focus on what each layer of encapsulation is for.

- **Vincent Bernat (2017): [VXLAN & Linux](https://vincent.bernat.ch/en/blog/2017-vxlan-linux)**
  A practical, Linux-specific walkthrough of exactly the mechanism Lab 1 builds by hand: `ip link add type vxlan`, unicast head-end replication via `bridge fdb append 00:00:00:00:00:00 dst <remote>`, and how to read the resulting FDB entries. Written by a well-known Linux networking engineer; treat this as the practical companion to the RFC's theory.

### Recommended

- **[Linux Kernel Documentation: Virtual eXtensible Local Area Networking](https://docs.kernel.org/networking/vxlan.html)**
  The kernel's own reference for the `vxlan` driver and every `ip link add type vxlan` option. Useful if you want to know exactly what a flag like `dstport` or `local` is actually configuring underneath the `ip` command.

---

## Before the Code Lab: VNI/MTU Overhead

### Required

- **PacketPushers: [TCP/IP over VXLAN Bandwidth Overheads](https://packetpushers.net/blog/vxlan-udp-ip-ethernet-bandwidth-overheads/)**
  Breaks down the same 50-byte overhead figure (14B outer Ethernet + 20B outer IPv4 + 8B outer UDP + 8B VXLAN header) this topic's [Code Lab](./vni-overhead) calculates from first principles, and carries the math one step further into what that overhead costs as a percentage of a full TCP/IP payload. Useful as an independent check that the byte-counting in the lab matches an outside source.

---

## Tools

### Recommended

- **`ip link`, `bridge fdb`, `bridge vlan`** (iproute2): already present in `nettools:week05`; no new packages are required for this topic. Alpine's `iproute2` package bundles both the VXLAN netlink interface and the `bridge` command, confirmed when [Lab 0](./lab0) builds `nettools:vxlan`.
- **`tcpdump`**: already present since Week 3; modern versions decode the VXLAN header natively (`-vv` shows the VNI), which Lab 1 uses to inspect encapsulated traffic on the underlay.

*Note: as with previous weeks, exact kernel-module availability (the `vxlan` driver) depends on the ContainerLab host's running kernel, not the container image. [Lab 0](./lab0) includes a step to confirm it's loaded before deploying Lab 1's topology.*
