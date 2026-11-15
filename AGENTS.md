# Instructions for AI contributors

This is a multi-design 3D-printing repository, not a single CAD application. Read this file before changing CAD scripts, STL files, build tooling, or documentation.

## Start here

- [QUICKSTART.md](QUICKSTART.md): first-time onboarding for people using this repository and AI assistants. When helping someone new, begin with their goal rather than assuming they need a Python environment.

- [CONTRIBUTING.md](CONTRIBUTING.md): how to submit a design or improvement.
- [docs/DESIGN_STANDARDS.md](docs/DESIGN_STANDARDS.md): canonical per-design layout, publishing criteria, print-test evidence, and licensing rules.
- [BUILDING_DESIGNS.md](BUILDING_DESIGNS.md): the *actual* `design.json` schema, uv groups, and build commands.
- [README.md](README.md): repository overview. Read the target design's own `README.md`, `LICENSE.md`, and `ATTRIBUTION.md` before modifying it.

## Non-negotiable rules

1. New projects go under `designs/<category>/<kebab-case-name>/`. Never put a new design in the repository root.
2. Keep human-editable CAD/source in `cad/`, committed publishable meshes in `stl/`, renders/photos in `images/`, slicer projects in `slicer/`, and third-party sources in `references/` **only when redistribution is allowed**.
3. Use `uv` and the root `pyproject.toml` + `uv.lock`. Do **not** create `requirements.txt` or use `pip install` in CI workflows. New CAD dependencies belong in a named root uv dependency group.
4. `design.json` opts a *buildable* design into the generic build runner. Do not invent a manifest for a design that has no working Python builder. Match the manifest exactly to [BUILDING_DESIGNS.md](BUILDING_DESIGNS.md).
5. Source changes affecting printable geometry need regenerated STL(s), updated project README/print instructions, and ideally updated rendered images. Do not silently change committed STLs without explaining where they came from.
6. A watertight STL is **not** proof of support-free printing, mechanical clearance, Gridfinity compatibility, or physical fit. Mark unverified claims **not tested** or **prototype**. Never claim to have printed a design unless actual print evidence exists.
7. Preserve third-party attribution and license terms. Each design chooses/records its own license; the repository intentionally has **no blanket design license**. Ask for permission if commercial or remix rights are unclear. Do not copy an existing project's CC BY-NC-SA terms onto unrelated original designs.
8. Don't commit secrets, home addresses, machine tokens, printer IP addresses, G-code, build caches, or huge intermediate files. Binary STLs and CAD formats follow `.gitattributes` / Git LFS.
9. Don't overwrite another design's files or rewrite history just to introduce a new design.

## Verify before completing work

From the repository root, with uv installed and a committed `uv.lock`:

```bash
uv sync --locked --no-default-groups --group ci
uv run --no-sync python -m unittest discover -s scripts/tests -v
uv run --no-sync python scripts/build_designs.py --check
uv run --no-sync python scripts/validate_stls.py
uv run --no-sync python scripts/run_project_checks.py
```

For a new or changed buildable design, also run the relevant manual build as described in `BUILDING_DESIGNS.md` if dependencies/time permit. Explain any checks not run and why. Physical/slicer evidence is separate from CI results.

## For a new design

Use the optional [new-design skill](.agents/skills/new-3d-design/SKILL.md) and [template](templates/design/README.md). Deliver a project README with clear print orientation, supports, tolerances, assembly and validation status, images (when available), provenance, and explicit licensing. Keep changes scoped and reviewable.
