# Building designs with uv

The repository-wide **Validate 3D designs** workflow runs on pushes and pull requests.
The generic **Build designs (manual)** workflow reconstructs CAD designs on demand;
large or memory-intensive builds are not part of routine validation.

## First-time setup

Install [uv](https://docs.astral.sh/uv/), then in the repository root run:

```bash
uv python install
uv lock                 # Generate uv.lock if it is not already committed
uv sync --locked --no-default-groups --group ci
uv run --no-sync python -m unittest discover -s scripts/tests -v
uv run --no-sync python scripts/validate_stls.py
```

**Commit `uv.lock`** along with `pyproject.toml`. The lock includes dependencies
for both CI and all registered CAD build groups, even though the CI environment
installs only `ci` during normal validation. When dependencies change, run
`uv lock` and commit the updated lockfile. The GitHub Actions workflows check
an existing lockfile with `uv lock --check` and refuse a stale lock. If a
lockfile is absent, Actions temporarily resolves one and uploads it as a
`generated-uv-lock` artifact so you can commit it; until then those runs
are **not reproducible**.

## Rebuild a design

In GitHub: **Actions → Build designs (manual) → Run workflow** and enter `all`
or a project ID, currently `gridfinity/reciprocating-saw-blade-holder`.
Download the `rebuilt-designs-...` artifact, containing generated STLs and
`BUILD-REPORT.md`. This does **not** commit or overwrite existing STL files.

Or run locally:

```bash
uv run --locked --no-default-groups --group ci python scripts/build_designs.py --list
uv run --locked --no-default-groups --group ci python scripts/build_designs.py --check
uv run --locked --no-default-groups --group ci python scripts/build_designs.py --design all --dry-run
uv run --locked --no-default-groups --group ci python scripts/build_designs.py --design gridfinity/reciprocating-saw-blade-holder
```

The builder automatically uses `uv run --locked` with the project's named
CAD dependency group. It isolates output in `dist/builds/<project-id>/` and
validates each required STL before reporting success. Group-specific packages
are *not* installed during the regular validation job.

## Register another design

Add the dependencies for your new CAD script to a **unique dependency group**
in the root `pyproject.toml`:

```toml
[dependency-groups]
# ... existing groups ...
cad-my-project = ["cadquery>=2.5,<3"]
```

Then run `uv lock` and commit the updated lockfile. Define a manifest at
`designs/household/my-project/design.json`:

```json
{
  "schema_version": 1,
  "id": "household/my-project",
  "name": "My project",
  "build": {
    "script": "cad/build.py",
    "dependency_group": "cad-my-project",
    "outputs": ["holder.stl", "lid.stl"]
  }
}
```

`id` must equal the directory path relative to `designs/`. The dependency group
is optional for builds that need only the `ci` packages. The manifest checker
rejects unknown dependency groups, path escapes, and missing Python scripts.
There are no per-design `requirements.txt` files.

Every CAD script should write generated files to the exact names in `outputs`,
respecting the following environment variables:

```python
import os
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
output_dir = Path(os.environ.get('DESIGN_BUILD_OUTPUT_DIR', project_root / 'stl'))
work_dir = Path(os.environ.get('DESIGN_BUILD_WORK_DIR', project_root / 'cad' / 'build'))
output_dir.mkdir(parents=True, exist_ok=True)
work_dir.mkdir(parents=True, exist_ok=True)
```

## What gets tested

The mesh validator checks watertightness, connected shells, winding, positive
volume, and plausible extents. It does not prove support-free printing, correct
baseplate tolerances, or locking strength. An optional `scripts/check_meshes.py`
inside each design is discovered automatically and runs against committed STLs.

CAD rebuilds run executable Python from the repository. Only run scripts from
sources you trust. The existing V4 reconstruction is resource intensive and
has not been run on a GitHub-hosted runner yet.
