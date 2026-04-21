The project is maintained through uv, a Python package and project manager. Please make sure it is installed.

# Make command master list
- `make run-archiver`: Runs the archiver program
- `make run-viewer`: Runs the viewer program 
- `make regen-test-sdc`: Regenerates `normalsdc.7z` and `normalsdc.json`. Run this after making any changes to the SDC or ACM format that might make old SDCs unreadable.
- `make clean`: Deletes the test output directory

# Adding or removing dependencies
1. `uv add (dependency_name)` will auto-magically add an external dependency to the project. Note that internal python modules (e.g., tkinter) will throw an error if you try to add it. Just import it.
2. `uv remove (dependency_name)` will remove that dependency from the project.

# Using pytest
Pytest is how you do unit and integration testing. It is complex and versatile.

The pyproject.toml file already has pytest stuff configured by me, so thankfully you don't have to worry about configuring it.

- `uv run pytest` : Runs every test.

# For Testing the viewer
- Check `normalsdc.txt`
