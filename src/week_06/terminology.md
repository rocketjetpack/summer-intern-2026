---
title: Terminology
---

# Week 6 — Terminology

| Term / Acronym | Definition |
|---|---|
| **802.3ba** | The IEEE amendment (2010) that first standardized 40GbE and 100GbE |
| **802.3bs** | The IEEE amendment (2017) that standardized 200GbE and 400GbE |
| **802.3cu / 802.3df** | The more recent IEEE amendments covering the 800GbE generation and its lane-rate progression |
| **AUI** | Attachment Unit Interface: the naming convention for an Ethernet electrical interface between a MAC/PHY and optics (e.g. XLAUI, CAUI-4, 400GAUI-8); the name encodes the lane count and rate feeding the transceiver |
| **BER** | Bit Error Rate: the fraction of received bits that are in error before any correction is applied |
| **CWDM** | Coarse Wavelength Division Multiplexing: combines a handful of widely-spaced wavelengths onto a single fiber pair; used by CWDM4 optics for 100G over 2km |
| **CWDM4** | A 100G optical spec that uses 4 lanes of 25G, each on its own CWDM wavelength, multiplexed over a single duplex single-mode fiber pair |
| **DWDM** | Dense Wavelength Division Multiplexing: combines many closely-spaced wavelengths on one fiber; the long-haul, high-density counterpart to CWDM, central to OTN transport (a stretch topic later in the program) |
| **Eye Diagram** | An oscilloscope view built by overlaying many signal periods; the "eye" opening's height and width indicate noise margin and timing margin. PAM4 has three smaller eyes stacked where NRZ has one large eye |
| **FEC** | Forward Error Correction: encoding redundant symbols alongside data so a receiver can detect and correct a bounded number of errors without retransmission |
| **Insertion Loss** | The optical power lost when light passes through a connector, splice, or other in-line component |
| **Lane** | One independent electrical or optical signaling path; modern Ethernet speeds are built from multiple lanes running in parallel rather than one lane running arbitrarily fast |
| **Link Margin** | The optical power budget remaining after subtracting all path losses (and a safety margin) from the transmitter/receiver dynamic range; positive margin means the link should close |
| **KP4 FEC** | RS(544,514) Reed-Solomon FEC: the stronger FEC variant generally required by PAM4-based Ethernet links |
| **KR4 FEC** | RS(528,514) Reed-Solomon FEC: the original "RS-FEC," defined for NRZ-based 100G backplane/optical links |
| **MPO / MTP** | Multi-fiber Push On (MPO is the generic connector standard; MTP is a common trademarked implementation): a connector carrying many fibers in one housing, used for parallel optics like SR4/PSM4 |
| **Multimode Fiber (MMF)** | Fiber with a wide core (typically 50 microns) that supports many simultaneous light paths ("modes"); cheaper, VCSEL-driven optics, but limited by modal dispersion to shorter distances. OM3/OM4/OM5 are current generations |
| **NRZ** | Non-Return-to-Zero: the simpler modulation scheme encoding one bit per symbol as one of two voltage levels |
| **OM3 / OM4 / OM5** | Successive generations of laser-optimized multimode fiber; each generation increases the effective bandwidth-distance product at 850nm, extending how far a given speed can run over multimode |
| **OS2** | The current single-mode fiber grade; narrow core (about 9 microns) forces a single light path, eliminating modal dispersion and enabling distances from kilometers to tens of kilometers |
| **OSFP** | Octal Small Form-factor Pluggable: an 8-lane transceiver form factor (with an OSFP-XD variant at 16 lanes) used for 400G/800G+ |
| **PAM4** | 4-level Pulse Amplitude Modulation: encodes 2 bits per symbol using four distinct voltage levels, doubling bit rate over NRZ at the same symbol rate, at the cost of reduced noise margin |
| **Parallel Optics** | An optical design that puts each data lane on its own physical fiber, all at the same wavelength (e.g. SR4, PSM4); simple optics, fiber count scales with lane count |
| **PSM4** | Parallel Single Mode 4-lane: a 100G parallel-optics spec using 4 lanes of 25G, each on its own single-mode fiber (8 fibers total for a duplex link) |
| **QSFP / QSFP+ / QSFP28** | Quad Small Form-factor Pluggable: a 4-lane transceiver form factor; the "Quad" name distinguishes it from single-lane SFP. Successive generations (QSFP+, QSFP28) raise the per-lane rate |
| **QSFP-DD** | QSFP Double Density: an 8-lane transceiver form factor, mechanically similar to QSFP but with twice the electrical lanes, used for 400G |
| **Receiver Sensitivity** | The minimum optical power (in dBm) a receiver needs to reliably detect a signal |
| **RS-FEC** | Reed-Solomon Forward Error Correction: the family of FEC codes (KR4, KP4) used across modern high-speed Ethernet |
| **SFP / SFP+ / SFP28** | Small Form-factor Pluggable: a single-lane transceiver form factor; successive generations (SFP+, SFP28) raise the per-lane rate from 1G/10G up to 25G |
| **Single-Mode Fiber (SMF)** | See OS2: fiber supporting only a single light path, used for longer-distance and higher-speed links; requires laser-based optics |
| **Symbol Rate** | The rate at which the signal changes state (measured in baud); distinct from bit rate once a modulation scheme (like PAM4) encodes more than one bit per symbol |
| **WDM** | Wavelength Division Multiplexing: combining multiple signals onto one fiber by assigning each its own wavelength of light; CWDM and DWDM are the coarse- and dense-spacing variants |
