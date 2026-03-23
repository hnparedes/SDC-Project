# Overview
This serves as a guide to get used to the src layout of Python projects.

The project is maintained using uv, and I recommend using it. Though, you can also maintain it with a standard pip.

# Layout
- docs: Contains documentation, such as the project layout and project support.
- data (if needed): Will contain any locally stored data.
- src: Contains all the source code
  - sdc_archiver: The package containing all the code for the SDC Archiver
  - sdc_viewer: The package containing all the code for the SDC Viewer
- tests: Where all the unit and integration testing will be. These will be committed in testing branches.
  - unit : Contains unit tests for mainly testing out single functions.
  - integration : Typically for testing whole files.
  - system : For testing the system as a whole.
- .gitignore
- .python-version: The minimum version required for the project to run. Set to **3.14.**
- main.py: Main code block. It's probably just going to go around and call functions from the other packages.
- pyproject.toml: The file that contains all project dependencies. It's the requirements.txt document on steroids.
- README.md: Will contain all front-facing documentation for the users
