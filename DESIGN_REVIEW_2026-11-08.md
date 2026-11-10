# Polestar FlexRay MITM — Pre-fab Design Review

**Date:** 2026-11-08 · **Files:** `Polestar_Flexray.kicad_sch` / `.kicad_pcb` (saved 14:52), `production/` (14:38) · **KiCad:** 10.0.8 · 4-layer, 98.1 × 58.1 mm, 80 parts (84 footprints incl. H1–H4), 133 nets

**Checks run:** kicad-cli ERC, DRC with schematic parity (stored fills and refilled), fresh netlist; kicad-happy `analyze_schematic`, `analyze_pcb --full --proximity`, `cross_analysis`, `analyze_emc`, `simulate_subcircuits` (ngspice), `analyze_thermal`, `analyze_gerbers` (production zip and a fresh export); manufacturer datasheets for every IC, transistor, ESD/TVS part, relay and the crystal; LCSC product API for every JLCPCB C-number; pad-level comparison of J1–J4 against the original built board (`main` branch of the harness-box repo).

## Verdict

**The circuit is wired correctly. Every pinout checked against its datasheet matches, ERC/DRC are clean, and no connectivity or polarity errors were found. Do not order yet, though:** the BOM/CPL in `production/` are stale, two connectors are out of stock, and the 40 MHz crystal is a −20…+70 °C consumer part in a car. Fix the four "must do" items; the "should fix" items are strongly recommended.

## Re-check and fixes (2026-11-09)

Every check was re-run on the 22:41 files. ERC, DRC and parity were clean, and `production/` matched the board on every layer. Three things were wrong or marginal, and all three are now fixed. Backups: `.mcp-backups/*.20261109-pre-fixes`.

| Item | Change |
|---|---|
| D12, D15 placement | JLC's footprint for the DSK14 (C908228, package `SOD-123_…-FD`) numbers the **anode** as pad 1. Every other diode on the board is cathode-first, and so is the `SCHOTTKY - 1A` footprint. The old placement file (D12 = 90°, D15 = 180°) would have had JLC fit both backwards: no 5 V to the XIAO, and no V+ for U1/U2. Hidden `FT Rotation Offset` = 180 added in the schematic and board. The placement file now reads D12 = 270°, D15 = 0°. In JLC's preview the band on D12 faces C26 and on D15 faces R21. |
| U8 part number | TCAN4550RGYRQ1 (C2876736) went to 0 stock. Switched to **TCAN4550RGYTQ1, C5215852** (45 at JLC on 11-09). It is the same device on a small reel with the same JLC footprint, so the 270° offset is unchanged. The footprint keeps its `TI TCAN4550RGYRQ1` name. |
| +5V run under U3 | The 0.6 mm run sat 0.05 mm inside U3's outline, directly under the package's two exposed ground tabs on the pin 5/6 edge. Those tabs have no land (the tab lands were left out on 11-08 because of this track), so only solder mask separated +5V from ground. The run moved 0.2 mm away, to y = 124.45. Its edge is now 0.15 mm outside the package and at least 0.25 mm from C27 and the ground via beside it. |

**Correction to the 11-08 rotation check.** That check matched pad numbers, which is valid for ICs and transistors but not for two-pin diodes. Re-done by anode/cathode: CR1, CR2, D9, D13, D14 and D16 were already right; D12 and D15 were not. Current result: 74 parts correct, 0 wrong, 6 not checkable from JLC's data (D10, D11, R17, R18 and U4 have no JLC footprint; J2 is keyed by its peg).

**After the fixes:**
- ERC: 0.
- DRC: 0 errors, 0 unconnected, with stored and refilled zones. Parity: only H1–H4.
- Netlist connectivity is unchanged.
- `production/` was regenerated at 20:36 and compared with a fresh plot. The only gerber change is the four +5V segments on F.Cu; the BOM and placement file changed only in the U8, D12 and D15 lines.

