"""Bottom tray of the Passthrough HarnessBox two-part enclosure.

Reference geometry, taken 2026-08-28 from Passthrough_HarnessBox_Final.step
and the matching .kicad_pcb (case/Passthrough_HarnessBox_Final.step is a
local copy of the PCB export used only for inspection/measurement, not
imported into this model):
  - Board outline (Edge.Cuts gr_rect): 73.0 x 43.0 mm, ~1.53 mm thick.
  - Two JAE MX34032NF4 harness connectors, one mounted at each end of the
    board, each overhanging its board edge by ~11.34 mm in X, spanning
    ~41.1 mm in Y, and protruding ~16.1 mm above / ~1.6 mm below the PCB.
  - One JAE DX07S024XJ1R1100 USB-C connector (J1) and one Molex 2125280400
    4-conductor connector (J2), both right-angle, mounted near the board's
    -Y edge in this model's frame and both overhanging that edge toward -Y.
    Positions/heights taken directly from the imported STEP occurrences
    (see USB_*/MOLEX_* constants below).
  - Two existing M3 (3.2 mm) mounting holes drawn on Edge.Cuts at kicad
    coords (129.5,76) and (155,100); board rect corner (106.5,69.5) to
    (179.5,112.5).

Origin: case center in X/Y, case exterior bottom face at Z=0. Board is
centered in X/Y to match the connector overhang (symmetric ~11.34 mm/side).
+Z is up.

Frame note: this file's (X,Y) is the imported PCB STEP's own frame, just
recentered on the board (case_x = STEP_x - 143, case_y = STEP_y + 91,
case_z = STEP_z + PCB_BOTTOM_Z) -- a pure translation, so the real PCB STEP
can be dropped in with only a translation, no rotation/mirror. KiCad's
2D editor uses a Y-down layout convention (STEP_y = -kicad_y for this
export), so any position taken from kicad_pcb coordinates must go through
that negation before use here -- do not subtract a kicad-frame board
center directly, that silently mirrors the Y axis (caught and fixed
2026-08-28: PCB_HOLES and the USB/Molex cutout wall were both on the wrong
side of Y until this was traced against the imported STEP's own measured
occurrence positions).
"""

from build123d import Align, Box, BuildPart, Cylinder, Locations, Mode

# ---- PCB / connector reference dimensions (mm) -----------------------------
BOARD_X = 73.0
BOARD_Y = 43.0
BOARD_T = 1.6

CONN_Y = 41.1
CONN_Z_BELOW = 1.6
CONN_Z_ABOVE = 16.1

PCB_HOLES = ((-13.5, 15.0), (12.0, -9.0))

# USB-C (J1) and Molex (J2) STEP bounding boxes, in this file's case-local
# frame (case_x = STEP_x - 143, case_y = STEP_y + 91). Z stays relative to
# the PCB bottom-copper plane (0), same as the connector constants above.
USB_X = (-16.0025, -6.6025)
USB_Y = (-23.5325, -13.7725)
USB_Z = (0.8106, 4.9206)

MOLEX_X = (1.4722, 8.3222)
MOLEX_Y = (-23.9, -11.68)
MOLEX_Z = (-1.6344, 10.4156)

# ---- Case parameters (mm) ---------------------------------------------------
WALL_T = 2.4
FLOOR_T = 2.4
LID_T = 2.4
STANDOFF_H = 8.0          # PCB standoff height (clears an M3 heat-set insert)
CEIL_CLEARANCE = 2.5      # clearance above tallest component to the lid
CUTOUT_CLEARANCE = 0.6    # clearance around each connector cutout window

INTERIOR_X = 100.0
INTERIOR_Y = 60.0         # widened vs. the 45.4 mm assembly footprint so the
                           # corner screw bosses clear the wide connectors

BOSS_OD = 9.0              # corner (case-to-case) screw boss outer diameter
STANDOFF_OD = 7.0          # PCB standoff outer diameter (kept slim: hole B
                           # sits close to the Molex connector's underside)
INSERT_DIA = 4.2           # M3 brass heat-set insert bore diameter
INSERT_DEPTH = 6.0         # M3 heat-set insert bore depth
OVERSHOOT = 0.5            # boolean-tool overshoot past a target face

# ---- Derived dimensions -----------------------------------------------------
EXTERIOR_X = INTERIOR_X + 2 * WALL_T
EXTERIOR_Y = INTERIOR_Y + 2 * WALL_T

FLOOR_TOP_Z = FLOOR_T
STANDOFF_TOP_Z = FLOOR_TOP_Z + STANDOFF_H
PCB_BOTTOM_Z = STANDOFF_TOP_Z
PCB_TOP_Z = PCB_BOTTOM_Z + BOARD_T
CONN_BOTTOM_Z = PCB_BOTTOM_Z - CONN_Z_BELOW
CONN_TOP_Z = PCB_TOP_Z + CONN_Z_ABOVE
RIM_Z = CONN_TOP_Z + CEIL_CLEARANCE          # bottom-part rim / total height
INTERIOR_Z = RIM_Z - FLOOR_TOP_Z

