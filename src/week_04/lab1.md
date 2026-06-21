---
title: "Lab 1: Loss × Latency Amplification"
---

# Lab 1: Loss × Latency Amplification

The Mathis formula gives TCP throughput a precise shape:

```js
tex.block`\text{throughput} \approx \frac{\text{MSS}}{\text{RTT}} \cdot \frac{C}{\sqrt{p}}`
```

where *MSS* is the maximum segment size (typically 1460 bytes), *RTT* is the round-trip time, *p* is the loss rate (fraction of packets dropped), and *C* ≈ 1.22, the classic constant for Reno-style AIMD (the congestion control Mathis et al. originally modeled). Throughput is inversely proportional to **both** RTT and √p. Their effects multiply.

This lab has two parts. First, explore the formula interactively. Then validate it against real measurements on a ContainerLab topology.

---

## Part A — Interactive Explorer

Move the sliders to explore how loss and latency degrade TCP throughput relative to an unimpaired baseline. Run the baseline test in Step 2 of Part B first, then enter your measured throughput below — the chart normalizes to your actual setup.

> **Why % of baseline, not absolute Mbps?** The Mathis formula was derived for TCP Reno without SACK. Modern Linux enables SACK for all congestion control algorithms, inflating absolute throughput well above what the formula predicts — and by a factor that varies with loss rate, so the gap cannot be corrected with a single constant. What does hold is the *shape*: throughput degrades proportionally to 1/RTT and 1/√p. Expressing measurements as % of an unimpaired baseline makes that shape comparable to the formula's trendline, even when absolute values diverge. Expect your measured data points to sit above the Mathis curve — that gap is SACK at work.

```js
const rttMs = view(Inputs.range([1, 100], {step: 1, value: 20, label: "RTT (ms)"}));
const lossPct = view(Inputs.range([0.0001, 5], {step: 0.0001, value: 0.1, label: "Loss rate (%)"}));
const baselineMbps = view(Inputs.number({label: "Base link speed (Mbps)", value: 1000, step: 1, min: 1}));
```

```js
const MSS = 1460;
const C = 1.22;
const lossRate = lossPct / 100;
const mathisMbps = (MSS * C) / ((rttMs / 1000) * Math.sqrt(lossRate)) * 8 / 1e6;
const mathisPct = Math.min(mathisMbps, baselineMbps) / baselineMbps * 100;
```

```js
display(html`
  <div style="background:#f8f8f8;border-left:4px solid #e53935;padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    Mathis lower bound at <strong>${rttMs}ms</strong> RTT / <strong>${lossPct}%</strong> loss:
    <strong>${mathisMbps.toFixed(1)} Mbps</strong>
    &rarr; <strong>${mathisPct.toFixed(1)}%</strong> of ${baselineMbps.toLocaleString()} Mbps baseline
  </div>
`);
```

### Chart — Throughput degradation vs RTT

The curve shows the Mathis prediction as a percentage of your baseline at the selected loss rate. In the top-left region where the formula predicts more than your baseline, TCP is link-rate limited and the chart shows 100%. Once RTT or loss pushes the Mathis prediction below your baseline, throughput degrades — this is the regime your Part B experiments probe. Your measured data points should follow the same downward slope, sitting above the curve due to SACK.

```js
const regions = [
  {name: "LAN",              x1: 0,  x2: 2,   fill: "#e8f5e9"},
  {name: "Metro",            x1: 2,  x2: 15,  fill: "#e3f2fd"},
  {name: "Regional",         x1: 15, x2: 40,  fill: "#fce4ec"},
  {name: "Continental",      x1: 40, x2: 80,  fill: "#fff3e0"},
  {name: "Intercontinental", x1: 80, x2: 100, fill: "#f3e5f5"},
];
```

