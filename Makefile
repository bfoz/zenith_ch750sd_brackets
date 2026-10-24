# Generate fabrication STEP files from the FreeCAD documents.
# See `make help`.

MANIFEST := scripts/parts.manifest
STEP_DIR := step

# The document list comes from the manifest, not from `wildcard *.FCStd`.
# The repository also holds .FCStd files that are not part models (ch750sd), and those must not become make targets.
# The hash in the comment-matching pattern is escaped: make treats # as a comment in a variable assignment, but not inside a recipe.
PART_NAMES := $(shell awk -F'|' \
	'/^[[:space:]]*\#/ || /^[[:space:]]*$$/ { next } \
	NF == 3 { \
		gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$1); \
		sub(/\.FCStd$$/, "", $$1); sub(/.*\//, "", $$1); \
		if (!seen[$$1]++) print $$1 \
	}' $(MANIFEST))

# FreeCAD's console interpreter. Override with: make FREECAD=/path/to/freecadcmd
FREECAD_CANDIDATES := freecadcmd /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd
FREECAD ?= $(shell \
	for candidate in $(FREECAD_CANDIDATES); do \
		found=$$(command -v "$$candidate" 2>/dev/null); \
		if [ -n "$$found" ]; then echo "$$found"; exit; fi; \
		if [ -x "$$candidate" ]; then echo "$$candidate"; exit; fi; \
	done)

export LC_ALL := C
export ZENITH_STEP_DIR := $(STEP_DIR)

.PHONY: all check force list step-files clean clean-steps help $(PART_NAMES)

# The export script decides what is stale: a STEP file is rebuilt when it is missing or older than its source document.
# Staleness lives in the script rather than in make because one document produces several STEP files whose names contain spaces.
all:
	@if [ -z "$(FREECAD)" ]; then \
		echo "freecadcmd not found; install FreeCAD 1.1 or run: make FREECAD=/path/to/freecadcmd" >&2; \
		exit 1; \
	fi
	ZENITH_STEP_MANIFEST="$(MANIFEST)" $(FREECAD) scripts/export_step.py

# Re-export every part regardless of timestamps.
force:
	@if [ -z "$(FREECAD)" ]; then \
		echo "freecadcmd not found; install FreeCAD 1.1 or run: make FREECAD=/path/to/freecadcmd" >&2; \
		exit 1; \
	fi
	ZENITH_STEP_MANIFEST="$(MANIFEST)" ZENITH_STEP_FORCE=1 $(FREECAD) scripts/export_step.py

# Build one document, e.g. `make TrailingEdgeBracket`. Honours timestamps, so it is a no-op when that document is current.
# The filter matches the document name as listed in the manifest.
$(PART_NAMES): %:
	@$(MAKE) --no-print-directory -e ZENITH_STEP_ONLY="$@.FCStd" all

# Export and verify everything from scratch.
# The script reads back each file it writes and fails if the geometry does not match the model.
# A clean run is therefore a real check, not merely exit code 0.
check: force

# Show the manifest as document / body / output columns.
list:
	@awk -F'|' '/^[[:space:]]*#/ || /^[[:space:]]*$$/ { next } NF == 3 { for (i = 1; i <= 3; i++) { gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$i) } printf "%-34s %-32s %s\n", $$1, $$2, $$3 }' $(MANIFEST)

# Print every output path under $(STEP_DIR), one per line, unpadded. Used by CI; needs no FreeCAD.
# Filenames contain spaces, so callers must read whole lines.
step-files:
	@awk -F'|' '/^[[:space:]]*#/ || /^[[:space:]]*$$/ { next } NF == 3 { gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$3); print "$(STEP_DIR)/" $$3 }' $(MANIFEST)

# Remove the declared outputs, leaving any stray scratch file in place.
clean-steps:
	@$(MAKE) --no-print-directory step-files | while IFS= read -r step_file; do \
		if [ -f "$$step_file" ]; then rm -f "$$step_file"; echo "Removed $$step_file"; fi; \
	done

# Remove the whole output directory, including scratch files left by an interrupted export.
clean:
	@rm -rf $(STEP_DIR)
	@echo "Removed $(STEP_DIR)"

help:
	@echo "Generate fabrication STEP files from the FreeCAD documents into $(STEP_DIR)/."
	@echo
	@echo "  make                 export stale parts (missing or out of date)"
	@echo "  make check           re-export and verify every part"
	@echo "  make force           same as check: ignore timestamps"
	@echo "  make list            show document / body / output for each part"
	@echo "  make step-files      print output paths, one per line (for CI)"
	@echo "  make <document>      build one document, e.g. make TrailingEdgeBracket"
	@echo "  make clean-steps     remove the declared STEP files"
	@echo "  make clean           remove $(STEP_DIR) entirely, including scratch files"
	@echo
	@echo "Documents: $(PART_NAMES)"
	@echo
	@echo "Uses freecadcmd from PATH, then the macOS FreeCAD.app location."
	@echo "Override with: make FREECAD=/path/to/freecadcmd"
