![Registry Spy](https://github.com/andyjsmith/Registry-Spy/raw/master/registryspy/img/wordmark.png)

![](https://img.shields.io/github/v/release/andyjsmith/Registry-Spy)
![](https://img.shields.io/github/downloads/andyjsmith/Registry-Spy/total)

# Registry Spy: Cross-Platform Windows Registry Browser

Registry Spy is a free, open-source cross-platform Windows Registry viewer. It is a fast, modern, and versatile explorer for raw registry files.

Features include:

- Windows, macOS, and Linux support
- Fast, on-the-fly parsing means no upfront overhead
- Open multiple hives at a time
- Searching
- Hex viewer
- Modification timestamps

## Requirements

- Python 3.8+

## Installation

Download the latest version from the [releases page](https://github.com/andyjsmith/Registry-Spy/releases). Alternatively, use one of the following methods.

### pip (recommended)

1. `pip install registryspy`
2. `registryspy`

### Manual

1. `pip install -r requirements.txt`
2. `python setup.py install`
3. `registryspy`

### Standalone

1. `pip install -r requirements.txt`
2. `python registryspy.py`

## Screenshots

#### Main Window

![Main Window](https://github.com/andyjsmith/Registry-Spy/raw/master/screenshots/main.png)

#### Find Dialog

![Find Dialog](https://github.com/andyjsmith/Registry-Spy/raw/master/screenshots/find.png)

## Building

Dependencies:

- PyInstaller 5.10+

Delete any existing venv, dist, and build directories.

Create and activate a new venv and install the requirements.txt and pyinstaller.

Regular building:
`pyinstaller registryspy_install.spec`

Creating a single file: `pyinstaller registryspy_onefile.spec`

Create the EXE installer with Inno Setup.

PyPI:

- `pip3 install build twine`
- `python3 -m build`
- `twine upload -r testpypi dist/*`
- `pip3 install -i https://test.pypi.org/simple/ registryspy`
- `twine upload dist/*`

## License

Registry Spy

Copyright (C) 2023 Andy Smith

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
