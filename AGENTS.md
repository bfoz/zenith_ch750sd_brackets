# AGENTS.md

Guidance for AI agents working in this repository. Read this before making changes.

## What this is

Parametric FreeCAD models of custom sheet-metal brackets for a Zenith CH750 Super Duty amateur-built aircraft: wire/cable/hose routing, elevator pulleys, parking brake valve, rudder pedal bearings.

This is **not a software project**. There is no build system, no dependency manifest, no test suite, no linter, and no CI beyond a release workflow. Don't look for `package.json`, `Makefile`, or `pytest`, and don't add any.

The deliverables are the `*.FCStd` FreeCAD source documents (canonical), `README.md` (fabrication notes, parts lists, installation steps — equally important), and the derived `*.step`/`*.dxf`/`*.svg` files builders send to cut shops.

## Repository inventory

FreeCAD documents, one per bracket family:

- `TrailingEdgeBracket.FCStd` — the big one, 7 bodies: `Body`, `Grommets`, `SnapBushings`, `BushingsGrommets`, `Body2Bushings3Grommets`, `OutboardTrailingEdgeBracket`, `OutboardTrailingEdgeBracketTape`
- `ElevatorPulleyBracket.FCStd` — `Bracket` + `Base` (to be fabricated), `Pulley` (reference only), plus an `Assembly` with joints
- `MatcoParkingBrakeBracket.FCStd` — `Top Bracket` + `Bottom Bracket` (note the spaces in the body labels) + `Assembly`; references `mcmaster/97590A711_*.STEP` studs
- `RudderPedalBracketAssembly.FCStd` — `LeftBracket`, `RightBracket`, `Bearing` (Delrin)
- `FuelReturnHoseBracket.FCStd` and `WingtipWireBracket.FCStd` — single body each

Other paths:

- `mcmaster/` — McMaster-Carr supplier STEP models for purchased hardware
- `RudderPedalAssembly/` — per-body STEP exports for that assembly
- `.github/workflows/release.yaml` — release automation (see Releases)
- `test.pdf`, `test1.pdf` — scratch junk, referenced by nothing

## FreeCAD environment

- App bundle: `/Applications/FreeCAD.app` — FreeCAD 1.1.4
- Headless CLI: `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd script.py` (also `.../bin/python`)

### Critical: the Sheet Metal workbench add-on is NOT installed

Every sheet-metal body starts from `BaseShape`, a `PartDesign::FeaturePython` supplied by the Sheet Metal Workbench add-on (`SheetMetalBaseShapeCmd`). It is a hard dependency of all six documents and is not installed here (`~/Library/Application Support/FreeCAD/Mod` does not exist).

Consequences:

- Opening a document logs `PropertyPythonObject::Restore: blocked import of module 'SheetMetalBaseShapeCmd'`, and `BaseShape.Proxy` is `None`.
- Cached shapes still load correctly — `Shape.isValid()`, `Volume`, and `BoundBox` all work — and a plain `doc.recompute()` reports "Up-to-date" with no errors. That is the cache being reused, not a real rebuild.
- Therefore never edit, recompute, and save a `.FCStd` headlessly and assume the sheet-metal features survived. Unfold, bend, and K-factor features cannot run.
- Reading geometry headlessly is safe: measurements, bounding boxes, volume checks, and STEP export of already-computed shapes.
- Real model edits happen in the FreeCAD GUI with the add-on installed via the Add-on Manager. Ask the user before assuming it's available.

Global sheet-metal parameters, consistent across every part:

