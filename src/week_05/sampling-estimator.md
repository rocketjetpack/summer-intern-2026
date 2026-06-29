---
title: "Code Lab: Sampling Estimator"
---

# Code Lab: Sampling Estimator

sFlow's packet sampling is a [Bernoulli process](https://en.wikipedia.org/wiki/Bernoulli_process): out of *K* true packets, each one is independently selected with probability *p* = 1/*N*. The number of samples actually observed, *S*, is binomially distributed, and the standard estimator for the true count is:

```js
tex.block`\hat{K} = S \cdot N`
```

This estimator is unbiased, but it has variance — for a 1-in-*N* sample of *K* true packets, the standard error of the estimate works out to approximately:

```js
tex.block`\text{SE}(\hat{K}) \approx \sqrt{N \cdot K}`
```

which means the **relative** error (the error as a fraction of the true count) is:

```js
tex.block`\frac{\text{SE}(\hat{K})}{K} \approx \sqrt{\frac{N}{K}}`
```

Two things fall out of that formula directly: relative error shrinks as the sampling rate gets denser (smaller *N*), and — for a *fixed* sampling rate — relative error also shrinks as the true flow gets bigger (larger *K*). A small flow sampled at 1-in-1000 can have enormous relative error; a flow 1000× larger sampled at the same rate is far more reliable. This is exactly what [Lab 1](./lab1) asks you to predict before measuring.

---

## Estimator

```js
const N = view(Inputs.range([1, 10000], {step: 1, value: 100, label: "Sampling rate (1-in-N)"}));
const K = view(Inputs.number({label: "True packet count (K)", value: 100000, step: 1, min: 1}));
```

```js
const expectedSamples = K / N;
const se = Math.sqrt(N * K);
const relErrorPct = Math.sqrt(N / K) * 100;
const khat = expectedSamples * N; // == K in expectation; real runs will deviate
const ciLow = Math.max(0, khat - 1.96 * se);
const ciHigh = khat + 1.96 * se;
```

```js
display(html`
  <div style="background:#f8f8f8;border-left:4px solid #1565c0;padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
    At 1-in-<strong>${N}</strong> sampling of <strong>${K.toLocaleString()}</strong> true packets:<br>
    Expected samples observed: <strong>${expectedSamples.toFixed(1)}</strong><br>
    Standard error of the estimate: <strong>&plusmn;${se.toLocaleString(undefined, {maximumFractionDigits: 0})}</strong> packets
    (<strong>${relErrorPct.toFixed(2)}%</strong> relative)<br>
    Approximate 95% confidence interval: <strong>${ciLow.toLocaleString(undefined, {maximumFractionDigits: 0})}</strong> &ndash;
    <strong>${ciHigh.toLocaleString(undefined, {maximumFractionDigits: 0})}</strong> packets
  </div>
`);
```

### Chart — relative error vs. sampling rate

```js
const seriesK = [1e3, 1e5, 1e7];
```

```js
{
  const curveData = seriesK.flatMap(k =>
    Array.from({length: 200}, (_, i) => {
      const n = Math.exp(Math.log(1) + i * (Math.log(10000) - Math.log(1)) / 199);
      return {n, pct: Math.sqrt(n / k) * 100, series: `K = ${k.toLocaleString()}`};
    })
  );
  const dotPoint = [{n: N, pct: relErrorPct}];

  display(Plot.plot({
    width: 680,
    height: 380,
    marginLeft: 70,
    marginRight: 20,
    x: {label: "Sampling rate (1-in-N)", type: "log", domain: [1, 10000]},
    y: {label: "Relative error (%)", type: "log"},
    color: {legend: true},
    marks: [
      Plot.line(curveData, {x: "n", y: "pct", stroke: "series", z: "series", strokeWidth: 2}),
      Plot.ruleX([N], {stroke: "#e53935", strokeWidth: 1.5, strokeDasharray: "4,3"}),
      Plot.dot(dotPoint, {x: "n", y: "pct", fill: "#e53935", r: 7, stroke: "white", strokeWidth: 2}),
      Plot.tip(dotPoint, {x: "n", y: "pct",
        title: d => `N: 1-in-${N}\nK: ${K.toLocaleString()}\nRelative error: ${d.pct.toFixed(2)}%`}),
    ]
  }));
}
```

The three curves hold *K* fixed at three sizes spanning small to large flows; your current *K* slider value sits somewhere among (or beyond) them — the red marker tracks your exact `(N, K)` choice.

### Questions

1. Hold *K* at 100,000 and move *N* from 10 to 1000 (100× sparser sampling). The formula predicts relative error grows by exactly √100 = 10×. Does the chart confirm this?

2. Hold *N* at 100 and increase *K* from 1,000 to 1,000,000 (1000× more traffic). Relative error should *shrink* by √1000 ≈ 31.6×, even though the sampling rate didn't change. Why does a bigger flow get a *more* reliable estimate at the same sampling rate?

3. Set *K* to a small value (e.g. 500) at *N* = 1000. What does the confidence interval look like? What does this tell you about sFlow's ability to see a single small flow that happens to be hiding inside a much larger traffic mix — the same kind of blind spot Week 4 raised about SNMP's polling-interval average?

4. Before running [Lab 1](./lab1)'s Step 5-6 measurement, estimate your rough expected traffic volume (from the `iperf3` rate and test duration) and your configured sampling rate, plug them in here, and write down the predicted relative error. Then compare it against what you actually measured.
