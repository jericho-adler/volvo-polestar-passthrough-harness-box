# Volvo/Polestar Passthrough Harness Box

# 🚧 IN DEVELOPMENT 🚧

> [!WARNING]
> **This branch (`flexray-integration`) is work in progress and has not been built or tested in a vehicle.**
> The FlexRay schematic is complete and ERC-clean, but **the PCB is unrouted** — footprints are placed,
> no copper is laid. Do not fabricate from this branch. The `main` branch holds the last stable design.


A small automotive ADAS harness pass-through box designed in KiCad, built for **Volvo/Polestar** vehicles. It sits inline on the camera/VCU harness and provides a fail-safe electrical bypass plus signal switching, protected against automotive power-rail transients and ESD.
- **Board:** 98.0 × 58.0 mm, 4-layer (F.Cu / In1.Cu=GND / In2.Cu / B.Cu), 80 components, 126 nets.
  Corners are radiused 3.8 mm, concentric with the four M3 mounting holes
- **Power inputs:** VBAT and VOBD, each TVS-protected (SMAJ16A) and OR'd through Schottky diodes (STPS2H100ZFY) into a combined VIN rail
- **Fail-safe passthrough:** a DPDT relay (Omron G5V-2-H1 DC12) wired so the normally-closed contacts connect CAMERA↔VCU when the box is unpowered, and open when VIN is applied. The coil sits directly across VIN/GND, so the high-sensitivity `-H1` variant is used: 150 mW instead of 500 mW, and a 180% max coil voltage (21.6 V) that tolerates a running alternator rail
- **Signal switching:** two DG419 SPDT analog switches route CAMERA/VCU signal pairs under control of an `SBU 1` logic input
- **Protection:** PESD1CAN ESD diodes on signal lines at the connectors
- **Connectors:** JAE MX34032NF4 (32-pin automotive, ×2) for the harness pass-through, plus a USB-C and Molex connector

## FlexRay MITM (this branch)

This branch adds a **man-in-the-middle tap on the vehicle's FlexRay bus** (harness pins 29 & 30) to the
existing pass-through box, so the bus can be observed and rewritten in transit rather than merely bridged.

The FlexRay pair no longer runs straight from `J3` (vehicle) to `J4` (ECU/module). It is cut into two
independent halves — `FR_VEH_BP`/`FR_VEH_BM` and `FR_ECU_BP`/`FR_ECU_BM` — each terminated in its own
transceiver, with the microcontroller between them relaying frames.

- **Controller:** Seeed **XIAO RP2350** module (`U4`), running [dynm/pico-flexray](https://github.com/dynm/pico-flexray)
- **Transceivers:** two **NXP TJA1082** (`U5` vehicle side, `U6` ECU side), one per bus half. Logic pins run
  to the XIAO as `FR1_*`/`FR2_*` (RXD/TXD/TXEN) with shared `FR_BGE` and `FR_STBN`; `VCC` on +5 V, `VIO` on
  +3.3 V so the module's own LDO sets the logic level
- **Fail-safe bypass:** a second DPDT relay `K2` (Omron G5V-2-H1 DC12) whose **normally-closed** contacts bridge
  the two halves back together. De-energized — unpowered box, crashed firmware, or the XIAO simply not driving
  it — the vehicle and ECU are wired directly to each other and the bus behaves as if the box were not there.
  Energizing it **splits** the bus into the MITM path. Driven from the XIAO via `FR_BYPASS_CTRL` → `Q2`
  (DMN3200U) with a 1N4148 flyback diode
- **Power:** `U3` **LM53600-Q1** buck (12 V → 5 V, always-on, forced PWM) with a 10 µH Coilcraft XAL4040
  inductor, feeding the XIAO's 5 V input; the XIAO's 3V3 regulator in turn supplies transceiver `VIO`
- **Protection:** PESD1FLEX ESD diodes (`D10`, `D11`) on each bus half at its connector

The original harness board — relay `K1` plus the two DG419 analog switches — is
**unchanged** and operates independently of the FlexRay circuit.

### Mechanical and DRC notes

- **Outline:** 98.0 × 58.0 mm. The four corners are arcs of **R3.8 mm** whose centres sit exactly on the
  mounting-hole centres, so each corner is concentric with its hole.
- **Mounting:** 4 × M3 holes, 3.2 mm drill, **non-plated**, inset 3.8 mm from both edges (`H1`–`H4`).
  They are deliberately non-plated so the enclosure screws do not bond chassis to board ground — harness
  pin 13 is not board GND. They exist on the PCB only, with no schematic symbols, so do not tick
  *delete footprints with no symbol* when running **Update PCB from Schematic**.
- **Edge-mounted connectors:** `J1`–`J4` overhang the board edge by design. `J3`/`J4` (JAE MX34032NF4)
  project 7.8 mm past the left and right edges respectively; their pads remain fully on the board.
- **Custom DRC rule** (`Polestar_Flexray.kicad_dru`): exempts intra-footprint pad spacing on `U3` and `U8`
  only. Both footprints reproduce the manufacturer's own land pattern exactly — `U8` matches TI drawing
  4225320/A (RGY0020A), which places the exposed pad 0.025 mm from every perimeter pin. Those pads are
  non-solder-mask-defined, so bridging is controlled by the stencil (78% paste coverage on pad 21) rather
  than by copper spacing. The rule is scoped to `U3`/`U8` so every other footprint is still checked normally.

### Status

| | |
|---|---|
| Schematic | Complete — 80 components, 0 ERC errors |
| Footprints & 3D models | All 80 components assigned and resolving |
| Placement | Complete — 84 footprints (80 components + 4 mounting holes) on a 98 × 58 mm outline |
| Routing | **Not started** — 0 tracks, 0 vias; In1.Cu ground pour defined but unfilled |
| DRC | 0 clearance, 0 courtyard-overlap, 0 copper-to-edge, 0 invalid-outline. Remaining items are 239 unrouted ratsnest connections and ~138 cosmetic silkscreen warnings |
| Firmware | In Progress with Dev Board |
| Bench / vehicle testing | In Progress with Dev Board |

Project files live in [`PCB Files/`](PCB%20Files/) as `Polestar_Flexray.kicad_{pro,sch,pcb,dru}`.

> [!IMPORTANT]
> `Polestar_Flexray.kicad_dru` carries a custom DRC rule and must be kept beside the project files.
> Without it the board reports 26 false clearance errors. See **Mechanical and DRC notes** above.


## License

Licensed under the [CERN Open Hardware Licence Version 2 - Strongly Reciprocal](LICENSE) (CERN-OHL-S-2.0).

## Disclaimer

This is a community hardware design shared as-is, with no warranty. It is designed specifically for Volvo/Polestar vehicles — using it on other platforms is unverified. **Use at your own risk.** Review the design review's blockers before fabricating or installing in a vehicle.