```js
{
  const curveData = Array.from({length: 300}, (_, i) => {
    const rtt = 0.2 + i * 99.8 / 299;
    const mathis = (MSS * C) / ((rtt / 1000) * Math.sqrt(lossRate)) * 8 / 1e6;
    return {rtt, pct: Math.min(mathis, baselineMbps) / baselineMbps * 100};
  });
  const dotPoint = [{rtt: rttMs, pct: mathisPct}];

  display(Plot.plot({
    width: 680,
    height: 380,
    marginLeft: 80,
    marginRight: 20,
    x: {label: "RTT (ms)", domain: [0, 100]},
    y: {label: "% of baseline throughput", domain: [0, 105]},
    marks: [
      ...regions.flatMap(r => [
        Plot.rect([r], {x1: "x1", x2: "x2", y1: () => 0, y2: () => 105, fill: "fill", fillOpacity: 0.5}),
        Plot.text([r], {x: d => (d.x1 + d.x2) / 2, y: () => 99, text: "name", fontSize: 10, fill: "#444", textAnchor: "middle"}),
      ]),
      Plot.ruleY([50], {stroke: "#aaa", strokeDasharray: "5,3"}),
      Plot.text([{x: 98, y: 50, t: "50%"}], {x: "x", y: "y", text: "t", fontSize: 10, fill: "#888", textAnchor: "end", dy: -6}),
      Plot.line(curveData, {x: "rtt", y: "pct", stroke: "#1565c0", strokeWidth: 2.5}),
      Plot.ruleX([rttMs], {stroke: "#e53935", strokeWidth: 1.5, strokeDasharray: "4,3"}),
      Plot.dot(dotPoint, {x: "rtt", y: "pct", fill: "#e53935", r: 7, stroke: "white", strokeWidth: 2}),
      Plot.tip(dotPoint, {x: "rtt", y: "pct",
        title: d => `RTT: ${d.rtt}ms\nLoss: ${lossPct}%\nMathis: ${d.pct.toFixed(1)}% of baseline`}),
    ]
  }));
}
```

### Questions — answer before running the experiments

1. Set loss to 0.1% and move the RTT slider from 10ms to 100ms (10×). By what factor does the Mathis % drop? The 1/RTT term predicts exactly 10×. Does the chart confirm this?

2. Hold RTT at 20ms and increase loss from 0.1% to 1.0% (10× more loss). Loss appears under a square root, so you expect only √10 ≈ 3.2× degradation, not 10×. Does the chart confirm this?

3. Move to 100ms RTT and 1% loss — 10× on both axes from 10ms / 0.1%. The formula predicts the penalties multiply: 10 × √10 ≈ 31×. Is that what you see? Why does this matter when adding latency to an already-lossy path?

---

## Part B — ContainerLab Experiments

### Step 0: Prepare

```bash
mkdir -p $HOME/container-lab/week04/lab1
cd $HOME/container-lab/week04/lab1
```

### Step 1: Write the topology and deploy

```yaml
# lab1.clab.yml
name: week04-lab1
topology:
  nodes:
    sender:
      kind: linux
      image: nettools:week04
      exec:
        - ip addr add 10.4.0.1/24 dev eth1
        - tc qdisc replace dev eth1 root netem rate 1gbit
    receiver:
      kind: linux
      image: nettools:week04
      exec:
        - ip addr add 10.4.0.2/24 dev eth1
        - tc qdisc replace dev eth1 root netem rate 1gbit
  links:
    - endpoints: ["sender:eth1", "receiver:eth1"]
```

*Note: If we don't set a fixed rate of 1 Gbit via `tc` the resulting baseline throughput measured by `iperf3` will be roughly host memory transfer speed, likely 50 Gbps or higher.*

```bash
containerlab deploy -t lab1.clab.yml
docker exec -d clab-week04-lab1-receiver iperf3 -s
```

### Step 2: Measure the baseline (T₀)

With both container interfaces capped at 1 Gbps and no simulated RTT or loss rate, run `iperf3` test using the Reno congestion control algorithm. 

*Note: This algorithm is used because the original Mathis formula was created using Reno. Modern Reno and TCP behavior is significantly better than what Mathis uses, other algorithms like CUBIC and BBR will make the divergence from Mathis even more notable.*

```bash
docker exec -it clab-week04-lab1-sender iperf3 -c 10.4.0.2 -t 30 -i 5 -C reno
```

With these arguments `iperf3` will connect to the server you started above and run a single-flow bandwidth test for 30 seconds using the Reno congestion control algorithm. It will also print progress output every 5 seconds. When the run completes, it will print final information from both the sender and receiver's numbers, which may be subtly different. For your records, only pay attention to the sender.

Record: **T₀ = \_\_\_\_\_ Mbps** → enter this in the "Your measured baseline" field in Part A now.

