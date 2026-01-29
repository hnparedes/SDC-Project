# Overview
This serves as a guide to get used to the src layout of Python projects.

The project is maintained using uv, and I recommend using it. Though, you can also maintain it with a standard pip.

# Layout
- docs: Contains documentation. So far, only the project layout
- data (if needed): Will contain any locally stored data.
- src: Contains all the source code
  - sdc_archiver: The package containing all the code for the SDC Archiver
  - sdc_viewer: The package containing all the code for the SDC Viewer
- tests: Where all the unit and integration testing will be. Layout unknown as of now.
- .gitingore
- .python-version: The minimum version required for the project to run. I have the minimum version currently set to **3.10**
- main.py: Main code block. It's probably just going to go around and call functions from the other packages.
- pyproject.toml: The file that contains all project dependencies. It's the requirements.txt document on steroids.
- README.md: Will contain all front-facing documentation for the users

# How to get it all set up for programming
## With UV
These instructions assume terminal
1. git clone the repo, either using ssh (with an SSH Key) or http.
2. `uv venv` to create a .venv in the project directory
3. `uv pip install -e .` to install the requirements AND the code in the src directory. Now the packages can be imported when testing and running.
