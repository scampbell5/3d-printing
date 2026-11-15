# Design standards

Use these conventions for **new projects** and when materially revising an existing design. They keep the repository navigable and make automated checks meaningful without pretending to replace slicer review or test prints.

## Directory convention

```text
designs/<category>/<kebab-case-design-name>/
├── README.md                   # REQUIRED: overview, print instructions, status
├── LICENSE.md                  # REQUIRED before public release: terms for this design
├── ATTRIBUTION.md              # REQUIRED for remixes/third-party sources
├── cad/                        # editable CAD source, build scripts, inputs
├── stl/                        # release candidates, not temporary meshes
├── slicer/                     # .3mf projects and slicer notes, not G-code
├── images/                     # renders, print photos, reference images with provenance
├── references/                 # third-party sources, only if licensed for redistribution
├── scripts/                    # optional per-design check_meshes.py
└── design.json                 # OPTIONAL; only for an actual working Python builder
```

Empty directories do not have to be created. Do not copy old model geometry or license files to start a new design.

## File and design rules

- Names: lowercase kebab-case for project directories and printable parts (`holder.stl`, `sliding-lid.stl`); image names describe what is shown (`assembled.png`, `bottom-feet.png`).
- Never silently change part dimensions, assembly orientation, or moving-part clearances. Document intended clearance *and* whether it was measured or tested.
- Prefer simple, support-minimized geometry, chamfers, and orientations designed for ordinary FDM printers. Requiring supports is acceptable when documented; don't hide it.
- Keep mesh quality separate from physical results: watertight, connected, positive-volume checks prove only limited STL integrity.
- Keep printable parts separate. Save .3mf **projects** if helpful, but exclude generated printer-specific G-code and machine credentials.
- Document the printer, material, nozzle size, layer height, walls, support setting, orientation, brim/adhesion, and any slicer caveats when known. Mark unknowns rather than guessing.

## Build contract

See [BUILDING_DESIGNS.md](../BUILDING_DESIGNS.md) for the authoritative schema. If and only if a working Python CAD build exists, register it with `design.json`; the manifest's `id` must equal the directory path after `designs/`. Keep outputs exactly as declared and write into `DESIGN_BUILD_OUTPUT_DIR` (use `DESIGN_BUILD_WORK_DIR` for intermediates). Add custom packages to root `pyproject.toml` as a named uv dependency group, run `uv lock`, and commit the lockfile.

**Don't** add a dummy `design.json`: `scripts/build_designs.py --check` validates every manifest and will fail if the referenced build script or uv group is missing. A manually created/edited STL design can be contributed without a manifest; its files under `stl/` are still checked by global STL validation.

## Required project README

Use [templates/design/README.md](../templates/design/README.md) and fill the fields that apply: what it does, clear image/gallery, files and print orientations, assembly, dimensional assumptions, validation statuses, print-test observations, build/source process, version history and attribution links. Do not show AI images as photographs of actual prints. Label CAD renders and physical photos honestly.

## Licensing and third-party work

This repository has **no blanket license**. For every published design, check the creator/rights holder and exact license version, record source URLs and modification history, comply with attribution / ShareAlike / noncommercial restrictions, and only include third-party original geometry when redistribution is permitted. AI-generated content does not eliminate third-party copyright obligations. GitHub publication is redistribution.

## Review gates

1. **Source**: traced and allowed to share, with appropriate per-design licensing.
2. **Mesh**: STLs pass available repository validation (see AGENTS.md).
3. **Slicer**: intended orientation reviewed, supports/bridges checked, footprint and bed clearance checked if claimed.
4. **Physical**: dimensional fit, assembly, retention and repeated motion checked when claimed.
5. **Docs**: screenshots/photos labeled, license/credits complete, current status marked honestly.

Only mark a design "print-tested" or "production-ready" after a physical run confirms the relevant claims. CI does not certify safety or fit.