### Step 3: RTT sweep at 0.1% loss

Apply impairment symmetrically: each container's `eth1` gets half the target RTT and the full loss rate. This models a symmetric link where both data packets and ACKs are independently subject to delay and loss.

For your first measurement, do the following to simulate 10ms of RTT and 0.1% loss: 

**10ms RTT, 0.1% loss:**
```bash
docker exec clab-week04-lab1-sender   tc qdisc replace dev eth1 root netem delay 5ms loss 0.1%
docker exec clab-week04-lab1-receiver tc qdisc replace dev eth1 root netem delay 5ms loss 0.1%
docker exec clab-week04-lab1-sender iperf3 -c 10.4.0.2 -t 30 -i 5 -C reno
```

Repeat the above testing at RTT's of 20ms, 50ms, and 100ms (all at 0.1% loss) and record them in the table below..

### Step 4: RTT sweep at 1% loss

Repeat the same four RTT values with 10× more loss. For example:

**10ms RTT, 1% loss:**
```bash
docker exec clab-week04-lab1-sender   tc qdisc replace dev eth1 root netem delay 5ms loss 1%
docker exec clab-week04-lab1-receiver tc qdisc replace dev eth1 root netem delay 5ms loss 1%
docker exec clab-week04-lab1-sender iperf3 -c 10.4.0.2 -t 30 -i 5 -C reno
```

Record values for the same RTT's (all now at 1% loss) in the table below.

### Step 5: Record and plot your results

Type each measured throughput into the table — the chart updates live as you type.

```js
const scenarios = [
  {rtt: 10,  loss: 0.1},
  {rtt: 20,  loss: 0.1},
  {rtt: 50,  loss: 0.1},
  {rtt: 100, loss: 0.1},
  {rtt: 10,  loss: 1.0},
  {rtt: 20,  loss: 1.0},
  {rtt: 50,  loss: 1.0},
  {rtt: 100, loss: 1.0},
];

function makeResultsTable(scenarios) {
  const inputs = scenarios.map(() => {
    const el = document.createElement("input");
    el.type = "number";
    el.step = "0.1";
    el.min = "0";
    el.placeholder = "—";
    el.style.cssText = "width:88px;padding:3px 6px;border:1px solid #ccc;border-radius:3px;font-size:0.9em";
    return el;
  });

  const container = document.createElement("div");
  const table = document.createElement("table");
  table.style.cssText = "border-collapse:collapse;max-width:520px;font-size:0.9em;margin-bottom:4px";

  const thead = table.createTHead();
  const hrow = thead.insertRow();
  ["#", "RTT", "Loss", "Measured (Mbps)"].forEach(text => {
    const th = document.createElement("th");
    th.textContent = text;
    th.style.cssText = "text-align:left;padding:5px 14px;border-bottom:2px solid #ddd;font-size:0.8em;text-transform:uppercase;letter-spacing:0.04em;color:#666";
    hrow.appendChild(th);
  });

  const tbody = table.createTBody();
  scenarios.forEach((s, i) => {
    const row = tbody.insertRow();
    row.style.background = i < 4 ? "#eef3ff" : "#fff3f3";
    if (i === 4) row.style.borderTop = "2px solid #ddd";
    [String(i + 1), `${s.rtt} ms`, `${s.loss}%`, inputs[i]].forEach((val, j) => {
      const td = row.insertCell();
      td.style.padding = "4px 14px";
      if (j === 3) { td.appendChild(val); }
      else {
        td.textContent = val;
        if (j === 0) td.style.color = "#bbb";
        if (j === 1) td.style.fontWeight = "600";
      }
    });
  });

  container.appendChild(table);
  Object.defineProperty(container, "value", {
    get() { return inputs.map(el => el.value === "" ? null : +el.value); }
  });
  inputs.forEach(el =>
    el.addEventListener("input", () => container.dispatchEvent(new Event("input", {bubbles: true})))
  );
  return container;
}

const measurements = view(makeResultsTable(scenarios));
```