CUTOUT_Z_MIN = CONN_BOTTOM_Z - CUTOUT_CLEARANCE
CUTOUT_Z_MAX = CONN_TOP_Z + CUTOUT_CLEARANCE
CUTOUT_Y_HALF = CONN_Y / 2 + CUTOUT_CLEARANCE


def _side_cutout(x_range, z_range):
    """Return (x_center, x_size, z_center, z_size) for a +Y wall cutout,
    expanded by CUTOUT_CLEARANCE and converting relative Z to absolute."""
    x_lo, x_hi = x_range[0] - CUTOUT_CLEARANCE, x_range[1] + CUTOUT_CLEARANCE
    z_lo = PCB_BOTTOM_Z + z_range[0] - CUTOUT_CLEARANCE
    z_hi = PCB_BOTTOM_Z + z_range[1] + CUTOUT_CLEARANCE
    return (x_lo + x_hi) / 2, x_hi - x_lo, (z_lo + z_hi) / 2, z_hi - z_lo


USB_CUTOUT = _side_cutout(USB_X, USB_Z)
MOLEX_CUTOUT = _side_cutout(MOLEX_X, MOLEX_Z)
SIDE_WALL_Y_CENTER = -(INTERIOR_Y / 2 + WALL_T / 2)  # USB/Molex overhang -Y
SIDE_CUTOUT_Y_SIZE = WALL_T + 2 * OVERSHOOT

BOSS_X = EXTERIOR_X / 2 - BOSS_OD / 2
BOSS_Y = EXTERIOR_Y / 2 - BOSS_OD / 2
BOSS_XY = tuple((sx * BOSS_X, sy * BOSS_Y) for sx in (-1, 1) for sy in (-1, 1))


def gen_step():
    with BuildPart() as bottom:
        # Outer shell.
        Box(
            EXTERIOR_X,
            EXTERIOR_Y,
            RIM_Z,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Hollow out the interior cavity; overshoot the top so the tray
        # opens cleanly rather than leaving a thin ceiling.
        with Locations((0, 0, FLOOR_TOP_Z)):
            Box(
                INTERIOR_X,
                INTERIOR_Y,
                INTERIOR_Z + 2 * OVERSHOOT,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Four corner screw bosses (M3 heat-set inserts), fused into the
        # wall corners. Overshoot into the solid floor for a clean union.
        boss_h = RIM_Z - (FLOOR_TOP_Z - OVERSHOOT)
        with Locations(*[(x, y, FLOOR_TOP_Z - OVERSHOOT) for x, y in BOSS_XY]):
            Cylinder(
                BOSS_OD / 2,
                boss_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # Two PCB mounting standoffs (M3 heat-set inserts) at the board's
        # existing mounting-hole positions.
        standoff_h = STANDOFF_H + OVERSHOOT
        with Locations(*[(x, y, FLOOR_TOP_Z - OVERSHOOT) for x, y in PCB_HOLES]):
            Cylinder(
                STANDOFF_OD / 2,
                standoff_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # End-wall cutouts so the harness connectors are accessible from
        # outside the case. Overshoot through both wall faces.
        cutout_x_size = WALL_T + 2 * OVERSHOOT
        cutout_y_size = 2 * CUTOUT_Y_HALF
        cutout_z_size = CUTOUT_Z_MAX - CUTOUT_Z_MIN
        cutout_x_center = INTERIOR_X / 2 + WALL_T / 2
        cutout_z_center = (CUTOUT_Z_MIN + CUTOUT_Z_MAX) / 2
        with Locations(
            (cutout_x_center, 0, cutout_z_center),
            (-cutout_x_center, 0, cutout_z_center),
        ):
            Box(
                cutout_x_size,
                cutout_y_size,
                cutout_z_size,
                mode=Mode.SUBTRACT,
            )

        # Side-wall cutouts (-Y wall) for the USB-C (J1) and Molex (J2)
        # connectors, which overhang the board's -Y edge.
        for x_center, x_size, z_center, z_size in (USB_CUTOUT, MOLEX_CUTOUT):
            with Locations((x_center, SIDE_WALL_Y_CENTER, z_center)):
                Box(
                    x_size,
                    SIDE_CUTOUT_Y_SIZE,
                    z_size,
                    mode=Mode.SUBTRACT,
                )

        # Heat-set insert bores, drilled blind from each boss/standoff top
        # face. Overshoot upward past the entry face for a clean cut.
        corner_bore_pts = [(x, y, RIM_Z + OVERSHOOT) for x, y in BOSS_XY]
        standoff_bore_pts = [
            (x, y, STANDOFF_TOP_Z + OVERSHOOT) for x, y in PCB_HOLES
        ]
        with Locations(*(corner_bore_pts + standoff_bore_pts)):
            Cylinder(
                INSERT_DIA / 2,
                INSERT_DEPTH + OVERSHOOT,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )

    part = bottom.part
    part.label = "case_bottom"
    return part
