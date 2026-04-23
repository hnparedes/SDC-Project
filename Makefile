# The specific command to remove files is OS-dependent
ifeq ($(OS),Windows_NT)
	delcommand := del
else
	delcommand := rm -rf
endif

# Runs SDC Archiver Program
run-archiver:
	uv run ./packages/sdc_archiver/src/sdc_archiver/archiver_ui.py
# Runs SDC Viewer Program
run-viewer:
	uv run ./packages/sdc_viewer/src/sdc_viewer/viewer_ui.py
# Regenerate test SDC
regen-test-sdc:
	uv run ./scripts/regen_test_sdc.py
# Remove old test files
clean:
	$(delcommand) .test-output

build-archiver:
	uv run pyinstaller ./packages/sdc_archiver/src/sdc_archiver/archiver.spec --distpath ./bin/dist --workpath ./bin/build

build-viewer:
	uv run pyinstaller ./packages/sdc_viewer/src/sdc_viewer/viewer.spec --distpath ./bin/dist --workpath ./bin/build
