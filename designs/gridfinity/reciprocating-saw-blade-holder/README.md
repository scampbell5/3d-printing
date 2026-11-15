# Gridfinity reciprocating saw blade holder — sliding cover (V4)

**Status: prototype; first physical print underway.** This project is a noncommercial remix of [oly's Gridfinity Reciprocating Saw (AKA Sawzall) Blade Storage Bin](https://www.printables.com/model/358300-gridfinity-reciprocating-saw-aka-sawzall-blade-sto). See [ATTRIBUTION.md](ATTRIBUTION.md) and [LICENSE.md](LICENSE.md) before redistributing.

## Design overview

- Approx. 1 × 6 Gridfinity footprint, with three longitudinal blade compartments.
- Six redesigned shallow/chamfered Gridfinity-style feet.
- Sidewall-guided removable sleeve lid. No projecting exterior rails; intended to avoid tall tree supports.
- Small friction catches and a positive end stop. **Not** a mechanically captive locking dovetail.
- Holder is a single watertight mesh; cover is also a single watertight mesh.

## Files to print

| File | Purpose | Orientation |
|---|---|---|
| [`stl/holder.stl`](stl/holder.stl) | The organizer body | Gridfinity feet on build plate; compartments up |
| [`stl/sliding-lid-print-face-down.stl`](stl/sliding-lid-print-face-down.stl) | Preferred print version of cover | Already oriented: exterior face on build plate |
| [`stl/sliding-lid-assembled.stl`](stl/sliding-lid-assembled.stl) | Assembly/viewing version of cover | Not recommended as supplied for printing |

The V4 cover is approximately **257 mm long** including its pull tab. Confirm its fit on your actual Qidi Q2 build plate and any brim/purge margins.

## First test print

- Printer: Qidi Q2; 0.4 mm nozzle assumed.
- Holder: PLA; cover: PETG preferred to accommodate minor friction-catch flex.
- Starting profile: 0.20 mm layer height, 3 walls.
- Start with supports **off** and inspect all overhangs and bridges in QIDI Studio.
- Pause or abandon the print if unsupported features, warping, or poor adhesion appear.
- Don't force the lid on: fit and locking resistance are not physically validated yet.

### Validation status

GitHub Actions runs the included mesh checks on commits and pull requests; see the [repository CI documentation](../../../README.md#automated-validation-github-actions). CI cannot check physical assembly or slicer support requirements.

| Check | Status |
|---|---|
| Holder STL watertight and connected | Passed in prior checks; rerun `scripts/check_meshes.py` |
| Lid STL watertight and connected | Passed in prior checks; rerun `scripts/check_meshes.py` |
| Long projecting rail supports | Eliminated by geometry change |
| QIDI Studio support-free slice | **Not confirmed** |
| Gridfinity baseplate gauge fit | **Not confirmed** |
| Lid motion/retention and end stop | **Not confirmed** |
| Full physical print | **Pending** |

### After-print checklist

- [ ] Feet sit fully in the Gridfinity baseplate
- [ ] No unwanted supports / sagging
- [ ] Holder remains flat, walls intact
- [ ] Lid starts and slides without forcing
- [ ] Detents retain cover when closed
- [ ] Cover can be removed intentionally
- [ ] Photos and QIDI Studio `.3mf` project archived

## Editing and rebuilding

`cad/build_v4.py` is the original Python/CadQuery + voxel-merging workflow adapted to use **relative paths and isolated build output paths**. It is editable source but **not a fully parametric native CAD model**. It uses two included derived intermediate STL inputs:

- `cad/inputs/body_capped.stl` — upper storage body, derived from the original.
- `cad/inputs/chamfered_feet.stl` — remodeled lower feet.

`references/original_oly_storage_v6b.stl` contains the original input supplied for the remix and is included under the original model's Creative Commons terms, with attribution. The build script produces `stl/holder.stl`, `stl/sliding-lid-assembled.stl`, and `stl/sliding-lid-print-face-down.stl` and requires substantial RAM for voxel mesh reconstruction.

```bash
# From the repository root; requires a committed/generated uv.lock:
uv run --locked --no-default-groups --group ci python scripts/build_designs.py --design gridfinity/reciprocating-saw-blade-holder
# Validate committed outputs:
uv run --locked --no-default-groups --group ci python scripts/run_project_checks.py
```

The generic [Build designs workflow](../../../BUILDING_DESIGNS.md) discovers this project through `design.json`. Generated GitHub artifacts are separate from committed STLs. The checked-in STLs are the version prepared during the V4 design session. Rebuilding with different dependency versions may produce slightly different triangulation or dimensions. A slicer preview and real test print are still required.

## Design history

| Revision | Notes |
|---|---|
| V1 | Initial T-rail sliding lid experiment |
| V2 | Angled rail experiment; still created slicer supports |
| V3 | Chamfered-foot rebuild; mesh union problems |
| V3R | Unified watertight mesh; rail support problems persisted |
| **V4** | Removed external projecting rails, uses wall-guided removable cover |

Earlier revision artifacts are **not** included in this initial repository; Git history begins with V4. Use future Git commits/tags to track revisions.
