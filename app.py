from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
BUILD_DIR = BASE_DIR / "builds"
BUILD_DIR.mkdir(exist_ok=True)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/build")
def build_exe():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    filename = data.get("filename", "main.py")
    onefile = bool(data.get("onefile", True))
    windowed = bool(data.get("windowed", False))

    if not code.strip():
        return jsonify(error="Python code is empty."), 400

    safe_name = Path(filename).name
    if not safe_name.endswith(".py"):
        safe_name += ".py"
    stem = Path(safe_name).stem or "main"

    work = Path(tempfile.mkdtemp(prefix="hexpy_", dir=BUILD_DIR))
    script = work / safe_name
    script.write_text(code, encoding="utf-8")
    dist = work / "dist"
    spec = work / f"{stem}.spec"

    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean"]
    if onefile:
        command.append("--onefile")
    else:
        command.append("--onedir")
    if windowed:
        command.append("--windowed")
    command += ["--distpath", str(dist), "--workpath", str(work / "work"), "--specpath", str(work), str(script)]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        shutil.rmtree(work, ignore_errors=True)
        return jsonify(error="Build timed out after 5 minutes."), 408

    if result.returncode != 0:
        log = (result.stdout + "\n" + result.stderr).strip()
        return jsonify(error="PyInstaller build failed.", log=log[-12000:]), 500

    exe_name = stem + (".exe" if sys.platform.startswith("win") else "")
    artifact = dist / exe_name
    if not artifact.exists():
        candidates = list(dist.glob("*"))
        if not candidates:
            return jsonify(error="Build completed but no output file was found.", log=result.stdout[-12000:]), 500
        artifact = candidates[0]

    return send_file(artifact, as_attachment=True, download_name=artifact.name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
