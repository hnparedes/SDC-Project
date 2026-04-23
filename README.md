# Secure Data Container (zip-archive based) and a Viewer
Project was made for a CEN 4033: Secure Software Engineering class.

# Overview

The project contains two pieces of software: 
1. **SDC Archiver:** Creates an Secure Data Container (SDC), an encrypted, password-protected 7z file containing files and an Access Control Matrix (ACM). The ACM contains a list of access levels, a list of users paired with access levels, and a list of documents paired with one or more access levels.
2. **SDC Viewer:** Opens and decrypts an SDC when provided the correct password. After logging in with certain credentials, the Viewer will only allow that user to decrypt files from the archive that they have access to with their access level specified in the ACM.

## Supported OSes
The project was tested on the following:
- **Windows 11**
- **MacOS Tahoe 26.4**
- The following Linux distros:
  - **CachyOS** (Arch-based)
  - **Linux Mint** (Debian-based)

# How to Run
Download *TBA* from Releases

# Compiling (devs only)
**NOTE: You will need the super secret ackey (Access Control Key) to be able to compile or build the programs yourself. Only the devs have it, as the ackey is not version controlled for *security***

## Pre-Requisites
- make: [[https://gunwin32.sourceforge.net/packages/make.html]]
  - If on Windows, you can also use a Windows package manager such as scoop or choclatey.
- uv (only if compiling): [[https://docs.astral.sh/uv/getting-started/installation]]

## Instructions
1. git clone the repo, either using ssh (with an SSH Key) or http.
2. `uv venv` to create a virtual environment.
3. `uv sync` to download/update dependencies.
4. Run either *make* command to build the program:
    - `make build-archiver`: Build the SDC Archiver program
    - `make build-viewer`: Build the SDC Viewer program
