---
title: "Code Lab: VXLAN MTU & Overhead"
---

# Code Lab: VXLAN MTU & Overhead

Every byte of VXLAN's encapsulation is a byte the underlay has to carry that the tenant never sees. This calculator makes two consequences of that concrete:

1. **The MTU consequence:** if hosts inside the overlay expect a standard 1500-byte IP MTU, the underlay's interfaces need a *larger* MTU to carry the encapsulated result without fragmenting. Get this wrong and small packets (pings, TCP handshakes) work fine while full-size packets silently vanish: one of the classic "the network is haunted" failure modes.
2. **The bandwidth consequence:** the overhead is per-packet, not per-byte, so its cost as a percentage depends entirely on how big the inner packets are.

```js
const innerMtu = view(Inputs.range([576, 9000], {step: 1, value: 1500, label: "Inner (tenant) IP MTU, bytes"}));
const outerIpVersion = view(Inputs.radio(["IPv4", "IPv6"], {value: "IPv4", label: "Underlay IP version"}));
const innerVlanTag = view(Inputs.toggle({label: "Inner frame carries an 802.1Q tag", value: false}));
```

```js
const OUTER_ETH = 14;      // outer Ethernet header (FCS not counted toward MTU)
const OUTER_IP = outerIpVersion === "IPv4" ? 20 : 40;
const OUTER_UDP = 8;
const VXLAN_HDR = 8;
const INNER_ETH = 14 + (innerVlanTag ? 4 : 0);
const encapOverhead = OUTER_IP + OUTER_UDP + VXLAN_HDR + INNER_ETH;   // what the underlay IP MTU must absorb
const wireOverhead = OUTER_ETH + encapOverhead;                        // total extra bytes on the wire
const requiredUnderlayMtu = innerMtu + encapOverhead;
const overheadPct = (wireOverhead / (innerMtu + INNER_ETH + wireOverhead)) * 100;
```

```js
display(html`
  <div style="background:#f8f8f8;border-left:4px solid #1565c0;padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    Encapsulation added per packet: <strong>${wireOverhead} bytes on the wire</strong>
    (${OUTER_ETH} outer Eth + ${OUTER_IP} outer ${outerIpVersion} + ${OUTER_UDP} UDP + ${VXLAN_HDR} VXLAN + ${INNER_ETH} inner Eth)<br>
    Required underlay interface (IP) MTU: <strong>${requiredUnderlayMtu} bytes</strong>
    to carry a ${innerMtu}-byte tenant packet unfragmented<br>
    Worst-case wire overhead at full-size packets: <strong>${overheadPct.toFixed(2)}%</strong>
  </div>
`);
```

The required-MTU number counts only what sits inside the outer IP packet (inner Ethernet + VXLAN + UDP + outer IP): interface MTU is an *IP* MTU, so the outer Ethernet header rides free, the same way it does for any ordinary packet. With the defaults (1500 inner, IPv4 underlay, untagged inner frame) the result is the well-known figure real vendor guides quote: 50 bytes of encapsulation, 1550-byte minimum underlay MTU. Flip the underlay to IPv6 and watch it grow by exactly the 20-byte difference between the IP header sizes, worth noticing given weeks 8-10 build toward an IPv6 deployment.

### Overhead composition

```js
{
  const layers = [
    {name: "Outer Ethernet", bytes: OUTER_ETH, fill: "#cfd8dc"},
    {name: `Outer ${outerIpVersion}`, bytes: OUTER_IP, fill: "#e3f2fd"},
    {name: "Outer UDP", bytes: OUTER_UDP, fill: "#fff3e0"},
    {name: "VXLAN header", bytes: VXLAN_HDR, fill: "#ffebee"},
    {name: "Inner Ethernet", bytes: INNER_ETH, fill: "#e8f5e9"},
    {name: "Inner IP packet (tenant payload)", bytes: innerMtu, fill: "#f3e5f5"},
  ];
  display(Plot.plot({
    title: "One encapsulated frame, to scale",
    width: 680, height: 110,
    marginLeft: 10, marginRight: 10, marginTop: 10, marginBottom: 30,
    x: {label: "bytes"},
    y: {axis: null},
    marks: [
      Plot.barX(layers, {x: "bytes", fill: "fill", stroke: "#333", strokeWidth: 0.8,
        title: (d) => `${d.name}: ${d.bytes}B`}),
    ]
  }));
}
```

### Overhead vs. packet size

The percentage cost of encapsulation isn't a property of VXLAN alone; it's a property of VXLAN *and* the traffic. Sweep the inner packet size and the same fixed overhead swings from negligible to substantial:

```js
{
  const sweep = Array.from({length: 200}, (_, i) => {
    const inner = 64 + i * (9000 - 64) / 199;
    return {inner, pct: (wireOverhead / (inner + INNER_ETH + wireOverhead)) * 100};
  });
  display(Plot.plot({
    width: 680, height: 300,
    marginLeft: 60, marginRight: 20,
    x: {label: "Inner IP packet size (bytes)", domain: [64, 9000]},
    y: {label: "encapsulation overhead (% of wire bytes)", domain: [0, 50]},
    marks: [
      Plot.ruleX([innerMtu], {stroke: "#e53935", strokeDasharray: "4,3"}),
      Plot.line(sweep, {x: "inner", y: "pct", stroke: "#1565c0", strokeWidth: 2.5}),
      Plot.dot([{inner: innerMtu, pct: overheadPct}], {x: "inner", y: "pct", fill: "#e53935", r: 6, stroke: "white", strokeWidth: 2}),
    ]
  }));
}
```

### Questions

1. With defaults set, what underlay MTU does a fabric need to give tenants a clean 1500? Now set the inner MTU to 9000 (tenant jumbo frames): what does the underlay need then, and why do many fabrics simply run the underlay at 9216 and stop thinking about this problem per-tenant?
2. A TCP ACK is roughly a 40-byte inner IP packet. Read its overhead percentage off the sweep chart. Recall from Week 5's lab that one direction of an `iperf3` run is almost entirely ACKs. What does that imply about the *relative* encapsulation cost of the two directions of a single TCP flow crossing a VXLAN fabric?
3. Switch the underlay to IPv6. The required underlay MTU grows by 20 bytes; the tenant's 1500-byte MTU didn't change. Who has to know about this difference: the tenant host's administrator, the VTEP's administrator, or the underlay fabric's administrator?
4. The failure mode described at the top (small packets fine, full-size packets dropped) happens when the underlay MTU is left at 1500 while tenants also use 1500. Using the calculator, how large can a tenant packet actually be before it stops fitting, with an IPv4 underlay at MTU 1500? Would a default `ping` catch the problem? Would `ping -s 1472`?
