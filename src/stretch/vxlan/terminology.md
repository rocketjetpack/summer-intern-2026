---
title: Terminology
---

# VXLAN: Terminology

| Term / Acronym | Definition |
|---|---|
| **BUM Traffic** | Broadcast, Unknown-unicast, Multicast: the categories of traffic that can't be forwarded to a single known destination and must instead be flooded |
| **Data Plane Learning** | MAC learning derived from observing actual traffic (flood-and-learn), rather than from a control-plane protocol advertising reachability |
| **EVPN** | Ethernet VPN ([RFC 7432](https://datatracker.ietf.org/doc/html/rfc7432)): uses MP-BGP to advertise MAC/IP reachability between VTEPs directly, replacing flood-and-learn's reactive, data-plane-driven learning |
| **FDB** | Forwarding Database: a bridge's table of learned `MAC -> port` (or, for a VXLAN bridge, `MAC -> remote VTEP IP`) entries; inspected with `bridge fdb show` |
| **Flood-and-Learn** | The classic Ethernet learning-bridge algorithm: flood traffic to an unknown destination everywhere, then learn the source MAC's real location from whatever reply comes back |
| **Head-End Replication** | Unicast-based BUM replication: instead of relying on underlay IP multicast, the sending VTEP itself maintains a list of remote VTEPs and sends a separate copy of the flooded frame to each one |
| **MAC-in-UDP** | VXLAN's encapsulation strategy: an entire original Ethernet frame is carried, unmodified, as the payload of a UDP packet |
| **Overlay** | The logical, tunneled L2 (or L3) network that tenants/hosts actually see; built on top of the underlay, independent of its physical topology |
| **Underlay** | The physical, L3-routed IP fabric that VXLAN traffic actually transits; has no awareness that VXLAN is running on top of it |
| **VNI** | VXLAN Network Identifier: the 24-bit field in the VXLAN header that scopes a frame to one overlay segment, analogous to a VLAN ID but with ~16.7 million possible values instead of 4094 |
| **VTEP** | VXLAN Tunnel Endpoint: the device that encapsulates frames entering the overlay and decapsulates frames leaving it; has an access side (plain Ethernet) and a network side (underlay IP) |
| **VXLAN** | Virtual eXtensible LAN ([RFC 7348](https://datatracker.ietf.org/doc/html/rfc7348)): a MAC-in-UDP encapsulation standard for building L2 overlay networks on top of an L3-routed underlay |
| **VXLAN Header** | The 8-byte header VXLAN inserts between the outer UDP header and the original (inner) Ethernet frame; carries flags and the 24-bit VNI |
| **VXLAN Port (4789)** | The IANA-assigned UDP destination port for VXLAN. Linux's `ip link add type vxlan` still defaults to the pre-standardization port **8472** for backward compatibility; it must be set explicitly with `dstport 4789` to interoperate with non-Linux VTEPs |

*Note: this list intentionally does not include multicast-based BUM replication in the underlay. This topic's lab uses head-end replication (a static unicast flood list) instead, which is what a real fabric without PIM/IGMP support in the underlay would also use.*
