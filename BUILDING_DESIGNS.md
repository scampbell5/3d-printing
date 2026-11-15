# Rebuilding CAD designs on GitHub Actions

The generic [Build designs (manual)](.github/workflows/build-designs.yml) workflow
regenerates selected models from their CAD scripts. It is independent of the
[automatic STL validation](.github/workflows/validate-designs.yml) workflow.

## Run a rebuild

1. Open your GitHub repository → **Actions** → **Build designs (manual)**.
2. Click **Run workflow**.
3. For `design`, enter **`all`** to rebuild all registered projects, or the
   project ID (currently **`gridfinity/reciprocating-saw-blade-holder`**).
4. When the run finishes, download the **`rebuilt-designs-...`** artifact from
   the run. It contains only generated STLs and a `BUILD-REPORT.md` file.

The build runs **only on manual request**, because some CAD reconstructions
are computationally expensive. A normal push or pull request runs the fast,
repo-wide STL checks instead. Builds do not modify or commit source files or
STLs in GitHub; outputs live in isolated `dist/builds/` directories in CI.

**Limitations:** mesh checks verify watertightness, shell connectivity, winding,
and positive volume; they cannot certify printability, Gridfinity fit, support
requirements, or the physical sliding-lock mechanism. The current V4 CAD
rebuild has not yet been executed on a GitHub-hosted runner; it may need RAM,
package version, or timeout adjustments.

## Register a new design

Place a `design.json` alongside that design's README:

```text
designs/household/my-project/
├── design.json
├── cad/
│   ├── build.py
│   └── requirements.txt
└── stl/
```

The manifest format is:

```json
{
  "schema_version": 1,
  "id": "household/my-project",
  "name": "My project",
  "build": {
    "script": "cad/build.py",
    "requirements": "cad/requirements.txt",
    "outputs": ["holder.stl", "lid.stl"]
  }
}
```

`id` must match its path below `designs/`. `requirements` is optional.
The list of `outputs` is required and is checked against actual generated STLs.

The builder invokes your Python script from the design directory. Read these
environment variables in the CAD script so CI can preserve tracked files:

```python
import os
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
output_dir = Path(os.environ.get('DESIGN_BUILD_OUTPUT_DIR', project_root / 'stl'))
work_dir = Path(os.environ.get('DESIGN_BUILD_WORK_DIR', project_root / 'cad' / 'build'))
output_dir.mkdir(parents=True, exist_ok=True)
work_dir.mkdir(parents=True, exist_ok=True)
```

Your script should write precisely the STL names declared under `outputs`.
The workflow installs the design's Python requirements, runs its script,
checks the generated STLs, and uploads them as artifacts.

## Optional project-specific validation

You can place an additional `scripts/check_meshes.py` inside any design
folder. Automatic CI discovers and runs all of them without modifying a
workflow. These tests check committed files; the generic builder separately
validates every generated STL named in `design.json`.

## Local commands

```bash
python -m pip install -r scripts/requirements-ci.txt
python scripts/build_designs.py --list
python scripts/build_designs.py --check
python scripts/build_designs.py --design all --dry-run
python scripts/build_designs.py --design gridfinity/reciprocating-saw-blade-holder
python -m unittest discover -s scripts/tests -v
```

Rebuilds run CAD code and install its dependencies. Only run builders from
projects you trust. Avoid adding untrusted or third-party build scripts to a
public repository without review.