**Stock on 2026-11-09 (JLC parts library):** J3/J4 C5359473 = 2 (one board's worth; LCSC has 0), U3 C2073079 = 10, R11/R12/R14/R15 C5290207 = 34, J2 C5354889 = 104.

**2026-11-10: R10 changed to 3.3 kΩ.** R10 (Q2's gate pull-down) is now the same part as R8/R21: Rohm ESR03EZPF3301, C510091, on footprint `Rohm ESR03EZPJ332`, which has the same land as before. Backups: `.mcp-backups/*.20261110-pre-r10`.
- **Why:** R9 + R10 put 11 kΩ on GP7. Raspberry Pi's erratum E9 for RP2350-A2 silicon asks for 8.2 kΩ or less on an external pull-down, because a pin left as an input can leak up to about 120 µA out of the pad. Through 10 kΩ that is 1.2 V on Q2's gate, above its 1.0 V maximum threshold, so K2/K3 could pull in. The total is now 4.3 kΩ, and the same leakage gives at most 0.40 V, below Q2's 0.45 V minimum threshold. The 8.2 kΩ and 120 µA figures come from published write-ups of the erratum, not from the datasheet PDF. The XIAO's chip revision can't be read under its shield; the A4 revision does not have the fault, and the change is harmless on it.
- **Gate drive:** Q2's gate now gets 2.5 V instead of 3.0 V. The DMN3200U-7 is rated 110 mΩ max at 2.5 V, and the load is 25 mA of relay coil. GP7 sources 0.77 mA when high.
- **Checks:** ERC 0. DRC 0 errors, 0 unconnected, with stored and refilled zones. Parity only H1–H4. Netlist connectivity unchanged.
- **`production/`** was regenerated at 07:20. The BOM moves R10 from the 10 kΩ line to the 3.3 kΩ line (still 40 lines, 80 parts). The placement file is unchanged. The gerbers and drill files differ from the 11-09 set only in their timestamps, and a fresh plot matches the zip on all 11 layers. JLC had 4,051 of C510091 on 11-10.

**2026-11-10: polarity marks added.** A silk asterisk now marks pin 1 of U5 and U6 and the cathode of D9, D12 and D15, matching the asterisks already on the other diodes and U1/U2. The "D15" label moved to the left of the part to make room. Only the board file and the front silkscreen gerber changed; DRC is still clean. Backup: `.mcp-backups/*.20261110-pre-silk`.

**Still open:**
- Order with 1 oz inner copper and ENIG, and tick "Confirm Parts Placement". JLC publishes no footprint for U4 (XIAO) or D10/D11, so check those in JLC's drawing. U4's USB-C end faces the top board edge, and its placement point is 0.44 mm off the centre of its pads.
- IGN (pin 25) is 0.6 mm. On the built board it was 1.0 mm while Harness_12v and Harness_GND were only 0.2 mm, so pin 25 was the line sized for current. Confirm what it feeds.
- Everything in §3 and §4 below, plus FlexRay polarity: BP is on pin 29 and BM on pin 30 at both connectors.

## Fixes applied (2026-11-08, after this review)

S1–S4 are done. Backups: `.mcp-backups/*.20261108-pre-fixes`.

After the fixes, all checks still pass:
- ERC: 0.
- DRC: 0 errors, 0 unconnected, with stored and refilled zones.
- Parity and library mismatches: the same 10 lib-mismatch warnings and H1–H4 parity notices as before.
- Netlist: connectivity identical to the pre-fix export.

| Item | Change |
|---|---|
| S1 Y1 / C17 / C18 | Y1 → **Slkor SL201640M12P** (C5155517): −40…+85 °C operating and storage, ESR ≤ 40 Ω, C0 ≤ 3 pF, CL 12 pF. C17/C18 → **2.2 pF C0G** FH 0603CG2R2C500NT (C1651), which matches the footprint name they already used. With the TCAN4550's pin capacitance this presents ~8.3 pF, deliberately below 12 pF, for an SLLA549 gain margin of ~4 (≈2.4 if matched). Frequency sits ~+40–65 ppm high, irrelevant for CAN. Raise both caps to 10 pF if you ever want it on frequency. R16's description was updated to the new crystal's ESR and drive limits. |
| S2 U8 paste | EP paste is now 4 windows of 0.85 × 1.265 mm (69 %), in the board instance **and** the library footprint `TI TCAN4550RGYRQ1`. The six EP vias moved into the cross-shaped gap between the windows: (0, ±0.43), (0, ±1.275), (±0.775, 0). Every via hole is clear of paste. The library footprint's perimeter pads still follow the TI drawing (the board's +0.3 mm offset is unchanged). The offset matches KiCad's stock `Texas_RGY_R-PVQFN-N20_EP2.05x3.05mm`. |
| S3 U3 land | New library footprint **`Footprints:TI LM53600LQDSXRQ1`** on TI DSX0010A: pins 0.6 × 0.25 mm at 2.8 mm span, EP 1.65 × 2.4 mm, two paste windows (74 %). TI's four tie-bar tabs are omitted because the +5V/FB run and the SW node pass where they would sit. The two outer EP vias moved to TI's (±0.575, 0). The 0.6 mm +5V run under U3 dropped 0.1 mm, to y = 124.25, for 0.25 mm clearance to the larger EP. |
| S4 L1 | → **Coilcraft XAL4030-472MEC** (C19191688): 4.7 µH, 40 mΩ, Isat 4.6 A, automotive. The KiCad XAL4030 land is identical to the XAL4040, so nothing was rerouted. |

**M1 done 22:02.** `production/` was regenerated with the Fabrication Toolkit CLI using your saved options; the stale set is in `.mcp-backups/production.20261108-pre-regen`.
- **BOM:** 40 lines, 80 parts. Every C-number matches the board. U4 was added at 22:18 as **C41882923**. Per JLC's part page it is Seeed 102010550 XIAO RP2350, Assembly Type SMT, MSL 1, 166 in stock. Its 30 bottom/edge pads match `XIAO-RP2350-SMD`. Pre-change set: `.mcp-backups/production.20261108-pre-xiao`.
- **Placement:** all 80 parts unchanged.
- **Gerbers:** 11 layers, 224 vias. They carry the new U3/U8 paste windows.

**22:41: U3 → LM53601LQDSXRQ1 (C2073079, 10 in stock)** on library footprint `TI LM53601LQDSXRQ1`. It is the same package, pinout and land as before, and the 4.7 µH / 4.6 A L1 already suits the 1 A part.

**Placement rotations fixed.** The toolkit only corrects rotations for stock KiCad footprint names, so 14 parts on custom footprints had placement-file rotations that don't match JLC's own footprints (checked against JLC's EasyEDA footprint data). Hidden `FT Rotation Offset` fields were added in the schematic and board:
- **180°:** D1, D2, D3, D17, Q1, Q2, D10, D11 (and L1, which is non-polar).
- **270°:** U1, U2, U5, U6, U8.

With the fix, 74 parts matched JLC's footprints by pad number. That test missed D12 and D15, which were corrected on 2026-11-09 (see the section above). In JLC's preview, check by eye D10/D11 (no JLC footprint exists for C2905640) and U4 (USB-C toward the top edge). Pre-change set: `.mcp-backups/production.20261108-pre-rotfix`.

**Still open:** M2–M4 and everything in §3/§4. In JLC's preview, check rotations on the custom footprints and mark U4 (and any out-of-stock connectors you'll fit yourself) as not placed.

---

## 1. Must do before ordering

| # | Issue | Evidence | Action |
|---|---|---|---|
| M1 | **`production/bom.csv` and `positions.csv` are stale.** They were exported at 14:38, before the part-number pass (board/sch saved 14:52). Nine BOM lines have no LCSC number: **U3, L1, Q3**, R16, D13, D14, D16, CR1/CR2, U4. U8's number is the text `TCAN4550RGYRQ1`, and four lines have leading spaces. Uploaded as-is, JLC would leave U3/L1 (no +5 V), Q3 (VIN never powers), R16 (no crystal path) and the flyback/clamp diodes unplaced. | Raw-file: CSV vs board fields. The current board fields are complete and correct. | Re-run the Fabrication Toolkit. The gerbers/drills in the zip are still valid (board geometry is identical to the 14:38 backup: 1661 tracks, 389 pads, 3 zones, 151 drawings), but regenerate everything together anyway. |
| M2 | **Stock (LCSC, today):** J3/J4 MX34032NF4 C5359473 = **0**; J2 212528-0400 C5354889 = **1**; U3 LM53600LQDSXRQ1 C2072602 = **3**; R11/R12/R14/R15 ESR03EZPJ470 C5290207 = **20** (4 per board → 5 boards max); U8 C2876736 = 23. | LCSC product API | Decide the quantity first. Source J2–J4 elsewhere and consign or hand-solder (they are THT). Reserve U3 now. |
| M3 | **U4 (XIAO RP2350 SMD) must be reflowed, not edge-soldered.** Bottom pads 15–22 carry SPI to the TCAN4550, TCAN_nINT, TCAN_RST and FR1/FR2_ERRN. U4 has no C-number, so JLC will not place it. | Netlist | Hot plate or hot air with paste on all pads, or consign it. Castellations alone leave CAN FD dead. |
| M4 | **Order with 1 oz inner copper.** The stackup is 4 × 35 µm. Harness_12v (2.5 mm on In2) and the VIN island live on inner layers, and JLC's 4-layer default inner copper is 0.5 oz (Harness_12v drops from ~3 A to ~2 A). | Stackup in `.kicad_pcb` | Select 1 oz inner. Also choose **ENIG**: the copper finish is unset, and U8 is a 0.5 mm-pitch QFN. |

## 2. Should fix (design warnings)

**S1 — Y1 crystal is consumer grade.** The Huiyuan HY40MSMD2016DA1R30 (C7275074) datasheet linked by LCSC rates **operating and storage −20 °C to +70 °C**. It is a series spec that lists frequencies only up to 38.4 MHz (ESR ≤ 35 Ω) and allows **C0 ≤ 5 pF**. A car cabin goes below −20 °C and above +70 °C, and the TCAN4550 is rated −40…+125 °C. Your C17/C18 description already says "confirm the −40 °C rating"; it isn't rated for that.
*Oscillation margin (TI SLLA549 eq. 3, 15–17, gm = 6.6 mS):* with C0 = 1.5 pF the margin is ≈ 5.0 at a 9 pF load and ≈ 3.7 at 11 pF. At the datasheet C0 limit of 5 pF it falls to **≈ 1.4–1.6**. TI asks for > 5.
*Fix:* a −40 °C-rated 40 MHz 2016 crystal (ideally AEC-Q200, −40…+105/125 °C) with ESR ≤ 40 Ω, C0 ≤ 2–3 pF and CL 8–10 pF, then re-size C17/C18.
*C17/C18 sizing note:* the 7.5 pF value assumes 0.5 pF PCB stray. At a typical 2–3 pF the presented load is ~10.5–11.5 pF (≈ −20 ppm), which is harmless for CAN. If you keep a 9 pF crystal, ~5.6 pF centres it better. Datasheet-verified (Huiyuan p.1–2, SLLA549 §4, §8).

**S2 — U8 exposed pad is 100 % pasted with six open 0.3 mm vias.** The pad is 2.05 × 3.05 mm with its own paste layer and no windowpane. On a 0.5 mm-pitch QFN this often floats the package or opens perimeter joints, and solder wicks into the vias.
*Fix:* set the EP paste margin negative, or add 4–6 paste windows for ~65–75 % coverage. (U3's EP already uses a 65 % windowpane.) Raw-file verified.

**S3 — U3 sits on the wrong land pattern.** The footprint is KiCad's `VSON-10-1EP_3x3mm_P0.5mm_EP1.2x2mm`, which is drawn for a Rohm BD8314NUV. TI's DSX0010A land (SNAS660D p.43) is a **1.65 × 2.40 mm EP plus four 0.25 mm tie-bar tabs and four Ø0.2 mm vias**. The board EP is 1.20 × 2.00 mm, about 39 % less contact area. Signal pads agree within 0.04 mm, so the part solders and runs; at ~0.2 W dissipation this is not a functional risk today. This was the October "verify U3 thermal-pad size" item, still open.
*Fix:* the stock `VSON-10-1EP_3x3mm_P0.5mm_EP1.65x2.4mm` matches TI's land including the tabs. Swapping needs a local touch-up: re-check the AGND/GND stubs into the EP and the +5V/FB trace that passes the package's bottom edge, then run DRC. Datasheet-verified.

**S4 — L1 = 10 µH; TI recommends 4.7 µH for the fixed 5 V LM53600.** TI states the internal compensation is "stable with inductance between 4 µH and 10 µH" (SNAS660D §9.2.1.2.1, Table 9-2). 10 µH nominal sits on that limit, and the XAL4040's ±20 % tolerance goes beyond it.
The 10 µH choice rested on a "650 kHz at 26 V" premise that the datasheet contradicts. The 5 V part runs at 2.1 MHz up to about 21 V and folds back only to 1.5 MHz at 36 V (§7.6, §8.3). With 4.7 µH, ripple is ~0.3 A p-p at 13.5 V and ~0.6 A p-p at 36 V, inside TI's 1.5 A saturation guidance.
*Fix:* a 4.7 µH part (≥ 1.5 A Isat) in the same XAL4040 4 × 4 mm footprint; check JLC stock. Datasheet-verified.

## 3. Worth considering

- **D2 (camera pair ESD) now sits at J4 (6.9 mm), not at J1 (48–50 mm away).** On the original board it was at J1. J1 B2/B3 are now the only comma bus pins without local ESD (A2/A3 → D17 at 3.4 mm, B10/B11 → D1 at 6.4–7.1 mm), so the DG419LE (2 kV HBM) sees that pin first. Add another PESD1CAN by J1 B2/B3, or accept the risk.
- **No fiducials.** You have a 0.5 mm-pitch QFN and 0.65 mm TSSOPs. JLC adds panel fiducials, but 2–3 board fiducials help placement accuracy.
- **IGN (J3/J4 pin 25) was 1.0 mm on the original board and is now 0.6 mm** (≈1.6 A at 10 °C rise, outer 1 oz). It's fine for a signal; confirm pin 25 isn't the VCU's KL15 supply. The other passthroughs went from 0.2 to 0.15 mm, the same signal class as the built board.
- **OSC1 runs 0.45 mm (edge to edge) from SPI_SCLK on F.Cu.** OSC1/OSC2 are 4.1 / 6.1 mm; TI's layout example asks for matched lengths. This is low risk because In1 GND is 0.21 mm below.
- **Single GND via on D1, D2, D3, D10, D17.** TI §11.1 asks for at least two on protection devices.
- **Documentation hygiene:**
  - C17/C18 use footprint `FH 0603CG2R2C500NT` (a 2.2 pF part name) for the 7.5 pF YAGEO part. The BOM is right; the name misleads.
  - Q3's Datasheet field links the DMN3200U PDF.
  - D14's description says "−20 V rating"; DMP4015SSS VGSS is ±25 V.

## 4. Only you can confirm

- **Enclosure.** The board is now 98.1 × 58.1 mm with 4 × M3 holes; the original was 82.2 × 43.2 mm. J3↔J4 spacing in X went from 43.3 to 59.2 mm.
- **F1 interrupt rating is 50 A @ 63 V.** Make sure the J2 feed is fused upstream (fuse tap) so F1 never has to clear a hard battery short.
- **XIAO pad 24 → GND** (Seeed numbers it SWDCLK). This is your pending check; with this wiring SWD debug won't work.
- **CAN3 termination.** Measure B11–B10 on the comma side with everything off: 60 Ω means two terminators, 120 Ω means only R17/R18.

---

## 5. What was verified

**Pinouts against manufacturer datasheets**

| Ref | Part | Source | Result |
|---|---|---|---|
| U3 | LM53600LQDSXRQ1 | TI SNAS660D Table 6-1; Device Comparison | LQ = **5.0 V fixed**, spread spectrum. All 10 pins + DAP match. EN/SYNC tied to VIN is allowed (forced PWM; SS stays on). |
| U8 | TCAN4550RGYRQ1 | TI SLLSEZ5D Table 5-1, Table 8-16 | All 20 pins + PAD match. OSC1 is the oscillator **output**, so R16 is on the right leg. GPIO1 defaults to GPO and nWKRQ to push-pull, so NC is safe. INH NC and WAKE → GND are allowed. |
| U5, U6 | TJA1082TT | NXP Rev 6 Table 2 (PDF embedded in your `NXP TJA1082` footprint) | 14/14 match. Pads run CCW on the PCB. VCC/VIO stay under the 5.5 V abs max. |
| U1, U2 | DG419LEDY | Vishay 76432 p.1–2 | 1 COM, 2 NC, 3 GND, 4 V+, 5 VL, 6 IN, 7 V−, 8 NO. Logic 0 → NC. V+ is 3–16 V (18 V abs max) and D16 clamps it at 12 V. |
| K1–K3 | G5V-2-H1 DC12 | Omron K046-E1-06 p.4 (bottom view) | Coil 1–16, A: COM 4 / NC 6 / NO 8, B: COM 13 / NC 11 / NO 9. The footprint is the correct top-view mirror, and the asymmetric pitch prevents reversed insertion. **K2 de-energised = halves bridged (fail-safe).** |
| Q1, Q2 | DMN3200U-7 | Diodes p.1 | 1 G, 2 S, 3 D, not mirrored. Q2's gate got 3.0 V from R9/R10 (SPICE ✓), and gets 2.5 V since R10 became 3.3 kΩ on 11-10; Vgs(th) max is 1.0 V. |
| Q3 | DMP4015SSS-13 | Diodes p.1–2 | S pads 1–3 = VIN, G 4, D 5–8 = VBAT_F. Correct reverse-polarity orientation; VGSS ±25 V, VDSS −40 V. |
| D1–D3, D17 | PESD1CAN | Nexperia Table 2 | Lines on 1/2, common on 3 → GND. |
| D10, D11 | PESD1FLEX (C2905640 is **TECH PUBLIC**) | TECH PUBLIC datasheet p.1 | Lines on 1/2, common on 3 → GND. VRWM 24 V. |
| D9, CR1/CR2, D12–D16 | SMAJ16A, 1N4148W, DSK14, BZT52C | Symbol graphics + footprint pad-1 cathode marks | Every cathode is where intended (TVS/clamps to VIN or the clamped node, flybacks to VIN, D12 toward the XIAO, D15 blocking back-feed). |
| Y1 | HY40MSMD2016DA1R30 | Huiyuan p.2 | Crystal on 1/3, GND/lid on 2/4, matching Crystal_GND24 and the 2016 footprint. |
| J1–J4 | DX07, Molex Micro-Fit+, MX34 ×2 | Original built board (`main`) | Pad geometry, rotation and side identical. Net changes are exactly the intended ones (RADAR tap removed, FlexRay 29/30 split, J2.4 → fused VBAT). J2 silk "VIN/GND" sits over pads 4/3. |
| BOM | 39 C-numbers | LCSC product API | **All 39 resolve to exactly the MFG Part # on the footprint.** |

**Power tree**

```
J2.4 VBAT ─ F1 3 A T ─ VBAT_F ─ Q3 P-FET (D14 16 V Vgs clamp, R20) ─ VIN ─┬ D9 SMAJ16A clamp
                                                                          ├ J1 VBUS ×4 → comma
                                                                          ├ U3 LM53600LQ 5 V/2.1 MHz ─ +5V ─┬ U5/U6 VCC, U1/U2 VL
                                                                          │                                 └ D12 ─ XIAO 5V ─ XIAO 3V3 ─ +3V3 → U5/U6 VIO, U8 VIO, R19
                                                                          ├ U8 VSUP (internal LDO → VCCOUT/C19)
                                                                          ├ K1 coil (always on); K2+K3 coils via Q2
                                                                          └ D15 ─ R21 3.3k ─ SW_VCC (D16 12 V) → U1/U2 V+
```

Q3 → In2 VIN island through **6 × 0.3 mm vias**; J1 VBUS fed through its plated B4/B9 pins in that island; VBAT 2.0 mm, VBAT_F 1.5 mm. Fine for the 3 A fuse rating with 1 oz inner copper.

**Layout**

- **U3:**
  - CIN_HF C12 is 2.2 mm from VIN/GND; C8 4.7 µF at 4.9 mm; VCC cap 2.2 mm, FB cap C27 3.0 mm, BOOT 3.0 mm.
  - AGND (pin 5) and GND (pin 10) are tied straight into the EP on F.Cu.
  - The EP has 3 vias; the SW node is one short 0.8 mm run.
- **U8 caps:** VSUP C24 2.0 mm, VCCOUT C19 2.5 mm, FLTR C20 4.3 mm, VIO C21 6.1 mm. The CAN split termination sits at the pins and the EP has 6 vias.
- **Transceiver decoupling:** 1.9–2.5 mm on all four pins (U5/U6 VCC and VIO).
- **Planes:** after a fresh fill, In1 GND is one continuous island. In2 is +5V with a single VIN island. There is no +3V3 zone.
- **Mechanical / DFM:**
  - Every footprint has a courtyard (DRC's missing-courtyard check is off in your rules, so this was checked separately).
  - Every SMD pad gets paste.
  - Pad copper is at least 0.83 mm from the edge and tracks at least 0.5 mm.
  - No copper within 3.5 mm of the M3 holes.
- **Library differences:** 9 of the 10 `lib_footprint_mismatch` footprints have identical pads; only U8 differs, as decided.

**Native checks**

- ERC: 0 violations.
- DRC: 0 errors, 0 unconnected, same result with refilled zones; 10 library-mismatch warnings.
- Parity: only H1–H4, which are board-only.

**SPICE (ngspice)**

17 pass, 1 warn:
- R9/R10 gate drive gives 3.0 V (with R10 = 10 kΩ; 2.5 V by calculation since 11-10).
- Split terminations are as designed.
- Decoupling impedance ≤ 6 mΩ at 1 MHz on +5V/VIN.
- +5V inrush is ~0.16 A.
- The Y1 warning is a model artifact (no motional parameters).

**Thermal**

The analyzer skipped (no dissipation data), so this is a hand estimate:

| Part | Estimated dissipation | Note |
|---|---|---|
| U3 | ~0.2 W | Tj ≈ ambient + 15–20 °C |
| Q3 | ~0.06 W | at 2 A |
| TCAN4550 internal LDO | ≤ ~0.3 W | worst case, continuous dominant |
| K1 coil | 150 mW | continuous |

No thermal concerns.

## 6. Analyzer findings judged false positives

| Source | Finding | Why it's a false positive |
|---|---|---|
| Schematic | NT-001 / PP-001 on U3 | kicad-cli netlist has AGND, EN, PAD and VIN connected. |
| Schematic | PP-001 on U1/U2 V+ | Fed VIN → D15 → R21; the analyzer's 2-hop search misses it. |
| Schematic | PU-001 on U3 EN | Tied to VIN. |
| Schematic | RS-001 VBAT/VBAT_F | Rails enter from J2. |
| Schematic | SS-001 | MPNs are in `MFG Part #`. |
| Cross-domain | PS-002 / RP-002 "plane splits", "SPI crosses VIN gap" | One GND island; SPI runs at y = 76–102 mm, VIN island starts at y ≥ 109.5 mm. |
| EMC | GP-001 ×48, SU-001/002 | In2 is a power plane, not a signal layer. |
| PCB | DFM-001/002 | 0.3/0.5 mm vias are JLC standard. |
| PCB | PM-002 | Connector overhang is intentional; pad copper is ≥ 0.83 mm from the edge. |
| PCB | TV-001 | TI's own land uses 4 small vias; U3 dissipation is ~0.2 W. |
| Gerber | GR-002 / GR-004 | Copper inset from the edge; paste count excludes THT pads and vias. |
| SPICE | Y1 warning | No crystal model. |

## 7. Previously decided (not re-raised)

- U8 perimeter pads 0.3 mm outward.
- R16 = 0 Ω.
- J1 shield tabs netless.
- Harness_GND isolated from board GND.
- No test points.
- XIAO pad 24 (your check, listed in §4).

## 8. Not performed / limits

- **Lifecycle audit not run.** MPNs live in `MFG Part #`, and there are no distributor API keys. LCSC stock was checked instead.
- **No datasheet for the Coilcraft XAL4040, Walter fuse or Molex/JAE mechanicals.** The connectors were verified against the built board instead.
- **JLC rotation offsets were not checked.** Inspect U3, U5, U6, U8, Q1–Q3, all diodes, Y1 and J1 in JLC's placement preview before paying.
- **Not verifiable from files:** FlexRay and CAN signal integrity on the real harness, oscillator start-up at temperature, and comma-side termination. These are bring-up tests.
