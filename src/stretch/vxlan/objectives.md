---
title: Objectives
---

# VXLAN & Overlay Networking: Objectives

*Note: this stretch topic turns back up the stack from Week 6's physical layer to L2/L3. Weeks 3-6 assumed the underlay (the physical, IP-routed fabric) and the broadcast domain a host lives on were basically the same thing. This topic breaks that assumption on purpose.*

By the end of the week you should be able to:

- **Explain the problem VXLAN exists to solve.**
  Two constraints on traditional VLANs stop scaling once a data center gets big enough:
  - **VLAN ID space is 12 bits.** 802.1Q reserves values 0 and 4095, leaving 4094 usable VLAN IDs, total, for an entire fabric. A cloud or multi-tenant environment with more than 4094 tenants (or more than 4094 things that need L2 isolation) simply runs out of IDs.
  - **L2 domains don't route.** Stretching a VLAN across multiple racks/rows historically meant stretching Spanning Tree across them too, with all the convergence-time and blast-radius problems that implies. Weeks 3-4's ECMP/Clos fabrics work specifically *because* the fabric is L3-routed, not one big L2 domain.

  VXLAN's answer to both: keep the physical fabric a clean, boring, L3-routed IP network (the **underlay**), and build the L2 domains tenants actually need as tunnels riding on top of it (the **overlay**). The tenant's Ethernet frame never actually touches the underlay's routing tables; it rides inside a UDP packet that does.

  *Questions to consider:*
  - If the underlay is "just" IP-routed, what do ECMP and Clos topology (Week 4) buy an overlay design, that a single non-redundant L2 path wouldn't?
  - 4094 VLANs sounds like a lot. What kind of environment runs out of it first: a single company's data center, or a public cloud provider hosting thousands of tenants?

