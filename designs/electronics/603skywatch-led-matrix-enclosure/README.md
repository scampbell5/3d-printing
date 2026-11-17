# 603Skywatch LED matrix enclosure — V2 prototype

**Status: unprinted; fit unverified.**

Prototype enclosure for a nominal 256 × 128 mm P4 64×32 HUB75 LED matrix, Huidu HD-WF2 controller, WAGO 221-415 connectors and external 5 V supply.

## Design concept

- Screwless front cassette, with the panel installed from the rear
- Rear electronics tub with controller and connector pockets, ventilation and DC jack opening
- Four snap features and two concealed safety-screw locations
- Separate left and right removable desktop feet

## Prototype limitations

The estimated overall shell footprint is 267 × 139 mm, very close to the QIDI Q2's nominal 270 mm width. Before printing, confirm usable build volume and exclusion zones in the slicer. Measure the actual LED panel, insert positions, connectors, controller and DC jack. Test snap-fit clearance before committing to a full PETG print. Support-free printing and physical fit have not been verified.

## Source and printable files

The source package is being reviewed for inclusion in this branch. This initial documentation commit **does not yet include** the OpenSCAD source, STL meshes, or CAD illustrations. Do not treat this folder as a ready-to-print release.

The planned files are:

- `cad/skywatch-enclosure-v2.scad`
- `stl/front-display-cassette.stl`
- `stl/rear-electronics-case.stl`
- `stl/left-foot.stl`, `stl/right-foot.stl`
- `stl/snap-test-coupon.stl`
- `images/` — concept CAD illustrations, not physical print photos

## Safety and publication

Verify polarity, strain relief, insulation, and connector ratings before powering the assembly. A redistribution license must be explicitly selected by the project owner before merging or publishing a printable release. No third-party geometry is claimed.
