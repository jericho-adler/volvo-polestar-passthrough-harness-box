# Volvo/Polestar Passthrough Harness Box

A small automotive ADAS harness pass-through box designed in KiCad. It sits inline on the camera/VCU harness and provides a fail-safe electrical bypass plus signal switching, protected against automotive power-rail transients and ESD.

- **Board:** 73.0 × 43.0 mm, 4-layer (F.Cu / In1.Cu=GND / In2.Cu / B.Cu), 25 components, 73 nets
- **Power inputs:** VBAT and VOBD, each TVS-protected (SMAJ16A) and OR'd through Schottky diodes (STPS2H100ZFY) into a combined VIN rail
- **Fail-safe passthrough:** a DPDT relay (Panasonic TQ2-12V) wired so the normally-closed contacts connect CAMERA↔VCU when the box is unpowered, and open when VIN is applied
- **Signal switching:** two DG419 SPDT analog switches route CAMERA/VCU signal pairs under control of an `SBU 1` logic input
- **Protection:** PESD1CAN ESD diodes on signal lines at the connectors
- **Connectors:** JAE MX34032NF4 (32-pin automotive, ×2) for the harness pass-through, plus a USB-C and Molex connector

## Repository structure

```
PCB Files/     KiCad project (schematic, PCB, rules), design review, and analysis/datasheet data
3D models/     STEP export of the assembled board, plus the enclosure (case) design and renders
```

### PCB Files

- `Passthrough_HarnessBox.kicad_pro` / `.kicad_sch` / `.kicad_pcb` / `.kicad_dru` / `.kicad_prl` — the KiCad project. Open `Passthrough_HarnessBox.kicad_pro` in KiCad 10 to get started.
- `design_review_2026-08-06.md` — a design review covering schematic/PCB consistency, ESD/decoupling/stackup checks, and datasheet-verified pinouts for the relay, MOSFET, and analog switches. See "Blockers before fab" in that file before ordering boards.
- `analysis/` — machine-readable analysis output (schematic, PCB, EMC, thermal, cross-analysis) backing the design review.
- `datasheets/` — datasheet sync manifest for the BOM parts.

### 3D models

- `Passthrough_HarnessBox.step` — STEP export of the assembled board.
- `case/` — enclosure design (`Case_Top.step`, `Case_Bottom.step` and their parametric `.step.py` generator sources) plus render snapshots in `case/snapshots/`.

## Status

Routing is complete and the schematic/PCB are in sync. Before fabricating, see the "Blockers before fab" section of the design review — outstanding items include populating MPNs on the BOM, adding pick-and-place fiducials, decoupling capacitors near U1/U2, a ground via near D1, and confirming the In2.Cu/B.Cu stackup adjacency.

## Disclaimer

This is a community hardware design shared as-is, with no warranty. Review the design review's blockers before fabricating or installing in a vehicle.
