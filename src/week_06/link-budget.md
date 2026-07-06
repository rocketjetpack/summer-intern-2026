---
title: "Code Lab: Link Power Budget"
---

# Code Lab: Link Power Budget (Needs More Work)

A link "closes" when enough light survives the trip from transmitter to receiver: not too little (below receiver sensitivity), and not so much it saturates the receiver either, though that second failure mode rarely comes up over real distances. Following [The FOA's loss budget method](./resources), the calculation is just subtraction in the logarithmic dB domain:

```js
tex.block`\text{Link Margin} = \underbrace{(P_{tx} - P_{rx})}_{\text{dynamic range}} - \underbrace{(L \cdot \alpha + n_c \cdot \ell_c + n_s \cdot \ell_s)}_{\text{total passive loss}} - M_{\text{safety}}`
```

where *P<sub>tx</sub>* is transmit launch power (dBm), *P<sub>rx</sub>* is receiver sensitivity (dBm), *L* is fiber length (km), *α* is fiber attenuation (dB/km), *n<sub>c</sub>* and *ℓ<sub>c</sub>* are the connector count and per-connector loss, and *n<sub>s</sub>* and *ℓ<sub>s</sub>* are the splice count and per-splice loss. *M<sub>safety</sub>* is a safety margin held back for aging, bend loss, and manufacturing tolerance. Positive result, the link should work. Zero or negative, it won't, no matter how correct everything above the physical layer is.

*Note: the default transmit power and receiver sensitivity values below are illustrative, representative of common short/long-reach optics, not pulled from any one vendor's datasheet. Use the actual transceiver's datasheet numbers for a real link design.*

---

## Calculator

```js
const fiberType = view(Inputs.select(
  new Map([
    ["Multimode (OM3/OM4/OM5, 850nm): α ≈ 3.0 dB/km", 3.0],
    ["Single-mode (OS2, 1310nm): α ≈ 0.4 dB/km", 0.4],
    ["Single-mode (OS2, 1550nm): α ≈ 0.3 dB/km", 0.3],
  ]),
  {label: "Fiber type"}
));
```

```js
const length = view(Inputs.range([0, 80], {step: 0.1, value: 0.5, label: "Fiber length (km)"}));
const txPower = view(Inputs.number({label: "Tx launch power (dBm)", value: -2, step: 0.1}));
const rxSensitivity = view(Inputs.number({label: "Rx sensitivity (dBm)", value: -11, step: 0.1}));
const nConnectors = view(Inputs.number({label: "Connector pairs", value: 2, step: 1, min: 0}));
const connectorLoss = view(Inputs.number({label: "Loss per connector pair (dB)", value: 0.5, step: 0.05, min: 0}));
const nSplices = view(Inputs.number({label: "Splices", value: 0, step: 1, min: 0}));
const spliceLoss = view(Inputs.number({label: "Loss per splice (dB)", value: 0.3, step: 0.05, min: 0}));
const safetyMargin = view(Inputs.number({label: "Safety margin (dB)", value: 3, step: 0.5, min: 0}));
```

```js
const fiberLoss = length * fiberType;
const connectorTotal = nConnectors * connectorLoss;
const spliceTotal = nSplices * spliceLoss;
const totalPassiveLoss = fiberLoss + connectorTotal + spliceTotal;
const dynamicRange = txPower - rxSensitivity;
const netMargin = dynamicRange - totalPassiveLoss - safetyMargin;
const closes = netMargin >= 0;
```

```js
display(html`
  <div style="background:${closes ? "#f1f8e9" : "#ffebee"};border-left:4px solid ${closes ? "#558b2f" : "#c62828"};padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    Dynamic range (Tx &minus; Rx sensitivity): <strong>${dynamicRange.toFixed(2)} dB</strong><br>
    Total passive loss (fiber + connectors + splices): <strong>${totalPassiveLoss.toFixed(2)} dB</strong>
    &nbsp;(fiber ${fiberLoss.toFixed(2)} + connectors ${connectorTotal.toFixed(2)} + splices ${spliceTotal.toFixed(2)})<br>
    Safety margin held back: <strong>${safetyMargin.toFixed(2)} dB</strong><br>
    <strong>Net link margin: ${netMargin.toFixed(2)} dB (${closes ? "link closes" : "link does NOT close"})</strong>
  </div>
`);
```

### Chart — margin vs. distance

```js
{
  const maxLen = Math.max(80, length * 1.3);
  const curveData = Array.from({length: 200}, (_, i) => {
    const l = (i / 199) * maxLen;
    const margin = dynamicRange - (l * fiberType + connectorTotal + spliceTotal) - safetyMargin;
    return {l, margin};
  });
  const dotPoint = [{l: length, margin: netMargin}];

  display(Plot.plot({
    width: 680,
    height: 380,
    marginLeft: 60,
    marginRight: 20,
    x: {label: "Fiber length (km)", domain: [0, maxLen]},
    y: {label: "Net link margin (dB)"},
    marks: [
      Plot.ruleY([0], {stroke: "#666", strokeWidth: 1.5, strokeDasharray: "2,2"}),
      Plot.line(curveData, {x: "l", y: "margin", stroke: "#1565c0", strokeWidth: 2}),
      Plot.dot(dotPoint, {x: "l", y: "margin", fill: closes ? "#558b2f" : "#c62828", r: 7, stroke: "white", strokeWidth: 2}),
      Plot.tip(dotPoint, {x: "l", y: "margin",
        title: d => `Length: ${length.toFixed(1)} km\nMargin: ${d.margin.toFixed(2)} dB`}),
    ]
  }));
}
```

Everything else stays fixed while the curve sweeps distance, so you can see where *this* configuration's margin crosses zero: in other words, the farthest this link could reach before you'd need to switch fiber type, cut down the connector count, or pick a different transceiver.

### Questions

1. Switch the fiber type from single-mode (1310nm) to multimode while keeping distance at 2km. How much margin does that cost, and does the link still close?
2. Hold multimode fixed and drag the distance slider up. Around what distance does the link stop closing? Does that match your intuition for why multimode fiber stays a short-reach, in-datacenter technology rather than something you'd run between sites?
3. Set connector pairs to 6 (a patch panel at every row, as in the objectives' question) instead of 2. How much margin does that cost compared to a direct run with 2 connectors?
4. This calculator assumes clean, linear dB math with no amplification. Week 7's long-haul DWDM links cover distances where fiber loss alone would exceed any transmitter's launch power by 10-20x. What does that tell you about what a long-haul link has to add that this calculator doesn't model?
