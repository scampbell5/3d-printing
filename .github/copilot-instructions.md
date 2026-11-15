# 3D-printing repository instructions for Copilot

Read the root [AGENTS.md](../AGENTS.md) and [design standards](../docs/DESIGN_STANDARDS.md) before suggesting or editing new designs. Follow the existing `BUILDING_DESIGNS.md` manifest schema rather than inventing one.

Core rules: use root **uv** groups/lockfile, not pip requirements; put new design files beneath `designs/<category>/<slug>/`; write new CAD sources into `cad/` and printed meshes into `stl/`; update each design's README, preview images, print orientation and license/attribution; do not claim slicer/physical verification based solely on watertight mesh checks.

Run or clearly report omissions for the validation commands in AGENTS.md. Treat existing remix licenses as project-specific, never as a blanket license for new designs.
