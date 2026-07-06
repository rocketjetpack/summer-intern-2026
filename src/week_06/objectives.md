---
title: Objectives
---

# Week 6: Objectives

*Note: This is primarily a reading week. There's no ContainerLab topology this week: optics and high-speed signaling aren't really things a Linux container can simulate. There is, though, one interactive [Code Lab](./link-budget) to make the physical-layer math concrete.*

Every previous week has quietly assumed the physical layer just works: a link has "a speed," a cable "just connects things." This week pokes at that assumption. By the end of the week you should be able to:

- **Explain why Ethernet speed increases are a lane-rate story, not just "a faster clock."**
  Going from 10GbE to 400GbE wasn't one continuous dial turning up. Each major jump (802.3ba for 40/100GbE, 802.3bs for 200/400GbE, 802.3cu/802.3df for the newest 800GbE generation) came from raising the per-lane signaling rate *and* changing how many lanes get ganged together to hit the total speed. 100GbE has historically been built as 10×10G, 4×25G, or 2×50G depending on which generation of hardware you're looking at: same total throughput, different lane count underneath it. The electrical-interface names you'll run into on datasheets (XLAUI, CAUI-4, 400GAUI-8) are just shorthand for that lane count and per-lane rate.

  *Questions to consider:*
  - If 100GbE can be built from 4 lanes of 25G *or* 2 lanes of 50G, what would you expect to differ about the transceiver's internal complexity between those two options?
  - Why might a datacenter operator care whether their 400GbE optic uses 8 lanes of 50G or 4 lanes of 100G, beyond "it's 400G either way"?

- **Explain why PAM4 replaced NRZ at higher lane rates, and what it costs.**
  NRZ (Non-Return-to-Zero) signaling encodes one bit per symbol: high voltage or low voltage. PAM4 (4-level Pulse Amplitude Modulation) packs two bits into every symbol instead, using four voltage levels rather than two. For a given symbol rate, that doubles the bit rate. That's why PAM4 shows up at every lane-rate doubling past 25G-per-lane.

  The catch is noise margin. NRZ only has to tell two voltage levels apart, so it has a wide gap between "high" and "low" to work with. PAM4 has to tell four levels apart in roughly that same voltage swing, so each level gets a much narrower slice, and the gap between adjacent levels shrinks accordingly. Raw bit error rate goes up a lot as a result, enough that PAM4 links generally can't ship without strong FEC (below), where the older NRZ links mostly could get away without it.

  The same 16-bit message, sent both ways, makes the trade-off visible:

  ```js
  const nrzBits = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1];
  const pam4Symbols = Array.from({length: nrzBits.length / 2}, (_, i) => [nrzBits[2 * i], nrzBits[2 * i + 1]]);
  const pam4Level = ([b0, b1]) => ({"00": -1, "01": -1 / 3, "11": 1 / 3, "10": 1})[`${b0}${b1}`];
  const nrzData = [...nrzBits.map((b, i) => ({t: i, v: b ? 1 : -1})), {t: nrzBits.length, v: nrzBits.at(-1) ? 1 : -1}];
  const pam4Data = [...pam4Symbols.map((s, i) => ({t: i, v: pam4Level(s)})), {t: pam4Symbols.length, v: pam4Level(pam4Symbols.at(-1))}];
  ```

  ```js
  Plot.plot({
    title: "NRZ: 1 bit per symbol (16 symbols to send 16 bits)",
    width: 680, height: 150,
    marginLeft: 55, marginRight: 20, marginBottom: 30,
    x: {label: "symbol count →", domain: [0, 16]},
    y: {label: "voltage", domain: [-1.4, 1.4], ticks: [-1, 1]},
    marks: [
      Plot.ruleY([0], {stroke: "#bbb", strokeDasharray: "3,3"}),
      Plot.line(nrzData, {x: "t", y: "v", curve: "step-after", stroke: "#1565c0", strokeWidth: 2.5}),
    ]
  })
  ```

  ```js
  Plot.plot({
    title: "PAM4: 2 bits per symbol (same 16 bits fit in 8 symbols)",
    width: 680, height: 150,
    marginLeft: 55, marginRight: 20, marginBottom: 30,
    x: {label: "symbol time →", domain: [0, 16]},
    y: {label: "voltage", domain: [-1.4, 1.4], ticks: [-1, -1 / 3, 1 / 3, 1]},
    marks: [
      Plot.ruleY([-2 / 3, 0, 2 / 3], {stroke: "#bbb", strokeDasharray: "3,3"}),
      Plot.line(pam4Data, {x: "t", y: "v", curve: "step-after", stroke: "#c62828", strokeWidth: 2.5}),
    ]
  })
  ```

  Both charts share the same x-axis and the same per-symbol duration. NRZ needs all 16 symbol slots to send the message; PAM4 is done by the halfway mark, because every symbol there is carrying 2 bits instead of 1. That's the density gain from the first paragraph. Now look at the dashed lines: NRZ only has to keep its signal on one side or the other of a single threshold, with a full unit of margin on either side. PAM4 has three thresholds packed into the same voltage swing, so the margin around each one shrinks to about a third of NRZ's. That shrinkage is the entire cost side of this trade-off, and it's exactly why FEC (next objective) has to pick up the slack. *(This is a simplified schematic with idealized, evenly-spaced Gray-coded levels, not a captured oscilloscope trace, but the geometry, and the roughly 3x margin reduction, holds in the real signal too.)*

  *Questions to consider:*
  - If PAM4 shrinks the noise margin between adjacent signal levels compared to NRZ, why would an engineer accept that trade-off at all?
  - What do you think an eye diagram (the standard oscilloscope view of a digital signal) looks like once you go from NRZ to PAM4? Which one would you rather have to read?

