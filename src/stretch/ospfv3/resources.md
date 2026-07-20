---
title: "OSPFv3: Resources"
---

# OSPFv3 & Dynamic Routing: Resources

Read the Required entries before starting [Lab 1](./lab1); Recommended entries deepen understanding but are not prerequisites. IPv6 prerequisites (RFC 4291, RFC 4861, and the rest) are in [Week 7's resources](../../week_07/resources).

---

## Required

- **RFC 5340: [OSPF for IPv6](https://datatracker.ietf.org/doc/html/rfc5340)**
  The OSPFv3 spec. Read section 2 ("Differences from OSPF for IPv4") for the conceptual payload: per-link processing, link-local adjacencies, and the removal of addressing semantics from the core protocol. The packet-format detail beyond that is reference material.

- **FRR Documentation: [OSPFv3 (ospf6d)](https://docs.frrouting.org/en/latest/ospf6d.html)**
  The authoritative reference for every command Lab 1 uses: `ipv6 ospf6 area` on interfaces, `ospf6 router-id`, the hello/dead interval knobs, and the `show ipv6 ospf6` command family. Skim before the lab so the config stanzas read as vocabulary rather than incantation.

## Recommended

- **RFC 2328: [OSPF Version 2](https://datatracker.ietf.org/doc/html/rfc2328)**
  The canonical OSPF spec that RFC 5340 modifies. Not required reading at 244 pages, but section 4 ("Functional Summary") is the clearest short description of the link-state flooding/SPF machinery ever written, and it applies to v3 nearly unchanged.

- **ContainerLab: [FRR lab example (frr01)](https://containerlab.dev/lab-examples/frr01/)**
  ContainerLab's own reference FRR topology, using exactly the pattern Lab 1 borrows: `linux`-kind nodes running the official FRR image with `daemons` and `frr.conf` bind-mounted in. Lab 1's setup is this example adapted to OSPFv3 and IPv6.

- **Brian Linkletter: [Use ContainerLab to emulate open-source routers](https://brianlinkletter.com/2021/05/use-containerlab-to-emulate-open-source-routers/)**
  A readable walkthrough of the same FRR-in-ContainerLab pattern with more narrative than the official example, including how the daemons file and vtysh fit together.

- **RFC 6164: [Using 127-Bit IPv6 Prefixes on Inter-Router Links](https://datatracker.ietf.org/doc/html/rfc6164)**
  Six pages on why the lab's router-to-router links get /127s. Section 5's neighbor-cache-exhaustion rationale connects addressing hygiene to a real attack surface.

---

## Tools

- **[FRRouting](https://frrouting.org/)**: the open-source routing suite (a fork of Quagga) providing this topic's OSPFv3 implementation, and the BGP implementation the weeks 8-10 labs use. The container image lives at `quay.io/frrouting/frr`; Lab 0 pins the exact tag.
- **`vtysh`**: FRR's unified CLI shell, bundled in the image. Its command dialect (`show ipv6 ospf6 neighbor`, `configure terminal`) descends from the same industry lineage as the Juniper and Arista CLIs, so fluency here transfers.

*Note: confirm the FRR image tag before starting. Lab 0 pins `quay.io/frrouting/frr:10.6.1` (current stable as of early July 2026); check [quay.io/repository/frrouting/frr](https://quay.io/repository/frrouting/frr?tab=tags) if the pull fails or a newer 10.x stable has shipped.*