```js
{
  // MSS and C are defined in Part A's module scope
  const computeMathis = (rtt, loss) =>
    (MSS * C) / ((rtt / 1000) * Math.sqrt(loss / 100)) * 8 / 1e6;

  const rttLine = Array.from({length: 300}, (_, i) => 0.5 + i * 99.5 / 299);

  const mathisCurves = [
    ...rttLine.map(r => ({rtt: r, mbps: computeMathis(r, 0.1), series: "0.1% loss"})),
    ...rttLine.map(r => ({rtt: r, mbps: computeMathis(r, 1.0), series: "1% loss"})),
  ];

  const measuredData = scenarios
    .map((s, i) => ({
      ...s,
      mbps: measurements[i],
      series: s.loss === 0.1 ? "0.1% loss" : "1% loss"
    }))
    .filter(d => d.mbps !== null && d.mbps > 0);

  display(Plot.plot({
    width: 680,
    height: 390,
    marginLeft: 72,
    subtitle: "Dashed curves = Mathis formula (no SACK lower bound) · dots/squares = your measurements",
    color: {
      domain: ["0.1% loss", "1% loss"],
      range: ["steelblue", "firebrick"],
      legend: true
    },
    x: {label: "RTT (ms)", domain: [0, 105]},
    y: {label: "Throughput (Mbps)", type: "log"},
    marks: [
      Plot.line(mathisCurves, {
        x: "rtt", y: "mbps", stroke: "series", z: "series",
        strokeWidth: 2, strokeDasharray: "7,4"
      }),
      Plot.dot(measuredData, {
        x: "rtt", y: "mbps", fill: "series",
        symbol: d => d.series === "0.1% loss" ? "circle" : "square",
        r: 6, stroke: "white", strokeWidth: 1.5
      }),
      Plot.text(measuredData, {
        x: "rtt", y: "mbps",
        text: d => String(Math.round(d.mbps)),
        fill: d => d.series === "0.1% loss" ? "steelblue" : "firebrick",
        dx: 10, dy: 2, fontSize: 11
      })
    ]
  }));
}
```

*What to look for:*
- Your measured points sit **above** the Mathis trendlines at every RTT — that vertical offset is the SACK benefit.
- The **downward slope** is the key test: as RTT doubles, throughput should roughly halve. Does your 0.1% series confirm a ~2× drop from 10ms to 20ms?
- The **gap between series**: Mathis predicts the 1% curve sits √10 ≈ 3.2× below the 0.1% curve. Your measured ratio may be larger — SACK's benefit shrinks proportionally at higher loss rates, widening the apparent gap.

### Step 6: Compare Reno, CUBIC, and BBR

The 100ms / 1% impairment from Step 4 is still applied. Run the same scenario with CUBIC and BBR without changing the tc rules.

```bash
docker exec clab-week04-lab1-sender sysctl net.ipv4.tcp_available_congestion_control

# CUBIC: cuts window by 30%, cubic recovery curve
docker exec clab-week04-lab1-sender iperf3 -c 10.4.0.2 -t 30 -i 5 -C cubic

# BBR: estimates bandwidth and RTT directly, ignores loss events
docker exec clab-week04-lab1-sender iperf3 -c 10.4.0.2 -t 30 -i 5 -C bbr
```

| Algorithm | Measured (Mbps) | % of T₀ | Ratio vs Reno |
|-----------|-----------------|---------|---------------|
| Reno (Step 4, row 8) | | | 1× |
| CUBIC | | | |
| BBR | | | |

netem applies random loss that is not correlated with actual queue congestion. BBR ignores loss as a signal and estimates bandwidth from RTT and delivery rate instead. Does your measurement reflect that difference?

### Step 7: Clean up

```bash
containerlab destroy -t lab1.clab.yml --cleanup
```

### Bonus challenge if you want

`iperf3` can be used between your workstation and the containerlab host (though we will need to make a firewall rule on the containerlab host to allow the port). What is the result of testing the connection, and how does it relate to the speed of your workstations connection and the RTT time to the containerlab host?

---

## Week 8 Connection

> RDMA (Remote Direct Memory Access) has no retransmit path at the transport layer. Any packet loss means an RDMA operation either stalls indefinitely or is failed back to the application to handle. This is why the requirement for any RDMA network (InfiniBand or Ethernet) is not "low loss", it is *zero loss*.
>
> The scale of the problem is visible in the formula. On a 10 Gbps link at 1ms RTT, a single TCP flow at just 1% loss achieves only **~142 Mbps** — 1.4% of link capacity. Loss rates that feel negligible to a network engineer are catastrophic at high speeds.

