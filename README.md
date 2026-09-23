# Hex Python into EXE

A small local web app for turning Python code into an executable with PyInstaller.

## Features

- Live Python code editor
- Open/select a local `.py` file
- Edit the code directly in the browser
- Save the current code back to a `.py` file
- Build a Windows `.exe` with PyInstaller
- One-file or one-directory builds
- Optional windowed mode

## Run

Use Python on the machine that will perform the build:

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

### Important

PyInstaller creates executables for the operating system it runs on. To produce a Windows `.exe`, run this project on Windows (or use a Windows build environment/CI runner).
