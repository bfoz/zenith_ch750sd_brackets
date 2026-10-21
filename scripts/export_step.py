"""Export fabrication STEP files from the FreeCAD documents.

Run with FreeCAD's console interpreter, not system Python:

    freecadcmd scripts/export_step.py

Generated files land in the step directory at the repository root.
All filenames must be unique, because the directory is flat and is what gets zipped into a release.

Configuration is read from the environment, because freecadcmd treats any argument after the script name as a document to open:

    ZENITH_STEP_DIR       output directory      (default step)
    ZENITH_STEP_MANIFEST  manifest to read      (default scripts/parts.manifest)
    ZENITH_STEP_ONLY      comma-separated documents to build
    ZENITH_STEP_FORCE     nonzero rebuilds everything, ignoring timestamps

Each document is opened, the requested bodies are written with Import.export, and the document is closed *without saving*. Never save from this script: a document opened without the Sheet Metal workbench installed has already lost the Python proxy for its BaseShape features, and saving would flatten those features permanently and unrecoverably.

The script therefore relies entirely on the cached shape stored in the file and never recomputes. If a model needs recomputation, do that in the FreeCAD GUI with the workbench installed, then re-export.

Two freecadcmd quirks this file works around:
  * arguments after the script name are treated as documents to open, so all configuration arrives via the env vars above.
  * stdout is not flushed when the script calls sys.exit(), and an uncaught exception exits 0.
    Output is flushed explicitly and every failure path calls sys.exit().
"""

import os
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
REPO = SCRIPT_PATH.parent.parent
os.chdir(REPO)

# Output directory and manifest may be overridden, so they are resolved after the chdir.
OUTPUT_DIR = Path(os.environ.get("ZENITH_STEP_DIR") or "step").resolve()
MANIFEST_PATH = Path(os.environ.get("ZENITH_STEP_MANIFEST") or Path("scripts") / "parts.manifest")

# Volume tolerance for the read-back check, in mm3.
# STEP round-tripping is lossless for these parts in practice, so anything above this is a real fault rather than floating point noise.
VOLUME_TOLERANCE = 1e-4


def emit(msg):
    print(msg)
    sys.stdout.flush()


def fail(msg):
    print("ERROR: %s" % msg, file=sys.stderr)
    sys.stderr.flush()
    sys.exit(1)


def check_args(argv):
    """Reject stray arguments, which freecadcmd would otherwise open as documents."""
    extra = [arg for arg in argv[1:] if Path(arg).resolve() != SCRIPT_PATH]
    if extra:
        fail("unexpected arguments: %s (freecadcmd opens these as documents; "
             "use ZENITH_STEP_MANIFEST / ZENITH_STEP_ONLY instead)" % " ".join(extra))


try:
    import FreeCAD
    import Import
    import Part
except ImportError as exc:
    fail("this script must run inside FreeCAD: freecadcmd scripts/export_step.py (%s)" % exc)


def parse_manifest(path):
    """Return a list of (document, body label, output filename) tuples.

    Output filenames are relative to OUTPUT_DIR, and must be unique across the whole manifest.
    The directory is flat because that is what gets zipped into a release, so a collision would
    silently overwrite one part with another rather than failing.
    """
    parts = []
    seen = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = [field.strip() for field in line.split("|")]
        if len(fields) != 3:
            fail("%s:%d: expected 'document | body | output', got: %s" % (path, lineno, line))
        document, label, filename = fields
        relative = Path(filename)
        if relative.is_absolute() or ".." in relative.parts:
            fail("%s:%d: output must stay inside the output directory: %s" % (path, lineno, filename))
        if relative.name in seen:
            fail("%s:%d: output filename %s collides with the entry on line %d"
                 % (path, lineno, relative.name, seen[relative.name]))
        seen[relative.name] = lineno
        parts.append((document, label, relative))
    if not parts:
        fail("no parts listed in %s" % path)
    return parts


def bodies_by_label(doc):
    """Map body Label to object.

    Label lookup has to be done by hand.
    FreeCAD's getObject() takes an internal name, so labels containing spaces ('Top Bracket') never resolve through it.
    """
    return {obj.Label: obj for obj in doc.Objects if obj.TypeId == "PartDesign::Body"}