- **Describe MAC-in-UDP encapsulation and identify each layer in a VXLAN frame.**
  VXLAN ([RFC 7348](https://datatracker.ietf.org/doc/html/rfc7348)) takes an entire original Ethernet frame, header and all, and wraps it inside a UDP packet. Nothing about the original frame changes; a device receiving it and stripping the outer layers gets back byte-for-byte what went in.

  ```js
  const vxlanLayers = [
    {name: "Outer Ethernet", bytes: 14, color: "#cfd8dc", detail: "underlay next-hop MACs"},
    {name: "Outer IP", bytes: 20, color: "#e3f2fd", detail: "VTEP source -> VTEP dest (underlay-routable)"},
    {name: "Outer UDP", bytes: 8, color: "#fff3e0", detail: "src port = hash of inner frame (for ECMP entropy), dst port = 4789"},
    {name: "VXLAN Header", bytes: 8, color: "#ffebee", detail: "flags + 24-bit VNI"},
    {name: "Inner Ethernet", bytes: 14, color: "#e8f5e9", detail: "original frame's real src/dst MAC"},
    {name: "Inner Payload", bytes: 1486, color: "#f3e5f5", detail: "the original frame's IP packet, unmodified"},
  ];
  ```

  ```js
  Plot.plot({
    title: "A VXLAN frame carrying a standard 1500-byte inner frame",
    width: 680, height: 130,
    marginLeft: 10, marginRight: 10, marginTop: 10, marginBottom: 30,
    x: {axis: null},
    y: {axis: null, domain: [0, 1]},
    marks: [
      Plot.barX(vxlanLayers, {x: "bytes", fill: "color", stroke: "#333", strokeWidth: 1,
        title: (d) => `${d.name}: ${d.bytes}B\n${d.detail}`}),
      Plot.textX(vxlanLayers, {x: "bytes", text: (d) => d.bytes >= 40 ? `${d.name}\n${d.bytes}B` : "", frameAnchor: "middle", lineAnchor: "middle", fontSize: 10}),
    ]
  })
  ```

  Hover each segment above for what it carries. Two fields matter more than the rest: the outer **destination IP** is the remote VTEP's address, not the original frame's destination, which is why this whole scheme works over a plain routed IP fabric with zero awareness that VXLAN exists. And the **VNI** (VXLAN Network Identifier) inside the VXLAN header is 24 bits, giving over 16 million possible segments, against VLAN's 4094.

  *Questions to consider:*
  - The outer UDP source port is described above as "a hash of the inner frame," not a fixed value. Given Week 4's ECMP discussion, why would a VXLAN implementation want that port to vary per-flow rather than using one fixed source port for every packet?
  - The total overhead added here is 14+20+8+8 = 50 bytes. If a host's NIC is configured for a standard 1500-byte MTU, what does that imply about the MTU the *underlay* interfaces need to support instead? (The [Code Lab](./vni-overhead) makes this exact question concrete.)

- **Explain the VTEP's job: encapsulate on the way in, decapsulate on the way out.**
  A VTEP (VXLAN Tunnel Endpoint) is the device that sits at the boundary between a tenant's real, untagged Ethernet segment and the IP underlay. It has two distinct sides:
  - **Access side:** a normal Ethernet port (or a specific VLAN on one), where it looks and acts like an ordinary switch port to whatever's plugged into it.
  - **Network side:** an IP address on the underlay, used as the source/destination for VXLAN-encapsulated UDP traffic to/from other VTEPs.

  When a frame arrives on the access side destined for a MAC the VTEP knows lives behind a remote VTEP, it wraps the frame in VXLAN/UDP/IP addressed to that remote VTEP's underlay IP and sends it into the fabric like any other IP packet. The remote VTEP receives it, strips every outer layer, and delivers the original, untouched frame out its own access side. Neither host on either end knows any of this happened; from their point of view, they're on the same wire.

  *Questions to consider:*
  - A VTEP's network-side address is usually a loopback/anycast-style address reachable via multiple physical uplinks, not the IP of a single physical interface. Given Week 4's ECMP discussion, why would that be a deliberate choice rather than an implementation detail?

- **Explain flood-and-learn: how a VTEP builds its MAC table without a control plane.**
  Before VXLAN's overlay MAC table has any entries, a VTEP receiving a frame for an unknown destination MAC has exactly the same problem an ordinary Ethernet switch has on power-up: it doesn't know which port (or, here, which remote VTEP) that MAC lives behind. **Flood-and-learn** is the classic answer, just extended across the tunnel:
  - **Flood:** an unknown-destination frame (along with genuine broadcast and multicast frames, collectively "BUM" traffic: Broadcast, Unknown-unicast, Multicast) gets replicated to *every* other VTEP that's part of the same VNI. Without IP multicast in the underlay (common in practice, and the case in this topic's lab), that replication is done by the sending VTEP itself, called **head-end replication**: a static list of "flood to these remote VTEP IPs" entries, checked one by one.
  - **Learn:** when a reply comes back, the receiving VTEP now knows the *source* MAC of that frame and the *remote VTEP IP* it arrived from (that's all it can observe: the outer IP source address of the VXLAN packet). It caches `(MAC) -> (remote VTEP IP)` in its local forwarding database (FDB), the same way an Ethernet switch caches `(MAC) -> (port)`. The next frame to that MAC gets unicast directly to the right remote VTEP; no more flooding needed for that destination.

  This is genuinely just Ethernet's original learning-bridge algorithm, with "port" replaced by "remote VTEP IP address." Nothing here needs a routing protocol, BGP, or any control-plane exchange between VTEPs at all, which is exactly why it's cheap to stand up, and exactly what [Lab 1](./lab1) has you watch happen in real time via `bridge fdb show`.

  *Questions to consider:*
  - A new host, freshly plugged into `host1`'s network, sends its very first packet: an ARP request, which is broadcast. Trace what every VTEP in the VNI does with that one frame, assuming none of them have learned anything yet.
  - Flood-and-learn has no way to detect a MAC that's moved or gone stale except waiting for its FDB entry to age out. What real operational problem could that cause in a network where VMs migrate between hosts frequently?

- **(Preview, not a lab here) Explain what EVPN replaces flood-and-learn with, and why.**
  Flood-and-learn has a real cost: every BUM frame gets replicated to every VTEP in the VNI, whether or not they have any host that actually needs it, and MAC learning only happens reactively, after traffic has already flowed. **EVPN** ([RFC 7432](https://datatracker.ietf.org/doc/html/rfc7432)) replaces the data-plane learning step with a control-plane one: VTEPs use BGP (a new address family, MP-BGP EVPN) to *advertise* MAC and IP reachability directly to each other, the same way BGP advertises route reachability. A VTEP that's never seen a single packet for some MAC can already know exactly which remote VTEP it lives behind, because BGP told it so, up front, before any BUM flooding was ever needed.

  This is intentionally left conceptual for now. Weeks 8-10 build up BGP from fundamentals through to a real production deployment, and EVPN is a genuinely natural place that arc could extend to afterward: the same VNI/VTEP vocabulary from this topic, with BGP doing the job flood-and-learn does here.

  *Questions to consider:*
  - Flood-and-learn's flooding cost scales with how many VTEPs share a VNI. Does EVPN's BGP-advertisement cost scale the same way, or differently? What would make you expect one to scale better than the other in a fabric with hundreds of VTEPs?

---

## Putting It Together

Every previous week quietly assumed a host's L2 broadcast domain was a physical, local fact about which cable it's plugged into. This topic breaks that assumption on purpose: VXLAN turns "which broadcast domain am I in" into a tunneling decision made by a VTEP, completely decoupled from the underlay's physical/routed topology underneath it. The oversubscription and ECMP fabric-design trade-offs from Week 4, and the physical link capacity Week 6 measured, are exactly what this overlay rides on top of. VXLAN doesn't add any capacity to the fabric, it changes how many independent tenants' L2 domains can share the capacity that's already there.

## The Weeks 8-10 Bridge

Flood-and-learn works, and it's genuinely how a lot of real VXLAN deployments run. But it has no control plane: MAC reachability is only ever learned reactively, from traffic that already flowed, and nothing here has any concept of policy, filtering, or authenticated peer relationships. Weeks 8-10 build up BGP from the ground up (first in ContainerLab, then live on the production Juniper connection), and BGP is exactly the tool EVPN reaches for to replace flood-and-learn's reactive learning with an advertised one. You won't be building EVPN in Weeks 8-10, but every BGP concept you pick up there (peering, address families, route advertisement, policy) is the same vocabulary EVPN uses to solve the problem this topic left as a preview.
