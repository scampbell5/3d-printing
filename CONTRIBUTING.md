# Contributing

**New here?** Start with the [Quickstart](QUICKSTART.md): it has separate guides for printing an existing design, suggesting improvements, using an AI assistant, and developing locally. You don't need Python to propose an idea or print an existing STL.

Contributions are welcome: new printable designs, CAD improvements, clearer instructions, photos of physical prints, and fixes to build/validation tooling.

## Before you start

1. Search existing Issues and designs to avoid duplicates. For substantial new ideas, open the **Design proposal** issue template first.
2. Read [AGENTS.md](AGENTS.md), [design standards](docs/DESIGN_STANDARDS.md), and [build instructions](BUILDING_DESIGNS.md). These are useful whether you use an AI assistant or not.
3. Check the license of every model you are remixing **before** uploading its original or modified geometry. Include source links, author credits, license version, and changes. Some models forbid redistribution or commercial use.
4. For the existing saw-blade holder, check its own attribution and **CC BY-NC-SA 4.0** license; that license does not automatically apply to unrelated new designs.

## Add or modify a design

- Place files under `designs/<category>/<design-slug>/`, using lowercase kebab-case names.
- Include the source CAD/script when available and a project `README.md` with meaningful images, print parameters, a version/status, and a separate physical-test checklist. See `templates/design/README.md` for a starting point.
- Place release-candidate STL files in `stl/`. Store slicer projects in `slicer/` if you have them, but **do not** commit machine-specific G-code (`*.gcode`, `*.gcode.3mf`).
- If the design is rebuildable by Python, add a working `cad/*.py` script and a `design.json` matching [BUILDING_DESIGNS.md](BUILDING_DESIGNS.md). Update root `pyproject.toml` and `uv.lock` if a new dependency group is needed.
- Do not claim a model is support-free, mechanically compatible, or physically validated unless you have slicer or print evidence. Prefer precise status labels like **CAD preview**, **Sliced**, **Test print passed**, and **Physically validated**.

## Validate before a pull request

```bash
uv sync --locked --no-default-groups --group ci
uv run --no-sync python -m unittest discover -s scripts/tests -v
uv run --no-sync python scripts/build_designs.py --check
uv run --no-sync python scripts/validate_stls.py
uv run --no-sync python scripts/run_project_checks.py
```

On a new machine, install uv and run `uv python install` first. Changes to dependencies require `uv lock` and a committed updated `uv.lock`. Use Git LFS for tracked STL/CAD binary types (`git lfs install`). If a print or heavy CAD build was not run, state that explicitly instead of inventing a passing result.

## Open a pull request

Provide a short change summary, link to the source or issue, before/after previews for visual changes, exact material/printer/slicer settings for print claims, STL validation results, and any known unverified fit or tolerance constraints. The [PR template](.github/PULL_REQUEST_TEMPLATE.md) contains a checklist. Keep each PR focused on one design or tooling improvement.

## AI-assisted contributions

AI-generated code or geometry is welcome, but contributors are accountable for source provenance, licensing, test output, and print safety. A model's self-reported 'validated' claim isn't a test result. The repository includes [`AGENTS.md`](AGENTS.md), a [new-design skill](.agents/skills/new-3d-design/SKILL.md), and a [reusable prompt](.github/prompts/new-design.prompt.md) for consistent AI-assisted work.
