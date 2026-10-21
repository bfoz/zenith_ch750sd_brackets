# AGENTS.md

Guidance for AI agents working in this repository. Read this before making changes.

## What this is

Parametric FreeCAD models of custom sheet-metal brackets for a Zenith CH750 Super Duty amateur-built aircraft: wire/cable/hose routing, elevator pulleys, parking brake valve, rudder pedal bearings.

This is **not a software project**. There is no build system, no dependency manifest, no test suite, no linter, and no CI beyond a release workflow. Don't look for `package.json`, `Makefile`, or `pytest`, and don't add any.

The deliverables are the `*.FCStd` FreeCAD source documents (canonical), `README.md` (fabrication notes, parts lists, installation steps — equally important), and the derived `*.step`/`*.dxf`/`*.svg` files builders send to cut shops.

## Repository inventory

FreeCAD documents that define brackets (these are the ones in `scripts/parts.manifest`):

- `TrailingEdgeBracket.FCStd` — the big one, 7 bodies: `Body`, `Grommets`, `SnapBushings`, `BushingsGrommets`, `Body2Bushings3Grommets`, `OutboardTrailingEdgeBracket`, `OutboardTrailingEdgeBracketTape`
- `ElevatorPulleyBracket.FCStd` — `Bracket` + `Base` (to be fabricated), `Pulley` (reference only), plus an `Assembly` with joints
- `MatcoParkingBrakeBracket.FCStd` — `Top Bracket` + `Bottom Bracket` (note the spaces in the body labels) + `Assembly`; references `mcmaster/97590A711_*.STEP` studs
- `RudderPedalBracketAssembly.FCStd` — `LeftBracket`, `RightBracket`, `Bearing` (Delrin)
- `ACK_E04_ELT_Bracket.FCStd` — `ACK_E04_ELT_Bracket` (fab) plus `ACK_E04_ELT`, a reference model of the ELT itself
- `FuelReturnHoseBracket.FCStd` and `WingtipWireBracket.FCStd` — single body each

Other `.FCStd` files are **not** bracket models and have no parts to build: `ELT_reference.FCStd`, `ch750sd.FCStd`, `sd750.FCStd` (all contain zero `PartDesign::Body` objects; `ch750sd.FCStd` is populated by the scratch script `ch750sd.py`). Don't add them to the manifest, and don't treat an empty body list in them as a bug.

Other paths:

- `mcmaster/` — McMaster-Carr supplier STEP models for purchased hardware
- `RudderPedalAssembly/` — per-body STEP exports for that assembly
- `scripts/` — `parts.manifest` and `export_step.py` (see Building STEP files)
- `.github/workflows/release.yaml` — release automation; `step-files.yaml` — STEP generation (see Releases)
- `test.pdf`, `test1.pdf`, `export_stl.applescript`, `stl/`, `__pycache__/`, `.env` — scratch and local tooling, referenced by nothing; leave them untracked unless asked

## FreeCAD environment

- App bundle: `/Applications/FreeCAD.app` — FreeCAD 1.1.4
- Headless CLI: `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd script.py` (also `.../bin/python`)

### The Sheet Metal workbench add-on is a hard dependency

Every sheet-metal body starts from `BaseShape`, a `PartDesign::FeaturePython` supplied by the Sheet Metal Workbench add-on (`SheetMetalBaseShapeCmd`, class `SMBaseShape`). All six documents depend on it.

It is installed at `~/Library/Application Support/FreeCAD/v1-1/Mod/sheetmetal`. Note the version-specific `v1-1` path segment — FreeCAD 1.1 does **not** use `~/Library/Application Support/FreeCAD/Mod`, so don't conclude the add-on is missing from that path. Verify with `import SheetMetalBaseShapeCmd` under `freecadcmd`, or by checking that a `Proxy` element in `Document.xml` carries `module="SheetMetalBaseShapeCmd"`.

With the add-on available, `BaseShape.Proxy` restores as a live `SMBaseShape` and headless scripting works properly.

### Data loss hazard: opening a doc without the add-on, then saving

FreeCAD blocks restoring an add-on-backed feature whose module can't be imported. The document still opens and looks perfect, but the feature's `Proxy` becomes `null` — and **saving at that point permanently destroys the add-on feature**, writing a plain shape in its place. FreeCAD reports no error, and every later `recompute()` says "Up-to-date". The only clue is the log line `PropertyPythonObject::Restore: blocked import of module '...'`.

Never save a document that logged that message. Close it without saving, install the add-on, then reopen.