- **Explain why PAM4 links require Forward Error Correction, and what FEC costs in return.**
  Because PAM4's raw bit error rate is too high to ship uncorrected, PAM4-based Ethernet always pairs the modulation with Reed-Solomon FEC. Two names come up constantly: RS-FEC (also "KR4," originally defined for NRZ-based 100G backplane links, RS(528,514)) and the stronger "KP4" FEC (RS(544,514)) that PAM4 links generally need. The mechanism is the same either way: extra redundant symbols ride alongside the data, so the receiver can detect and correct a bounded number of symbol errors without asking for a retransmit.

  The cost is latency: encoding and decoding both take time, on the order of 100-200ns depending on which FEC variant is running, plus a small chunk of the link's raw bit rate spent on the redundant symbols. For most Ethernet traffic that's nothing. It matters a lot more once you get to RDMA/InfiniBand (Week 8), where the whole latency budget for an operation is measured in single-digit microseconds, and a few hundred nanoseconds stops being a rounding error.

  *Questions to consider:*
  - Week 4 established that TCP throughput collapses multiplicatively with loss (the Mathis formula). Does FEC make that problem go away, or just move where in the stack loss shows up?
  - A 100-200ns FEC latency add sounds tiny. Under what circumstances might it stop being negligible?

- **Describe the transceiver form-factor evolution as a density and power story.**
  `SFP → SFP+ → SFP28 → QSFP → QSFP+ → QSFP28 → QSFP-DD → OSFP` looks like an alphabet-soup naming problem, but it's really just two knobs being turned: raise the per-lane rate the module supports, or add more electrical lanes. QSFP's whole distinction from SFP is exactly that: four lanes instead of one, hence "Quad." QSFP-DD ("Double Density") and OSFP push lane count further still, to eight, to reach 400G and 800G totals in one pluggable module.

  A switch's front panel only has so much physical space, and each slot only has so much power and cooling capacity. Packing more bandwidth into the same rack unit means more lanes per module, a higher rate per lane, or both. It's the same trade-off as the first objective, just showing up now as a mechanical and thermal constraint instead of a signaling one.

