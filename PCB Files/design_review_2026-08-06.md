# Design Review — Passthrough_HarnessBox

**Date:** 2026-08-06 | **Run:** `analysis/2026-08-06_1457/` | **KiCad:** 10.0 (schematic v20260306)
**Board:** 73.0 × 43.0 mm, 4-layer (F.Cu / In1.Cu=GND / In2.Cu / B.Cu), 25 components, 73 nets, single sheet.

## What this board is

A small automotive ADAS harness pass-through box. Two power inputs (VBAT, VOBD) are TVS-protected (SMAJ16A) and OR'd through Schottky diodes (STPS2H100ZFY) into a combined VIN rail. A DPDT relay (Panasonic TQ2-12V) sits between camera and VCU signal pairs, wired so the **normally-closed contacts connect CAMERA↔VCU when unpowered** (fail-safe pass-through) and open when VIN is applied — the normally-open throws are left unconnected. Two DG419 SPDT analog switches (U1/U2) route CAMERA/VCU signal pairs under control of an `SBU 1` logic input. PESD1CAN ESD diodes protect the signal lines at the connectors. A small MOSFET (Q1) low-side-switches an unrelated `SBU 2` line, gated by a voltage divider (R2/R3) off `SBU 1`.

## Verification basis

- **No datasheets directory existed and no BOM part carries an MPN property** (`DS-001`, `SS-001` — both `error`/`high`). Per this skill's contract, findings below are **consistency checks only** unless explicitly marked "datasheet-verified."
- Automated sync (LCSC, no-auth) found **zero** matches — most parts (JAE/Molex/Phoenix automotive connectors, custom `My_Components` diodes) aren't in that catalog, and no DigiKey/Mouser/element14 API keys are configured in this environment.
- To close the gap on the three parts where a wrong pin assumption would be board-killing, I manually pulled the actual manufacturer datasheets via web search and verified pin-by-pin:

