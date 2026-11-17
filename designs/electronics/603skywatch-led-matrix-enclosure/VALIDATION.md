# 603Skywatch Enclosure v2 — Validation

Generated from `skywatch_enclosure_v2.scad` with OpenSCAD.

## Exported STL checks

| Part | Watertight | Bounding box |
|---|---:|---:|
| Front display cassette | Yes | 267 × 139 × 14.3 mm |
| Rear electronics case | Yes | 267 × 139 × 39 mm |
| Left foot | Yes | 21 × 47 × 36 mm |
| Right foot | Yes | 21 × 47 × 36 mm |
| Snap test coupon | Yes | 42 × 24 × 14 mm |

The original package reports all STL meshes were reloaded with Trimesh after export and reported watertight. These results have not been independently rerun as part of this PR.

## Still requires physical measurement

This is a printable prototype, not a final production enclosure. Verify panel W/H/depth, rear brass-insert spacing/thread, HUB75 and power connector projection, WF2 component envelope, and DC jack diameter. Print the snap coupon first to tune PETG snap clearance.