def check_shape(body, label, document):
    shape = body.Shape
    if shape.isNull():
        fail("%s / %s has a null shape. Recompute and save it in the FreeCAD GUI "
             "with the Sheet Metal workbench installed." % (document, label))
    if not shape.isValid():
        fail("%s / %s has invalid geometry" % (document, label))
    if not shape.Solids:
        fail("%s / %s contains no solids" % (document, label))
    if shape.Volume <= 0:
        fail("%s / %s has non-positive volume %s" % (document, label, shape.Volume))
    return shape


def write_step(body, shape, document, label, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a scratch path first, so a failure can never leave a truncated file that then looks up to date.
    # The scratch name has to keep the .step extension because Import.export picks the exporter from the extension.
    tmp_path = out_path.with_name(out_path.stem + ".tmp.step")
    try:
        Import.export([body], str(tmp_path))
        if not tmp_path.is_file() or tmp_path.stat().st_size == 0:
            fail("%s / %s produced an empty STEP file" % (document, label))
        check = Part.Shape()
        check.read(str(tmp_path))
        if check.isNull() or not check.isValid():
            fail("%s: written STEP does not read back as valid geometry" % out_path.name)
        if abs(check.Volume - shape.Volume) > VOLUME_TOLERANCE:
            fail("%s: written STEP volume %.4f differs from model %.4f"
                 % (out_path.name, check.Volume, shape.Volume))
        tmp_path.replace(out_path)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise
    emit("  %-58s vol=%9.2f mm3" % (out_path.name, shape.Volume))


def output_is_current(document, out_path, force):
    """True when the STEP file exists and is newer than its source document.

    Staleness lives here rather than in make, which handles the space-containing filenames badly.
    Deleting a generated file therefore always rebuilds it.
    """
    if force or not out_path.is_file():
        return False
    return out_path.stat().st_mtime >= (REPO / document).stat().st_mtime


def export_document(document, requests, force):
    """Open one document once and export the bodies of it that are stale."""
    stale, fresh = [], []
    for label, out_path in requests:
        (fresh if output_is_current(document, out_path, force) else stale).append((label, out_path))

    for _, out_path in fresh:
        emit("  %-58s up to date" % out_path.name)
    if not stale:
        return

    doc = FreeCAD.openDocument(str(REPO / document))
    try:
        bodies = bodies_by_label(doc)
        for label, out_path in stale:
            if label not in bodies:
                fail("%s has no body named '%s'. Available: %s"
                     % (document, label, ", ".join(sorted(bodies)) or "(none)"))
            body = bodies[label]
            shape = check_shape(body, label, document)
            write_step(body, shape, document, label, out_path)
    finally:
        # Drop the document without saving.
        # openDocument has no flag to stop an implicit save, so the rule is simply: never call save().
        FreeCAD.closeDocument(doc.Name)


def main():
    check_args(sys.argv)

    if not MANIFEST_PATH.is_file():
        fail("manifest not found: %s" % MANIFEST_PATH)

    # Like the document filter, the force flag arrives by environment variable.
    # freecadcmd rejects unknown --options before they ever reach this script.
    force = os.environ.get("ZENITH_STEP_FORCE", "") not in ("", "0")
    only = [name.strip() for name in os.environ.get("ZENITH_STEP_ONLY", "").split(",") if name.strip()]

    parts = parse_manifest(MANIFEST_PATH)
    if only:
        wanted = set(only)
        unknown = wanted - {document for document, _, _ in parts}
        if unknown:
            fail("ZENITH_STEP_ONLY names no parts in %s: %s" % (MANIFEST_PATH, ", ".join(sorted(unknown))))
        parts = [part for part in parts if part[0] in wanted]

    emit("%s %d parts from %s into %s"
         % ("Exporting" if force else "Checking", len(parts), MANIFEST_PATH, OUTPUT_DIR))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Group by document so each file is opened at most once.
    for document in dict.fromkeys(part[0] for part in parts):
        emit("%s" % document)
        requests = [(label, OUTPUT_DIR / filename)
                    for part_doc, label, filename in parts if part_doc == document]
        export_document(document, requests, force)

    emit("Done.")


try:
    main()
except SystemExit:
    raise
except BaseException:  # freecadcmd exits 0 on an uncaught exception
    import traceback
    traceback.print_exc()
    sys.stderr.flush()
    sys.exit(1)