- **Understand dBm and dB (absolute power vs. relative loss) before doing any link math.**
  Two units get used constantly from here on, and mixing them up is the single most common way to get lost in this stuff. **dBm** is absolute: a specific amount of optical power, measured against a fixed 1 milliwatt reference.

  ```js
  tex.block`P_{\text{dBm}} = 10 \log_{10}\left(\frac{P_{\text{mW}}}{1\text{ mW}}\right)`
  ```

  **dB** is relative: a ratio between two powers, with no fixed reference point at all. It only ever describes a *change*.

  ```js
  tex.block`\text{Loss or gain (dB)} = 10 \log_{10}\left(\frac{P_{\text{out}}}{P_{\text{in}}}\right)`
  ```

  A transmitter's launch power is a dBm number, because it's a specific quantity of light. Fiber attenuation, connector loss, and splice loss are all dB numbers, because they only say how much of whatever power arrived got thrown away. They don't care what the starting power was. Try it below: drag the starting power, then drag a loss or gain on top of it.

  ```js
  const dbmStart = view(Inputs.range([-40, 10], {step: 0.5, value: 0, label: "Starting power (dBm)"}));
  const dbChange = view(Inputs.range([-30, 10], {step: 0.5, value: -6, label: "Applied loss/gain (dB, negative = loss)"}));
  ```

  ```js
  const mwFromDbm = (dbm) => Math.pow(10, dbm / 10);
  const formatPower = (mw) => mw >= 1 ? `${mw.toFixed(3)} mW` : mw >= 0.001 ? `${(mw * 1000).toFixed(1)} µW` : `${(mw * 1e6).toFixed(1)} nW`;
  const startMw = mwFromDbm(dbmStart);
  const resultDbm = dbmStart + dbChange;
  const resultMw = mwFromDbm(resultDbm);
  const linearRatio = resultMw / startMw;
  ```

  ```js
  display(html`
    <div style="background:#f8f8f8;border-left:4px solid #1565c0;padding:10px 16px;margin:8px 0;font-family:monospace;font-size:0.95em">
      Starting power: <strong>${dbmStart.toFixed(1)} dBm</strong> = <strong>${formatPower(startMw)}</strong><br>
      Applying <strong>${dbChange >= 0 ? "+" : ""}${dbChange.toFixed(1)} dB</strong> is just addition in the log domain:
      ${dbmStart.toFixed(1)} + (${dbChange.toFixed(1)}) = <strong>${resultDbm.toFixed(1)} dBm</strong><br>
      Resulting power: <strong>${formatPower(resultMw)}</strong>. That's the starting power times <strong>${linearRatio.toFixed(4)}×</strong> in the linear (mW) domain.
    </div>
  `);
  ```

  Notice the two domains stay in sync no matter where you drag: dB numbers add, mW numbers multiply, and the calculator is just doing both at once so you can see they're the same fact. A few fixed points are worth keeping in your head, because they cover most real mental math in the field:

  | dB | Power ratio | Rule of thumb |
  |---|---|---|
  | +10 dB | 10× | "add a zero" |
  | +3 dB | ≈2× | roughly double |
  | 0 dB | 1× | no change |
  | −3 dB | ≈0.5× | roughly half |
  | −10 dB | 0.1× | "drop a zero" |
  | −20 dB | 0.01× | |
  | −30 dB | 0.001× | |

  This is exactly why the [Link Power Budget](./link-budget) code lab, a few objectives from now, gets to treat a whole chain of fiber loss, connector loss, and splice loss as one plain sum: dB numbers add, so the running total is just addition all the way down, no per-component multiplication required.

  *Questions to consider:*
  - A transmitter outputs 0 dBm. After 10km of fiber at 0.3 dB/km and 2 connectors at 0.5 dB each, what's the resulting power, in dBm and in mW?
  - One engineer says "we lost half the power on that run." Another says "we measured 3 dB of loss." Are they disagreeing, or describing the same thing two different ways?