This has already happened once and the damage is permanent. `WingtipWireBracket.FCStd` was upgraded from the FreeCAD 1.0 document format and saved while the add-on was missing (2026-10-13). Its `BaseShape` is now a static shape with `Proxy = null` and no module reference, where the other five documents still carry `module="SheetMetalBaseShapeCmd"`. Installing the add-on afterwards does **not** repair it — re-saving leaves the proxy null, because the object in the file no longer names a module to restore.

What was lost in that file, precisely:

- The Base Shape feature is inert. Setting `BaseShape.length` to `40 mm` and recomputing leaves the body volume at exactly `505.729221 mm³`. The `length`/`width`/`height`/`radius`/`thickness` properties are still readable but no longer regenerate anything.
- Sheet-metal-specific features (Unfold, bend and K-factor handling) can no longer attach to that body. This part is `shapeType="Flat"` with no bends, so its flat pattern is simply the solid itself and the fabrication drawing is unaffected.
- What still works: the sketch-driven chain. Adding a circle to `Sketch` and recomputing changes the volume (505.73 → 477.45), so hole and cutout editing remains fully parametric. Sketch (8 geometries, 21 constraints), `Pocket` (ThroughAll), `Fillet`, and `Fillet001` are all intact, and the solid is unchanged and valid.

Repair is optional and low-value: re-create the Base Shape in the GUI (30 x 20 x 1 mm plate, 1 mm radius) and re-attach the sketch. The original FreeCAD 1.0 document is unrecoverable — it was overwritten, never committed, and only one `.FCBak` is kept, which is also post-upgrade.

Global sheet-metal parameters, consistent across every part:

- `thickness = 1.0 mm` (0.040" aluminum)
- Bend radius and K-factor are tuned for Send Cut Send; other shops need different values
- Millimetres everywhere (STEP exports carry `SI_UNIT(.MILLI.,.METRE.)`)
- Older DXF exports came from FreeCAD v1.0 (`AC1014`); the current app is 1.1.x

## Building STEP files

STEP generation is automated. `scripts/parts.manifest` is the single source of truth for what gets built, one line per output:

    <FreeCAD document> | <body label> | <output filename>

Outputs are flat files in the `step/` directory at the repo root (gitignored, overridable with `ZENITH_STEP_DIR`), which is what CI uploads and what a release zips. The directory is flat and filenames must be unique, so the exporter rejects duplicate outputs and any path that escapes the directory.

Make targets (`make help` prints them all):

- `make` — export parts that are missing or older than their source document, into the `step/` directory
- `make check` (or `make force`) — re-export everything, ignoring timestamps
- `make <document>` — build one document, e.g. `make TrailingEdgeBracket`
- `make list` / `make step-files` — show the manifest, or just the output paths under `step/`
- `make clean-steps` — delete the declared STEP files, leaving the directory
- `make clean` — delete the whole `step/` directory, including scratch files from an interrupted run

`scripts/export_step.py` is the implementation. It runs under `freecadcmd`, opens each document once, exports the listed bodies, and closes **without saving**. Never add a `save()` call there, and never recompute: the script reads the shapes FreeCAD already cached in each file, which is why it works with or without the Sheet Metal add-on installed. It writes to a `.tmp.step` scratch path and validates each file by reading it back and comparing volume before renaming into place.

Bodies not in the manifest are deliberately excluded: `Pulley` (bought, not cut) and the three superseded TrailingEdge variants (`Grommets`, `SnapBushings`, `Body2Bushings3Grommets`), which are alternatives to `BushingsGrommets`. Add a manifest line, don't export everything blindly.

freecadcmd quirks that will bite you (all encoded in the script):

- An uncaught exception exits **0**; `sys.exit(N)` works. Output is not flushed on exit, so flush before exiting or write to stderr. Catch everything and exit non-zero explicitly.
- Arguments after the script name are treated as documents to open, and unknown `--options` are rejected before the script runs. Configuration therefore arrives in env vars: `ZENITH_STEP_MANIFEST`, `ZENITH_STEP_ONLY`, `ZENITH_STEP_FORCE`.
- `Import.export` picks the exporter from the file extension, so a scratch path must keep `.step`.
- FreeCAD prints harmless noise to stderr on every run (a missing 3Dconnexion driver, "Recomputation required" geo-version notes). Don't write a check that greps stderr for the word Error.

## Working rules

1. **Edit models in the GUI, generate exports with make.** Model changes are made in FreeCAD (by a human, or with the add-on installed) and then committed. Regenerating STEP files is safe to automate with `make`; editing parametric geometry headlessly is not. Agents may inspect models, regenerate exports, and update `README.md`.
2. **README and model must stay in sync.** Every bracket section follows the same shape: intro prose, optional `### Fabrication`, `### Bushings and Grommets` and/or `### Parts` (Part number / Quantity / Description table with Aircraft Spruce and McMaster links), then `### Installation` as numbered steps. A new bracket needs a matching README section in the same commit.
3. **Fabrication files: STEP first.** Unfolded DXF output has been unreliable with Send Cut Send (see the June 2025 note in the README). Prefer STEP exports for ordering and keep DXFs only where they demonstrably still work.
4. **Naming convention for derived files:** `<DocumentName>-<BodyLabel>.step` and `<DocumentName>-<BodyLabel>_Unfold.dxf`. Spaces in body labels become underscores in DXFs but stay spaces in STEPs, e.g. `MatcoParkingBrakeBracket-Top Bracket.step` vs `MatcoParkingBrakeBracket-Top_Bracket_Unfold.dxf`. The manifest is authoritative for STEP names; this rule is what it follows, and DXFs are still hand-made.
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

Tracked files are the `.FCStd` documents, `README.md`, `AGENTS.md`, `Makefile`, `scripts/`, `.github/`, and one `mcmaster/` supplier model. Everything else in the working tree is untracked: all generated `*.step` files, the hand-made `*.dxf`/`*.svg` unfold drawings, `RudderPedalAssembly/`, a second `mcmaster/` model, and `test.pdf`/`test1.pdf`. Whether those belong in git is the maintainer's call, not an agent's. Never run `git add -A` or `git add .` here; stage explicit paths and surface the ambiguity to the user instead of resolving it silently.

## Workflows

`.github/workflows/step-files.yaml` builds the STEP files. It runs on push to `main`, on pull requests, on `workflow_dispatch`, and is called by the release workflow. It installs the pinned FreeCAD AppImage, exports with `ZENITH_STEP_FORCE=1`, asserts that no tracked `.FCStd` changed, verifies every declared file was written, and uploads the `step/` directory as an artifact named `zenith-ch750sd-step-files` (`-<tag>` when triggered by a tag) retained 30 days. Nothing is committed back and no release is modified by this workflow.

- The FreeCAD version is pinned by asset name and SHA256 in the workflow `env` block. Bump it deliberately and diff the output, because a FreeCAD upgrade can change exported geometry. It runs on `ubuntu-24.04`, not `ubuntu-latest`, so a runner image bump can't strand the pinned AppImage.
- The exporter reads cached shapes, so the workflow does **not** install the Sheet Metal workbench. Keeping the add-on out of CI proves the exporter doesn't depend on it. If a model ever needs recomputation to export correctly, fix the document in the GUI rather than adding the add-on to CI.
- Being called is declared under `on.workflow_call`, including a workflow-level `outputs.artifact`. A reusable workflow must redeclare its outputs there; a job-level `outputs:` alone hands the caller an empty string with no error.

`.github/workflows/release.yaml` fires on any pushed `v*` tag, calls `step-files.yaml` first, and attaches **two** assets to the release: `<repo-name>.zip` containing every `*.FCStd`, and `<repo-name>-<tag>-steps.zip` containing the generated STEP files flattened into a single directory.

- DXF and SVG unfold drawings are still not in any bundle; they are hand-made and unreliably generated (see the June 2025 note in the README).
- The STEP bundle is flattened with `zip -j`, so two parts sharing a basename would silently overwrite each other. The release workflow detects collisions and fails; if it fires, rename the manifest output for the new part rather than renaming a body.
- Tag format is `v<version>` (`v0` exists) and release titles are `Version <version>`. Don't create or push tags unless explicitly asked.

## Sanity checks an agent can actually run

- `make check` regenerates every STEP file and verifies each one reads back with the same volume as the model. This is the primary check.
- `make list` and `make step-files` show what the manifest declares.
- List bodies and parameters with a short `freecadcmd` script (`PartDesign::Body` labels, `thickness`, `BoundBox`, `Volume`).
- Confirm a STEP export's units and body count from its `ISO-10303-21` header.
- Inspect object names and history without FreeCAD via `unzip -p <Model>.FCStd Document.xml` — a `.FCStd` is a zip.
- Cross-check every part number, quantity, and installation step in `README.md` against the model it documents; README accuracy is the highest-value review an automated agent can do here.
- Verify derived filenames against rule 4.
