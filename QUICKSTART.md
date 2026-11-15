# Quickstart: 3D Printing Designs

Welcome! You do **not** need to know Python or CAD to use the printable files. Pick the path that matches what you want to do.

| I want to… | Start here |
| --- | --- |
| **Print an existing design** | [A. Print a model](#a-print-an-existing-model) |
| **Suggest an idea or report a problem** | [B. Suggest or improve a design](#b-suggest-or-improve-a-design) |
| **Create a design with an AI coding assistant** | [C. Create a new design with AI](#c-create-a-new-design-with-ai) |
| **Develop CAD or tooling myself** | [D. Work locally and run checks](#d-work-locally-and-run-checks) |

## A. Print an existing model

1. Open the [design catalog](README.md#designs), then choose a design.
2. Read **that design's README** for parts, material, print orientation, supports, and current test status. For example, see the [reciprocating saw blade holder](designs/gridfinity/reciprocating-saw-blade-holder/).
3. Download the STLs in that project's `stl/` directory. **Important:** this repository stores STLs with Git LFS; some ordinary download methods may give you tiny LFS pointer files instead of real meshes. If that happens, use the cloning steps below or a published GitHub Release (if available).
4. Import the STLs into your slicer, confirm orientation/bed fit, inspect the sliced layers, and print. Check the project's license before redistributing or selling anything.
5. If you test a model, consider contributing photos and notes about slicer settings, fit, or issues. The **CI passing** does not mean the print or assembly has been physically tested.

**Need actual STL files via Git?** Install [Git](https://git-scm.com/downloads) and [Git LFS](https://git-lfs.com/), then:

```bash
git lfs install
git clone https://github.com/OWNER/3d-printing.git
cd 3d-printing
git lfs pull
```

Replace `OWNER` with the repository owner displayed in GitHub's address bar.

## B. Suggest or improve a design

No programming required:

1. Check existing Issues to avoid duplicates.
2. Open **Issues → New issue → Design proposal**, or open a regular issue for a bug, fit problem, or improvement.
3. Describe what you'd like to change, approximate dimensions, printer/material, and any photos or sketches. Link the original source and its license if you're remixing something.
4. For a simple documentation/photo correction, you can also edit the file on GitHub and propose a pull request (PR).

For larger changes, use the contributor workflow below. Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

## C. Create a new design with AI

You can use an AI coding assistant **that can inspect and edit repository files**. It must have access to a local checkout or connected repository; simply mentioning the repo in chat doesn't load its instructions automatically.

1. **Fork** the GitHub repository to your account and clone your fork with Git LFS, using the commands in [D](#d-work-locally-and-run-checks).
2. Open the checked-out project in your AI assistant's workspace or IDE.
3. Tell the assistant to **read [`AGENTS.md`](AGENTS.md) first**, followed by [`docs/DESIGN_STANDARDS.md`](docs/DESIGN_STANDARDS.md) and [`BUILDING_DESIGNS.md`](BUILDING_DESIGNS.md).
4. Copy the prompt below, replacing the example with your idea. Alternatively, use [the reusable prompt](.github/prompts/new-design.prompt.md) or [design skill](.agents/skills/new-3d-design/SKILL.md) if your assistant supports those formats.
5. Review the proposed geometry, licenses, images, and test results yourself. AI instructions help with consistency but **do not automatically validate or guarantee printability**.
6. Push your branch and open a PR, using the supplied checklist.

**Copy/paste example:**

> Read `AGENTS.md`, `QUICKSTART.md`, `docs/DESIGN_STANDARDS.md`, and `BUILDING_DESIGNS.md` first. Create a new design for a wall-mounted cable organizer under `designs/household/cable-organizer/`. Design for a 0.4 mm nozzle and PLA. Include editable CAD source if possible, real STL exports, a project README using `templates/design/README.md`, print orientation, a render of the actual model, explicit licensing, and honest test status. Register `design.json` **only if** the Python build script works with the generic builder. Use uv and run the repository checks. Do not claim physical fit or support-free printing without evidence.

For your own request, replace the object, category, materials, dimensions, and printer settings. The assistant should **not** copy another creator's model unless its license permits it.

## D. Work locally and run checks

### One-time setup

Install [Git](https://git-scm.com/downloads), [Git LFS](https://git-lfs.com/), and [uv](https://docs.astral.sh/uv/getting-started/installation/). No global `pip install` is needed. On macOS with Homebrew, one option is `brew install git git-lfs uv`.

Fork this repo on GitHub, then clone **your fork**:

```bash
git lfs install
git clone https://github.com/YOUR-USERNAME/3d-printing.git
cd 3d-printing
git lfs pull
uv python install
```

The project uses Python 3.12 from `.python-version`.

### Install the lightweight validation environment

```bash
# Only needed if this checkout does not already have a committed uv.lock:
uv lock

uv sync --locked --no-default-groups --group ci
```

If you generated `uv.lock` because it was missing, include it in your PR. If you're changing dependency groups, run `uv lock` again and commit the updated lockfile.

### Start a new design

1. Make a branch: `git switch -c design/my-new-project`.
2. Create `designs/<category>/<kebab-case-name>/` and start with [`templates/design/README.md`](templates/design/README.md).
3. Put editable source in `cad/`, printable STLs in `stl/`, and preview images in `images/`. Add a project-specific `LICENSE.md` and attribution when necessary.
4. Add **`design.json` only if** you have a functioning Python build script; follow [BUILDING_DESIGNS.md](BUILDING_DESIGNS.md). A manually designed STL doesn't require a manifest.
5. For prints or assemblies, document material, orientation, supports, tolerances, what you inspected, and what you have *not* tested.

### Run checks before opening a PR

From the repository root:

```bash
uv run --no-sync python -m unittest discover -s scripts/tests -v
uv run --no-sync python scripts/build_designs.py --check
uv run --no-sync python scripts/validate_stls.py
uv run --no-sync python scripts/run_project_checks.py
```

The automatic GitHub Action also validates committed STLs. CAD rebuilds are a separate manual workflow (see [`BUILDING_DESIGNS.md`](BUILDING_DESIGNS.md)); building a model does **not** mean it was successfully sliced or printed.

### Submit your changes

```bash
git add .
git commit -m "Add cable organizer design"
git push -u origin design/my-new-project
```

Open a PR against the original repository. The PR template will ask for previews, license and source information, validation, print settings, and anything still untested. Review Git LFS usage before adding large binaries. Do **not** commit machine-specific G-code, private addresses, printer IPs, or secrets.

## Where to go next

- [Contributing guide](CONTRIBUTING.md): how to submit changes and report validation.
- [Design standards](docs/DESIGN_STANDARDS.md): what each design must contain.
- [AI agent instructions](AGENTS.md): rules for assistants working in this repository.
- [Build and dependency guide](BUILDING_DESIGNS.md): uv groups, `design.json`, and manual CAD builds.
- [Design proposal](.github/ISSUE_TEMPLATE/design-proposal.yml): GitHub issue template for a new idea.

**Licensing reminder:** This repository does not have one license covering every design. The [saw blade holder](designs/gridfinity/reciprocating-saw-blade-holder/) is a CC BY-NC-SA 4.0 remix. Always check the license in the particular design folder before modifying, redistributing, or selling it.
