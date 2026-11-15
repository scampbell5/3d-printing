#!/usr/bin/env python3
"""Quick structural checks for the latest STL files (not a slicer/fit simulation)."""
from pathlib import Path
import sys
import trimesh

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'holder': ROOT / 'stl' / 'holder.stl',
    'lid, print oriented': ROOT / 'stl' / 'sliding-lid-print-face-down.stl',
    'lid, assembled': ROOT / 'stl' / 'sliding-lid-assembled.stl',
}
failed = False
for name, path in FILES.items():
    try:
        mesh = trimesh.load_mesh(path, force='mesh')
        parts = mesh.split(only_watertight=False)
        passed = mesh.is_watertight and len(parts) == 1
        print(f"{'PASS' if passed else 'FAIL'} {name}: watertight={mesh.is_watertight}, "
              f"connected_components={len(parts)}, dimensions_mm={mesh.extents.round(2).tolist()}, "
              f"triangles={len(mesh.faces):,}")
        failed |= not passed
    except Exception as exc:
        print(f'FAIL {name}: {exc}')
        failed = True

print('\nStructural STL checks only: not a physical-fit, lock-strength, or support-free slicing validation.')
sys.exit(1 if failed else 0)
