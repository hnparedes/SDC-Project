# Secure Data Container (zip-archive based) and a Viewer
Project was made for a CEN 4033: Secure Software Engineering class.

# Overview

The project contains two pieces of software: 
1. **SDC Archiver:** Creates an Secure Data Container (SDC), an encrypted, password-protected 7z file containing files and an Access Control Matrix (ACM). The ACM contains a list of access levels, a list of users paired with access levels, and a list of documents paired with one or more access levels.
2. **SDC Viewer:** Opens and decrypts an SDC when provided the correct password. After logging in with certain credentials, the Viewer will only allow that user to decrypt files from the archive that they have access to with their access level specified in the ACM.

# Pre-requisites
The project was tested on the following OSes:
- **Windows 11**
- **MacOS Tahoe 26.4**
- The following Linux distros:
  - **CachyOS** (Arch-based)
  - **Linux Mint** (Debian-based)

## Make sure the following are installed 
- make: [[https:://gunwin32.sourceforge.net/packages/make.html]]
  - If on Windows, you can also use a Windows package manager such as scoop or choclatey.
- uv (only if compiling): [[https://docs.astral.sh/uv/getting-started/installation]]

# Compiling
1. git clone the repo, either using ssh (with an SSH Key) or http.
2. `uv venv` to create a virtual environment.
3. `uv sync` to download dependencies.
4. Run either *make* command to run the program:
  - `make run-archiver`: Runs the SDC Archiver program
  - `make run-viewer`: Runs the SDC Viewer program 



For how to set up the in-dev project during development, please check `docs/project_setup.md`
