---
name: new-3d-design
description: Create or revise a new 3D printable project in this repository. Use for STL/CAD design creation, support-minimized parts, new Gridfinity or household organizers, printable enclosures, or adding a new design to the GitHub catalog.
---

# New design contributor workflow

Use this skill only when creating/revising a repository design. Start by reading these files at the repository root: `AGENTS.md`, `docs/DESIGN_STANDARDS.md`, `BUILDING_DESIGNS.md`, and the closest existing project's README.

## Steps

1. **Define design constraints**: intended purpose, print dimensions, printer bed, material, nozzle, orientation, assembly/mating tolerances, and whether Gridfinity or other standards apply. If unknown, mark assumptions in the README.
2. **Trace provenance**: if modifying someone else's STL, confirm exact author, source URL, license version, whether redistribution and modification are permitted, and required attribution. Stop before distributing restricted source files; keep per-design licensing separate.
3. **Create a project folder** at `designs/<category>/<slug>/`; use the human-readable README template at `templates/design/README.md`. Avoid placeholder STL files.
4. **Implement real geometry**: prefer editable CAD sources under `cad/` and export printable STLs to `stl/`. Preserve geometry/assembly contracts when revising; use chamfers and print orientation rather than unnecessary supports.
5. **Register automatic building only if it works**: create `design.json` in the exact `BUILDING_DESIGNS.md` schema. Reference a working `cad/*.py` script that uses `DESIGN_BUILD_OUTPUT_DIR`, outputs exact declared filenames, and uses a named group in the root `pyproject.toml` if additional packages are required. Run `uv lock` after dependency changes.
6. **Document and illustrate**: add clearly labeled *CAD renders* (not pretend photos), print settings, bill of parts, orientations, clearance assumptions, assembly steps, status and test notes. Credit third-party source materials.
7. **Validate**: from repository root run the uv/CI commands in AGENTS.md; run build for the specific design if applicable and feasible. Structural mesh validation alone is not support-free slicing, Gridfinity fit, lock strength or actual print-test evidence. Mark each separately.
8. **Submit**: describe changes, images, license terms, tests run, missing tests and remaining risks in the PR template.

## Pitfalls specific to this repository

- The existing saw-blade holder is a CC BY-NC-SA 4.0 remix. New original designs do **not** inherit that license automatically.
- The existing generic builder scans `designs/**/design.json`; a fake manifest fails CI. For manually created STLs, omit it.
- Git LFS is configured for large STL/CAD binary files. Avoid committing machine-specific G-code, private credentials, or oversized intermediate CAD volumes.
- Avoid modifying both committed STL files and scripts independently without updating their relationship in the README.
- Do not say "fully validated" unless physical evidence supports the precise claims.