- **Compare multimode and single-mode fiber as a distance/cost trade-off.**
  Picture each fiber core in cross-section, with light entering at a handful of different angles:

  ```js
  const fiberLen = 10;
  const mmfXs = Array.from({length: 300}, (_, i) => (i / 299) * fiberLen);
  const mmfModes = [
    {name: "axial ray", period: Infinity, color: "#1565c0"},
    {name: "low-angle mode", period: 14, color: "#2e7d32"},
    {name: "high-angle mode", period: 6, color: "#c62828"},
  ];
  const mmfRayData = mmfModes.flatMap((m) => mmfXs.map((x) => ({
    x,
    y: m.period === Infinity ? 0 : (2 / Math.PI) * Math.asin(Math.sin((2 * Math.PI * x) / m.period)),
    mode: m.name,
  })));
  const mmfCore = [{x1: 0, x2: fiberLen, y1: -1, y2: 1}];
  const mmfCladTop = [{x1: 0, x2: fiberLen, y1: 1, y2: 1.4}];
  const mmfCladBottom = [{x1: 0, x2: fiberLen, y1: -1.4, y2: -1}];
  ```

  ```js
  Plot.plot({
    title: "Multimode fiber: several paths, several path lengths",
    width: 680, height: 190,
    marginLeft: 20, marginRight: 20, marginTop: 30, marginBottom: 30,
    x: {domain: [0, fiberLen], label: "fiber length →", ticks: []},
    y: {domain: [-1.4, 1.4], axis: null},
    color: {domain: mmfModes.map((m) => m.name), range: mmfModes.map((m) => m.color), legend: true},
    marks: [
      Plot.rect(mmfCladTop, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: "#cfd8dc"}),
      Plot.rect(mmfCladBottom, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: "#cfd8dc"}),
      Plot.rect(mmfCore, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: "#e3f2fd"}),
      Plot.line(mmfRayData, {x: "x", y: "y", stroke: "mode", z: "mode", strokeWidth: 2}),
    ]
  })
  ```

  ```js
  const smfRayData = mmfXs.map((x) => ({x, y: 0}));
  const smfCore = [{x1: 0, x2: fiberLen, y1: -0.3, y2: 0.3}];
  const smfCladTop = [{x1: 0, x2: fiberLen, y1: 0.3, y2: 1.4}];
  const smfCladBottom = [{x1: 0, x2: fiberLen, y1: -1.4, y2: -0.3}];
  ```

  ```js
  Plot.plot({
    title: "Single-mode fiber: one path, no modal dispersion",
    width: 680, height: 190,
    marginLeft: 20, marginRight: 20, marginTop: 30, marginBottom: 30,
    x: {domain: [0, fiberLen], label: "fiber length →", ticks: []},
    y: {domain: [-1.4, 1.4], axis: null},
    marks: [
      Plot.rect(smfCladTop, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: "#cfd8dc"}),
      Plot.rect(smfCladBottom, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: "#cfd8dc"}),
      Plot.rect(smfCore, {x1: "x1", x2: "x2", y1: "y1", y2: "y2", fill: "#e3f2fd"}),
      Plot.line(smfRayData, {x: "x", y: "y", stroke: "#1565c0", strokeWidth: 2}),
    ]
  })
  ```

  The multimode core (light blue band) is wide enough for light to bounce down several distinct paths at once. Every path spans the same fiber length, but the steeper ones physically travel farther to get there, so they show up at the far end a little later than the axial ray. That spread in arrival times is modal dispersion, and it's what caps multimode fiber's distance and speed. The single-mode core is drawn to scale next to it: too narrow for anything but one path, so there's nothing to spread out. That's the whole reason single-mode fiber, not multimode, is what carries traffic once you leave the building: not a better version of the same thing, but a structurally different guarantee.

  Multimode fiber (OM3, OM4, OM5) uses cheaper VCSEL-based optics matched to its wider core, and stays cheaper for short runs: in a rack, between rows. Single-mode (OS2) uses costlier laser-based optics and is the on-ramp to Week 7's long-haul transport.

  *Questions to consider:*
  - OM3, OM4, and OM5 all use the same 850nm VCSEL-based approach and the same core width. What do you think actually improved between those generations, if not the wavelength or the core?
  - The diagram draws single-mode core at less than a third of multimode's width, roughly true to life (about 9 microns vs. 50). Why would a narrower core be the thing that forces light down a single path?

