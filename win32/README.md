# Windows Release

## Requirements

1. Clone or download the code (https://www.github.com/jooyeshgar/amir)
2. Install [python 2.7](https://www.python.org/downloads/)
3. Install PyInstaller with pip `pip.exe install pyinstaller`
4. Install [PyGTK with all-in-one installer](http://www.pygtk.org/downloads.html)
5. Install [GTK+ for Windows Runtime Environment >= v2.24.10](https://sourceforge.net/projects/gtk-win/)
6. Install project dependencies in `requirements.txt` with pip
6. Install [Nullsoft Scriptable Install System](https://sourceforge.net/projects/nsis/)

## Compiling

1. `cd path\to\code`
2. `cd win32\`
3. `pyinstaller --clean amir.spec`

## Creating Installer

Compile the `amirsetup.nsi` file
