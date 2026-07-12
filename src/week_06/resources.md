---
title: Resources
---

# Week 6 — Resources

Readings are grouped by topic, in the same order as the [Objectives](./objectives) page. Read the Required entry before the corresponding topic's discussion; Recommended entries deepen understanding but are not prerequisites. Every link below was fetched and content-checked before being listed here. A couple of topics have a caveat noting a source that had to be substituted or dropped, called out inline.

---

## Ethernet Speed Evolution (802.3ba/bs/cu/df)

### Required

- **[Ethernet Alliance — 2025 Ethernet Roadmap (PDF)](https://ethernetalliance.org/wp-content/uploads/2025/03/2025-Ethernet-Roadmap-2-Sided-Web-03-17-2025.pdf)**
  A single infographic covering every Ethernet speed generation from 10Mb/s through 1.6Tb/s: the AUI electrical-interface names (XLAUI, CAUI-4, 400GAUI-8, etc.), per-generation FEC and lane counts, and the pluggable-optics roadmap. Focus on the lane-count/lane-rate columns, not the exact dates.

### Recommended

- **[IEEE SA — 802.3ba-2010 standard overview](https://standards.ieee.org/ieee/802.3ba/4319)**
  The official abstract page for the 40/100GbE amendment: scope and approval date, not the full (paywalled) standard text.
- **[IEEE SA — 802.3bs-2017 standard overview](https://standards.ieee.org/ieee/802.3bs/6748)**
  Same treatment for the 200/400GbE amendment.

---

## PAM4 Modulation

### Required

- **[Keysight — Pulse Amplitude Modulation (PAM4)](https://www.keysight.com/us/en/learn/hubs/high-speed-digital-system-design/pulse-amplitude-modulation-pam4.html)**
  Clear explanation of PAM4 doubling data rate per symbol relative to NRZ, and the resulting SNR/noise-margin trade-off that makes FEC necessary.

### Recommended

- **[VIAVI Solutions — What is PAM4?](https://www.viavisolutions.com/en-us/what-pam4)**
  A concise NRZ-vs-PAM4 comparison from a test-equipment vendor's perspective; a good second angle on the same SNR/BER trade-off.

*Note: Keysight also publishes deeper PAM4 application notes, but the PDF links for those turned out to be registration-gated rather than freely accessible, so they're excluded here.*

---

## Forward Error Correction (FEC)

### Required

- **[IEEE 802.3 — "802.3bj FEC Overview and Status" (Gustlin & Lusted, 802.3db Task Force, June 2020, PDF)](https://www.ieee802.org/3/db/public/adhoc/presentations/gustlin_3db_adhoc_01_062520.pdf)**
  A primary-source IEEE 802.3 working-group presentation with an explicit table mapping each relevant amendment (802.3ba/bj/bm/bs/cd/ck/cu) to its FEC code, clearly distinguishing RS(528,514) ("KR4," originally for NRZ) from RS(544,514) ("KP4," for PAM4).

### Recommended

- **[LINK-PP — Forward Error Correction (FEC) in Optical Networks](https://www.link-pp.com/knowledge/forward-error-correction-fec-optical-networks.html)**
  Explicitly quantifies FEC's latency cost (roughly 80-120ns for RS-FEC, 100-200ns for KP4-FEC): the number behind the "InfiniBand/RDMA latency budget" question in the objectives.
- **[Anritsu — Implementing FEC Rx Test using FEC Symbol Capture Function (Application Note, PDF)](https://dl.cdn-anritsu.com/en-en/test-measurement/files/Application-Notes/Application-Note/mp1900a-fec-rx-ef1200.pdf)**
  A test-equipment vendor's walkthrough of IEEE 802.3 FEC structure and physical-layer evaluation, useful if you want to go one level deeper into how FEC is actually tested.

---

## Optical Transceiver Form Factors

### Required

- **[Wikipedia — Small Form-factor Pluggable transceiver](https://en.wikipedia.org/wiki/Small_Form-factor_Pluggable_transceiver)**
  Traces the full SFP (2001) → SFP+ (2006) → SFP28 (2014) → QSFP (2006) → QSFP+ (2012) → QSFP28 (2014) → QSFP-DD (2016) → OSFP lineage with lane counts, speeds, and pin counts for each.

### Recommended

- **[QSFP-DD MSA — Specification page](http://www.qsfp-dd.com/specification/)**
  The Multi-Source Agreement group's own published hardware-spec revisions for QSFP-DD.
- **[OSFP MSA — osfpmsa.org](https://osfpmsa.org/)**
  Covers OSFP (8 lanes, up to 1.6Tbps) and the newer OSFP-XD (16 lanes) variants directly from the MSA group.

*Note: the SNIA/SFF committee (the body historically behind the SFP/QSFP MSAs) is the more "canonical" source for this topic, but their site is a JavaScript-rendered SPA that couldn't be content-verified this pass, so Wikipedia was used as a well-sourced substitute instead.*

---

## Fiber Types: Multimode (OM3/OM4/OM5) vs. Single-Mode (OS2)

### Required

- **[Fluke Networks — OM1, OM2, OM3, OM4, OM5 and OS1, OS2 Fiber Testing](https://www.flukenetworks.com/knowledge-base/copper-testing/om1-om2-om3-om4-om5-and-os1-os2-fiber)**
  Covers every current multimode and single-mode fiber grade, what distinguishes them, and how each is tested.

### Recommended

- **[The FOA (Fiber Optic Association) — Fiber Optic Cable Plant Nomenclature](https://www.thefoa.org/tech/OM.html)**
  The OM/OS naming-convention reference from the industry's own trade association.
- **[The FOA — Singlemode Fiber Types](https://www.thefoa.org/tech/smf.htm)**
  Single-mode-specific detail (OS1 vs OS2, core size, why single-mode requires laser sources).

*Note: Corning is the more commonly cited vendor reference for this topic, but every Corning URL attempted (app notes, datasheets) returned an access-blocked response this session rather than a working page. It may well work in an ordinary browser, but it's excluded here since it couldn't be verified.*

---

## Parallel Optics vs. WDM-Multiplexed Optics

### Required

- **[FiberMall — 100G QSFP28: SR4 vs PSM4 vs CWDM4 vs LR4 vs ER4](https://www.fibermall.com/blog/100g-qsfp28-sr4-psm4-cwdm4-lr4-er4.htm)**
  Directly explains the trade-off from the objectives: parallel optics (SR4/PSM4, MPO/MTP connector, more fibers, simpler optics) versus wavelength-multiplexed optics (CWDM4/LR4/ER4, duplex LC connector, fewer fibers, costlier optics).

### Recommended

- **[CWDM4-MSA Group](https://cwdm4-msa.org/)**
  The MSA body's own description of the 4×25G CWDM approach for 100G over a single duplex single-mode fiber pair.
- **[LINK-PP — PSM4 vs. CWDM4: Which Optical Transceiver Is Right for Your Network](https://resources.l-p.com/knowledge-center/psm4-vs-cwdm4-which-optical-transceiver-for-your-network)**
  A side-by-side vendor comparison table (fiber count, reach, connector type, relative cost).

---

## Optical / Link Power Budgets

### Required

- **[The FOA — Calculating Fiber Optic Loss Budgets](https://www.thefoa.org/tech/lossbudg.htm)**
  Walks through the exact calculation this week's [Link Power Budget](./link-budget) code lab implements: fiber loss + connector loss + splice loss, compared against the transmitter/receiver dynamic range, with a margin check.

*Note: only one fully-verified source was found for this specific topic in the time available. If you want a second reading here, flag it and it can be added in a follow-up pass. Don't take the single-source list as a signal this topic is any less important than the others.*
