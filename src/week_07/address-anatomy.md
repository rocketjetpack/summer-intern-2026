---
title: "Code Lab: IPv6 Address Anatomy"
---

# Code Lab: IPv6 Address Anatomy

Type any IPv6 address and take it apart: expansion, canonical compression, scope classification, the prefix/interface-ID split at any boundary, and the solicited-node multicast group that [Lab 1](./lab1) watches Neighbor Discovery actually use.

```js
const input = view(Inputs.text({label: "IPv6 address", value: "2001:db8:7:1::10", placeholder: "e.g. fe80::1"}));
const prefixLen = view(Inputs.range([0, 128], {step: 1, value: 64, label: "Prefix length (bits)"}));
```

Some addresses worth pasting in (from this week's lab and the [Basics](./basics) page):

| Try | Why |
|---|---|
| `2001:db8:7:1::10` | host1's address in Lab 1, on the documentation prefix |
| `2001:0db8:0000:0000:0000:0000:0000:0001` | fully expanded; watch the canonical form shrink it |
| `fe80::a8bb:ccff:fedd:eeff` | a link-local with an EUI-64 interface ID (spot the `ff:fe`) |
| `2001:db8:7:f13::` | a /127 point-to-point link address (the OSPFv3 stretch topic wires three of these); set the prefix slider to 127 |
| `ff02::5` | where OSPFv3 hellos go (a stretch-topic preview) |
| `fd12:3456:789a::1` | a ULA |
| `::1` and `::` | the two special ones |

```js
function parseIPv6(str) {
  const s = str.trim().toLowerCase();
  if (s.length === 0) return {error: "Enter an address."};
  if (!/^[0-9a-f:]+$/.test(s)) return {error: "Only hex digits and colons are supported here (embedded IPv4 forms like ::ffff:192.0.2.1 are out of scope for this lab)."};
  const parts = s.split("::");
  if (parts.length > 2) return {error: "\"::\" may appear at most once."};
  let groups;
  if (parts.length === 2) {
    const head = parts[0] === "" ? [] : parts[0].split(":");
    const tail = parts[1] === "" ? [] : parts[1].split(":");
    if (head.length + tail.length > 7) return {error: "Too many groups for a \"::\" to be valid."};
    groups = [...head, ...Array(8 - head.length - tail.length).fill("0"), ...tail];
  } else {
    groups = s.split(":");
    if (groups.length !== 8) return {error: `Found ${groups.length} groups; an address without "::" needs exactly 8.`};
  }
  if (groups.some((g) => g.length === 0 || g.length > 4)) return {error: "Each group needs 1 to 4 hex digits (an empty group means a stray colon)."};
  return {groups: groups.map((g) => parseInt(g, 16))};
}

function toCanonical(groups) {
  let bestStart = -1, bestLen = 0;
  for (let i = 0; i < 8; i++) {
    if (groups[i] !== 0) continue;
    let j = i;
    while (j < 8 && groups[j] === 0) j++;
    if (j - i > bestLen) { bestLen = j - i; bestStart = i; }
    i = j;
  }
  const hex = groups.map((g) => g.toString(16));
  if (bestLen < 2) return hex.join(":");
  const head = hex.slice(0, bestStart).join(":");
  const tail = hex.slice(bestStart + bestLen).join(":");
  return `${head}::${tail}`;
}

function classify(groups) {
  const allZero = groups.every((g) => g === 0);
  if (allZero) return {name: "Unspecified (::)", detail: "The absence of an address; used as the source for Duplicate Address Detection probes.", unicast: false};
  if (groups.slice(0, 7).every((g) => g === 0) && groups[7] === 1) return {name: "Loopback (::1)", detail: "This host talking to itself; the whole of what IPv4 spent 127.0.0.0/8 on.", unicast: false};
  if ((groups[0] & 0xff00) === 0xff00) {
    const known = {"ff02::1": "all nodes on the link", "ff02::2": "all routers on the link", "ff02::5": "all OSPFv3 routers on the link"};
    const c = toCanonical(groups);
    return {name: `Multicast (ff00::/8)${known[c] ? `: ${known[c]}` : ""}`, detail: "IPv6 has no broadcast; well-known groups like these do broadcast's old jobs.", unicast: false};
  }
  if ((groups[0] & 0xffc0) === 0xfe80) return {name: "Link-local (fe80::/10)", detail: "Automatic, mandatory, valid only on its own link; needs a %zone in commands, and serves as OSPFv3's transport and IPv6 routing's usual next-hop.", unicast: true};
  if ((groups[0] & 0xfe00) === 0xfc00) return {name: "Unique local (fc00::/7)", detail: "Private, non-Internet-routable space; the RFC 1918 counterpart.", unicast: true};
  if (groups[0] === 0x2001 && groups[1] === 0x0db8) return {name: "Documentation (2001:db8::/32)", detail: "Reserved for examples by RFC 3849; every address in this week's lab lives here. Never routed on the real Internet.", unicast: true};
  if ((groups[0] & 0xe000) === 0x2000) return {name: "Global unicast (2000::/3)", detail: "The globally routable space; the public-IPv4 counterpart.", unicast: true};
  return {name: "Other / reserved", detail: "Outside the allocations this week covers.", unicast: false};
}

const parsed = parseIPv6(input);
```

```js
{
  if (parsed.error) {
    display(html`<div style="background:#fff3e0;border-left:4px solid #e65100;padding:10px 16px;margin:8px 0;font-family:monospace">${parsed.error}</div>`);
  } else {
    const g = parsed.groups;
    const expanded = g.map((x) => x.toString(16).padStart(4, "0")).join(":");
    const canonical = toCanonical(g);
    const cls = classify(g);
    const addrBig = g.reduce((acc, x) => (acc << 16n) | BigInt(x), 0n);
    const mask = prefixLen === 0 ? 0n : (((1n << BigInt(prefixLen)) - 1n) << BigInt(128 - prefixLen));
    const netBig = addrBig & mask;
    const netGroups = Array.from({length: 8}, (_, i) => Number((netBig >> BigInt(16 * (7 - i))) & 0xffffn));

    let solicited = null;
    if (cls.unicast) {
      const lowByte = g[6] & 0xff;
      solicited = `ff02::1:ff${lowByte.toString(16).padStart(2, "0")}:${g[7].toString(16).padStart(4, "0").replace(/^0+(?=.)/, "")}`;
    }

    const fullChars = Math.floor(prefixLen / 4);
    const partial = prefixLen % 4 !== 0;
    let seen = 0;
    const spans = [];
    for (const [i, x] of g.entries()) {
      if (i > 0) spans.push(html`<span style="color:#999">:</span>`);
      for (const ch of x.toString(16).padStart(4, "0")) {
        const inNet = seen < fullChars;
        const isBoundary = partial && seen === fullChars;
        spans.push(html`<span style="padding:1px 0;background:${inNet ? "#e3f2fd" : isBoundary ? "#fff3e0" : "#f3e5f5"};border-bottom:2px solid ${inNet ? "#1565c0" : isBoundary ? "#e65100" : "#6a1b9a"}">${ch}</span>`);
        seen++;
      }
    }

    display(html`
      <div style="background:#f8f8f8;border-left:4px solid #1565c0;padding:12px 16px;margin:8px 0;font-family:monospace;font-size:0.95em;line-height:1.9">
        Expanded: <strong>${expanded}</strong><br>
        Canonical (RFC 5952): <strong>${canonical}</strong><br>
        Type: <strong>${cls.name}</strong><br>
        <span style="font-size:0.85em;color:#555">${cls.detail}</span><br>
        <span style="font-size:1.15em;letter-spacing:1px">${spans}</span><br>
        <span style="font-size:0.85em"><span style="color:#1565c0">&#9632;</span> network prefix (${prefixLen} bits)
        ${partial ? html` &nbsp;<span style="color:#e65100">&#9632;</span> boundary falls inside this hex digit` : ""}
        &nbsp;<span style="color:#6a1b9a">&#9632;</span> interface identifier (${128 - prefixLen} bits)</span><br>
        Network: <strong>${toCanonical(netGroups)}/${prefixLen}</strong><br>
        ${solicited ? html`Solicited-node multicast group: <strong>${solicited}</strong> <span style="font-size:0.85em;color:#555">(ff02::1:ff + the last 24 bits; the group a Neighbor Solicitation for this address is sent to)</span>` : html`<span style="font-size:0.85em;color:#555">No solicited-node group: only unicast addresses have one.</span>`}
      </div>
    `);
  }
}
```

### Questions

1. Compress `2001:0db8:0000:0000:0001:0000:0000:0001` by hand using the two rules from [IPv6 Basics](./basics), then paste it in. There are two zero runs; which one did the canonical form compress, and why that one?
2. Paste in the link-local address your Lab 1 `host1` actually generated, and confirm the solicited-node group shown here matches the `ff02::1:ff...` entry in `ip -6 maddr show`. Then find that same group in your Step 4 tcpdump capture.
3. Set the prefix slider to 127 on `2001:db8:7:f13::`. How many hex digits belong to the interface ID, and what are the only two addresses this network can ever contain?
4. Why does `ff02::5` report no solicited-node group? Trace the logic: what would it even mean to send a Neighbor Solicitation for a multicast address?
