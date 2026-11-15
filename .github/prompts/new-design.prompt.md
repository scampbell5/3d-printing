---
description: Create or revise a 3D printable design using this repository's standards
---

I want to create or revise this 3D printing project:

**Concept:** [Brief description of the object]
**Category / project ID:** [e.g., household/cable-organizer]
**Functional constraints:** [dimensions, attachments, strength/fit, material]
**Printer / slicer (if known):** [e.g., Qidi Q2 / QIDI Studio]
**Source model / license (if remixing):** [URL, author, exact license]

Use `AGENTS.md`, `docs/DESIGN_STANDARDS.md`, `CONTRIBUTING.md`, and `BUILDING_DESIGNS.md` as the operating instructions. Inspect existing `designs/` examples. Use the new-design skill if your environment supports it.

Deliver a working, reviewable project folder (not just a prose plan): editable CAD/source where feasible, appropriately named STL files only if actually generated, an updated README using `templates/design/README.md`, images of the actual geometry if rendering is possible, clear print orientation and tolerances, per-design license/attribution, and `design.json` **only when** its builder is real and follows the existing contract.

Use uv for dependencies. Run the applicable tests and STL checks. Explicitly separate proven mesh checks, inspected slicer preview, and physical print testing; don't label untested geometry support-free or production-ready. State missing information and anything not verified. Do not commit or redistribute third-party meshes without permission.