- **Compare parallel optics and WDM-multiplexed optics as two answers to "how do I get N lanes across a fiber plant."**
  Say you need to move 4 lanes of traffic. There are two fairly different ways to do it optically:
  - **Parallel optics** (SR4, PSM4): give each lane its own physical fiber, all at the same wavelength, bundled into a multi-fiber MPO/MTP connector. The optics are simple, but fiber count scales linearly with lane count.
  - **Wavelength-multiplexed optics** (CWDM4, LR4, ER4): put all 4 lanes on a single fiber pair by giving each lane its own wavelength and combining/splitting them optically. The optics cost more, but fiber count stays at 2 no matter how many lanes you add.

  It's the same tension Week 4 raised with ECMP vs. LAG, just at the physical layer: parallel optics is cheap and simple but eats into fiber-plant capacity as bandwidth grows (a real constraint when a spine-leaf fabric only has so many fiber runs between rows), while WDM optics costs more per port but decouples bandwidth from fiber count. It's also where Week 7 picks up: OTN and long-haul DWDM transport are this same idea, just with dozens of wavelengths over much longer distances instead of 4 wavelengths over a couple of kilometers.

- **Compute a basic optical link power budget and determine whether a link will close.**
  A link "closes" when the light arriving at the receiver is bright enough to read reliably, without being so bright it overwhelms the receiver (rarely the binding constraint in practice). The calculation is a straightforward budget: take the transmitter's launch power in dBm, subtract every source of loss along the way (fiber attenuation over distance, connector loss at each mated pair, splice loss at each splice), and see what's left against the receiver's sensitivity, the minimum power it needs to read a signal reliably. Subtract a safety margin for aging and manufacturing tolerance, and what remains is the link margin. Positive margin, the link should work. Margin near or below zero, it won't, no matter how correct your addressing, routing, and congestion control are further up the stack.

  That's the whole exercise in the [Link Power Budget](./link-budget) code lab: pick a fiber type and distance, add connectors and splices, and watch how much margin you have (or don't).

  *Questions to consider:*
  - Two links use identical transceivers and identical fiber length, but one has 2 connector pairs and the other has 6 (a patch panel at every row). Roughly how much margin does that difference cost?
  - Why does dB math work by subtracting losses and adding margin, rather than the multiplication/division you might expect from "percentage of power lost"? (Hint: dB is already a logarithmic ratio.)

---

## Putting It Together

Everything this program has covered so far (TCP congestion control in Week 4, flow telemetry in Week 5, even plain addressing and switching in Week 3) quietly assumes frames actually arrive at the other end of a link with an acceptably low error rate. This week is about the layer underneath all of that: the modulation scheme, the error correction, the physical medium, and the power budget that make "the link works" true in the first place.

If there's one idea tying the objectives above together, it's that speed and density always cost something: money, power, distance, or noise margin, usually some combination. PAM4 trades noise margin for lane-rate doubling, and pays some of it back with FEC latency. QSFP-DD and OSFP trade per-slot power and heat for port density. Parallel optics trades fiber count for simplicity; WDM trades optic cost and complexity for fiber efficiency. None of these are solved problems. They're decisions a network architect makes on purpose, the same way Week 4 treated oversubscription ratio and ECMP-vs-LAG as deliberate choices rather than flaws to be fixed.

## The Week 7 Bridge

Week 7 (OTN, transport between sites) picks up right where this week's WDM discussion leaves off. This week's CWDM4/LR4 optics multiplex a handful of wavelengths over a couple of kilometers, inside or between buildings on the same site. Week 7's DWDM transport multiplexes dozens of wavelengths over tens to thousands of kilometers between sites. The link power budget you compute in this week's code lab is the same calculation an OTN/DWDM designer runs, just with amplifiers, dispersion compensation, and a lot more decibels to account for.

*Forward reference: the FEC and latency discussion above is also a direct on-ramp to Week 8 (InfiniBand & RDMA), where link-layer latency additions that are negligible for ordinary Ethernet traffic become a meaningful fraction of a microsecond-scale RDMA operation.*