| Part | Ref | Library assumption | Datasheet (source) | Result |
|---|---|---|---|---|
| DMN3200U-7 (Diodes Inc, SOT-23 N-MOSFET) | Q1 | Pin1=G, Pin2=S, Pin3=D | [diodes.com DS31188 Rev.7](https://www.diodes.com/datasheet/download/DMN3200U.pdf) | **Match** |
| DG419LEDY-T1-GE4 (Vishay, SOIC-8 SPDT switch) | U1, U2 | 1=COM,2=NC,3=GND,4=V+,5=VL,6=IN,7=V-,8=NO | [Vishay Doc 70051 Rev E](https://www.vishay.com/docs/70051/dg417.pdf), p.1 pin diagram | **Match** — datasheet calls pins 1/2/8 "D/S1/S2"; library's COM/NC/NO are just a naming choice for the same pole/throw terminals. Pins 3–7 (GND,V+,VL,IN,V-) match exactly. |
| TQ2-12V (Panasonic, 10-pin DPDT relay) | K1 | Pins 1 & 10 = coil (from netlist: pin1→VIN, pin10→GND) | [Panasonic ASCTB14E catalog](https://mediap.industry.panasonic.eu/assets/download-files/import/ds_61020_en_tq.pdf), p.10 "Schematic (Bottom view)" | **Match** — pins 1(+)/10(−) are the coil; pins 2/9=COM, 3/8=NC, 4/7=NO, 5/6=spare (unconnected), confirmed against the datasheet's bottom-view schematic diagram. |

No datasheet was found/verified for the passives, PESD1CAN, STPS2H100ZFY, SMAJ16A, or the connectors — those remain consistency-only.

- **SPICE**: no simulator (`ngspice`/`ltspice`/`xyce`) installed in this environment — skipped. The schematic has no filter/divider/gain circuit that would materially benefit anyway (R2/R3 is a simple 1:1 gate-bias divider).
- **Thermal**: ran, 0 findings — no components with computable power dissipation (no MPN-backed θJA data); not a meaningful result, treat as "not assessed."
- **Lifecycle audit**: not run — no MPNs to query.
- **Gerbers**: none exported in this project directory — not applicable.
- **Prior review**: none found in the project directory.

---

## Blockers before fab

| # | Finding | Severity | Detail |
|---|---|---|---|
| 1 | **SS-001** — 0/14 BOM lines have an MPN | High (sourcing) | Every connector, diode, and the relay/MOSFET/switches are `My_Components`/custom entries with no MPN field populated, even though real part numbers are embedded in the `Value` field (e.g. "DMN3200U-7"). Nothing here is orderable through the standard sourcing workflow as-is. **Fix:** copy the value-field part numbers into the MPN property (or run the `bom` skill) before ordering. |
| 2 | **FD-001** — 0 fiducials on F.Cu, 19 SMD parts | High (assembly) | No fiducials for pick-and-place vision alignment. Add ≥3 non-symmetric fiducials on F.Cu. |
| 3 | **DC-002** — U1 and U2 have no decoupling capacitor within 10mm | High (EMC/decoupling) | Both DG419 switches' V+/VL/V- pins have no local bypass cap in the layout. Add 100nF X7R close to each part's supply pins. |
| 4 | **ES-002** — No ground via within 3mm of D1 (PESD1CAN) | High (ESD) | D1's TVS ground return relies on a long path, undermining ESD clamp effectiveness. Add 1–2 ground vias directly at D1's ground pad. |
| 5 | **SU-001** — In2.Cu and B.Cu are adjacent signal layers with no reference plane between them | High (stackup) | Stackup is F.Cu(sig) / In1.Cu(GND) / In2.Cu(labeled "POWER" but typed as a signal layer, not a poured plane) / B.Cu(sig). In2/B.Cu neighbor each other directly — poor return-path control and crosstalk risk between those two layers. Worth revisiting the stackup or confirming In2.Cu is fully poured as a solid power plane (its `type` is currently "signal" in the KiCad layer table, not "power/plane"). |

## High-value warnings (not blockers, worth fixing)

- **GP-001 (17 error + 8 warning)** — 25 signal nets have <30% ground-plane coverage under their routing, the worst on several `J3` pins (5.7–23% coverage over 50–90mm of trace). All are low-speed automotive I/O (not flagged `is_high_speed_or_clock`), so radiated-emissions risk is lower than it would be for a clock/data line — but this is worth a look, since **only one zone exists on the whole board** (`zone_count: 1`). Confirm the GND pour on In1.Cu actually extends under J3/J4's fanout and re-run *Edit → Fill All Zones* before re-checking — stale fills are the most common cause of this class of finding.
- **BE-002 / BE-001** — Ground pour covers only ~36% of the board perimeter; three signals (incl. `Net-(J3-Pad31/32)`, `/SBU 2`) run within 0.03–0.08mm of the board edge with no plane underneath (slot-antenna risk).
- **PS-002** — VIN plane has 3 disconnected islands with 5 signals crossing the gaps (return-path discontinuity).
- **RS-001** (×2) — VBAT and VOBD rails have no `PWR_FLAG` and no recognized regulator source. This is almost certainly a false-positive pattern for a harness box (the rails legitimately originate off-board at J1/J6), but ERC will keep warning on every future edit unless you add `PWR_FLAG` symbols to these nets.
- **DFM-001/002** — 0.1mm annular ring on some pads/vias is below standard-tier (0.125mm) fab minimums; requires an advanced process tier or the values need increasing.
- **TE-001** — 0% test-point coverage across 72 signal nets. Fine for a low-volume/prototype run; add test points if this goes to ICT.
- **VP-001** — Via-in-pad at Q1 pin 2 (GND) is untented; solder can wick through during reflow. Tent or cap it.
- **IO-002** — J3/J4 (32-pin JAE MX34032NF4 connectors) have **zero** dedicated ground pins for 32 signal pins each. For automotive harness connectors carrying camera/VCU signal pairs this is a real return-path/EMC concern worth a second look at the connector's actual pinout (confirm this isn't a pin-mapping omission in the schematic — the analyzer only sees pins tied to a net literally named `GND`).

## Design behavior worth confirming with the designer (not a defect)

- **K1's unused NO throws.** Verified against the Panasonic datasheet: this relay is wired as a fail-safe passthrough — with no power applied, the NC contacts connect `CAMERA_H↔VCU_H` and `CAMERA_L↔VCU_L` directly. When VIN is applied, the relay energizes, the NC path opens, and **the NO throws (pins 4 & 7) are not wired to anything** — so the camera/VCU pairs simply go open-circuit rather than being rerouted somewhere else. If the intent is "disconnect for safety while powered," this is correct as built. If the intent was ever to route the camera feed to a diagnostic/alternate path when energized, the NO contacts need wiring — currently unused.
- **Q1's actual role.** Despite sitting near the relay, Q1 (MOSFET) does not drive the relay coil — the coil is hard-tied directly across VIN/GND with no switching, so K1 energizes purely on power presence. Q1 instead low-side-switches the unrelated `SBU 2` line via R7, gated by `SBU 1` through the R2/R3 divider. No flyback diode is needed here since the load (R7→SBU2) is resistive, not inductive — the automated `TR-DET` "no flyback diode" signal on Q1 is a non-issue once the actual net is traced (Q1 isn't driving the coil).
- **PM-002 edge overhangs (J1: 2.26mm, J3: 7.97mm, J4: 7.7mm, J5: 2.57mm)** — all four are at board edges consistent with their footprint orientation (J5 is a Phoenix pluggable terminal block that always mounts wire-side-out past the edge; J1/J3/J4 sit flush against the bottom/right board edges). This is very likely intentional panel/edge-mount placement for a harness enclosure, not a placement error — but confirm the 7.7–8mm overhangs on J3/J4 clear your enclosure cutout.

## Cross-domain / connectivity

- Component count: schematic 25 vs PCB 25 footprints — **matches**.
- All 73 schematic nets are present and routed on the PCB; `routing_complete: true`, 0 unrouted nets.
- Cross-analysis found only the one plane-split finding (PS-002) above; no ESD-gap (`EG-001`), decoupling-adequacy (`DA-001`), or schematic/PCB sync (`XV-00x`) findings — i.e. no swapped-pin or un-synced-net issues detected between schematic and layout.

## What was not performed / limits

- **Full MPN-backed verification** of PESD1CAN, STPS2H100ZFY, SMAJ16A, and the JAE/Molex/Phoenix connector pinouts — no datasheet obtained for these; findings involving them are internal-consistency checks only, not datasheet-confirmed.
- **SPICE simulation** — no simulator installed in this environment.
- **Lifecycle/obsolescence audit** — skipped, no MPNs to query.
- **Gerber-level DFM check** — no gerbers exported in this project.
- Trust rollup for this run: schematic/PCB findings are a mix of deterministic topology checks and heuristic EMC rules (EMC trust_level: **low**, 0% datasheet-backed provenance) — treat magnitude estimates (e.g. GP-001 coverage %, ES-001 overshoot voltage) as heuristic engineering estimates, not measured values.

---

**Bottom line:** routing is complete and schematic/PCB are in sync — no swapped-pin or missing-net bugs found, and the three riskiest pinout assumptions (relay coil, MOSFET, analog switch) check out against real datasheets. The blocking items before ordering are administrative/manufacturing (add MPNs, add fiducials) plus two layout hardening items (decoupling on U1/U2, ground via at D1) and one stackup question (In2/B.Cu adjacency) worth a deliberate answer rather than fixing.
