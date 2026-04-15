The project is maintained through uv, a Python package and project manager. Please follow the steps to be able to test the code.

Pre-requisites:
- make: [[https://gnuwin32.sourceforge.net/packages/make.htm]] or using a Windows package manager such as scoop or choclatey.
- uv: [[https://docs.astral.sh/uv/getting-started/installation/]]

# Setup Project for Editing and Testing
1. git clone the repo, either using ssh (with an SSH Key) or http.
2. `uv venv` to create a virtual environment.
3. `uv sync` to sync all the dependencies. We are using uv workspaces to manage each individual package (don't worry about the specifics, I'll worry about them).
4. Due to executables files being under *five layers of directories*, running `uv run (name_of_file)` is cumbersome. Instead, there is a **Makefile** in the project root. 
The Makefile contains aliases that run the long cumbersome commands.

## Make command master list
- `make run-archiver`: Runs the archiver program
- `make run-viewer`: Runs the viewer program 

# Adding or removing dependencies
1. `uv add (dependency_name)` will auto-magically add an external dependency to the project. Note that internal python modules (e.g., tkinter) will throw an error if you try to add it. Just import it.
2. `uv remove (dependency_name)` will remove that dependency from the project.

# Using pytest
Pytest is how you do unit and integration testing. It is complex and versatile.

The pyproject.toml file already has pytest stuff configured by me, so thankfully you don't have to worry about configuring it.

Some cool commands  *(incomplete)*
- `uv run pytest` : Runs every test.

# For Testing the viewer
- Check `normalsdc.txt`