- `thickness = 1.0 mm` (0.040" aluminum)
- Bend radius and K-factor are tuned for Send Cut Send; other shops need different values
- Millimetres everywhere (STEP exports carry `SI_UNIT(.MILLI.,.METRE.)`)
- Older DXF exports came from FreeCAD v1.0 (`AC1014`); the current app is 1.1.x

## Working rules

1. **Edit in the GUI, commit the result.** Model changes are made in FreeCAD (by a human, or with the add-on installed) and then committed. Agents should restrict themselves to reading/inspecting models, writing and updating `README.md`, checking naming conventions, and reviewing diffs.
2. **README and model must stay in sync.** Every bracket section follows the same shape: intro prose, optional `### Fabrication`, `### Bushings and Grommets` and/or `### Parts` (Part number / Quantity / Description table with Aircraft Spruce and McMaster links), then `### Installation` as numbered steps. A new bracket needs a matching README section in the same commit.
3. **Fabrication files: STEP first.** Unfolded DXF output has been unreliable with Send Cut Send (see the June 2025 note in the README). Prefer STEP exports for ordering and keep DXFs only where they demonstrably still work.
4. **Naming convention for derived files:** `<DocumentName>-<BodyLabel>.step` and `<DocumentName>-<BodyLabel>_Unfold.dxf`. Spaces in body labels become underscores in DXFs but stay spaces in STEPs, e.g. `MatcoParkingBrakeBracket-Top Bracket.step` vs `MatcoParkingBrakeBracket-Top_Bracket_Unfold.dxf`.
5. **Right-wing parts are mirrored.** Most brackets are modelled for the left wing and the README tells builders to flip the bend angle (or have the cut shop duplicate the part with a reversed bend). Don't silently add duplicate mirrored geometry — document the flip instead.
6. **Amateur-built aircraft, safety-relevant.** These are published as a workable option, not a certified engineering drawing. Keep the README's hedging ("can be used", "feel free to adjust", "verify fit") instead of prescriptive absolutes, keep exact hardware part numbers and quantities, and flag permanent or destructive steps such as the epoxy-bonded M4 studs on the parking brake bracket. Never delete an existing caution.
7. **Binary files can't be diffed.** `git diff` on a `.FCStd` shows only a byte-count change. Verify model edits by re-opening the file headlessly and inspecting the affected bodies, or ask the user to eyeball them in the GUI.
8. **Backups are ignored.** `.gitignore` covers `*.FCBak` and `*.FCStd1` (FreeCAD auto-backups). Never commit them.

## Git conventions

- Remote `origin` is `git@github.com:bfoz/zenith_ch750sd_brackets.git` over SSH. The Gitea MCP tools configured in this session point at a different host, so don't assume the GitHub repo is reachable through them.
- Commit messages are sentence case with no conventional-commit prefixes and describe the change as a complete thought: `Added brackets for the rudder pedals`, `Changed the Matco parking brake bracket bottom mounting holes to M4`, `Recomputed for FreeCAD 1.1`.
- Reference issues with a `[#N]` prefix: `[#4] Added a bracket for the Matco parking brake valve`.
- Use a commit body when the reason matters, e.g. why rivets became bonded studs.
- A typical commit is `<Model>.FCStd` plus the matching `README.md` change.

### Untracked files — do not auto-stage

Only 9 files are tracked today. The working tree also holds a large set of untracked derived artifacts (`*.step`, `*.dxf`, `*.svg`), `RudderPedalAssembly/`, `mcmaster/97590A716_*.STEP`, and even `WingtipWireBracket.FCStd` despite it being documented in the README, plus `test.pdf`/`test1.pdf`. Whether those belong in git is the maintainer's call, not an agent's. Never run `git add -A` or `git add .` here; stage explicit paths and surface the ambiguity to the user instead of resolving it silently.

## Releases

`.github/workflows/release.yaml` fires on any pushed `v*` tag: it zips `*.FCStd` into `<repo-name>.zip` and runs `gh release create --generate-notes`.

- **Only `.FCStd` files ship.** STEP and DXF files are absent from the bundle, so the workflow's glob needs extending if the maintainer wants fabrication files released.
- Tag format is `v<version>` (`v0` exists) and release titles are `Version <version>`.
- Don't create or push tags unless explicitly asked.

## Sanity checks an agent can actually run

- List bodies and parameters with a short `freecadcmd` script (`PartDesign::Body` labels, `thickness`, `BoundBox`, `Volume`).
- Confirm a STEP export's units and body count from its `ISO-10303-21` header.
- Inspect object names and history without FreeCAD via `unzip -p <Model>.FCStd Document.xml` — a `.FCStd` is a zip.
- Cross-check every part number, quantity, and installation step in `README.md` against the model it documents; README accuracy is the highest-value review an automated agent can do here.
- Verify derived filenames against rule 4.
