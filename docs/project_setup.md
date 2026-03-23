The project is maintained through uv, a Python package and project manager. Please follow the steps to be able to test the code.

First step: download and install uv through one of its various methods of installation: [[https://docs.astral.sh/uv/getting-started/installation/]]

# Setup Project for Editing and Testing
1. git clone the repo, either using ssh (with an SSH Key) or http.
2. `uv venv` to create a .venv (virutal environment) in the project directory. (if there isn't one already)
3. `uv pip install -e .` to install the requirements and the code in the src directory. This is done so code in different files within the modules can be imported.
4. `uv run (name of file)` to run a file.

# Adding or removing dependencies
1. `uv add (dependency_name)` will auto-magically add an external dependency to the project. Note that internal python modules (e.g., tkinter) will throw an error if you try to add it. Just import it.
2. `uv remove (dependency_name)` will remove that dependency from the project.

# Using pytest
Pytest is how you do unit and integration testing. It is complex and versatile.

The pyproject.toml file already has pytest stuff configured by me, so thankfully you don't have to worry about configuring it.

Some cool commands  *(incomplete)*
- `uv pytest` : Runs every test (not recommended).
- `uv pytest -k (test_name)`: Run a specific test using a keyword expression
- Add a `-s` flag to show print statements in the output.
