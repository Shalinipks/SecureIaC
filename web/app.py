from flask import Flask, request, jsonify, send_from_directory
import subprocess
import tempfile
import os
import shutil

app = Flask(__name__, static_folder=".")


def find_tool(name):
    """Find a security tool available on the system."""

    path = shutil.which(name)

    if path:
        return path

    local_app_data = os.environ.get("LOCALAPPDATA", "")

    search_root = os.path.join(
        local_app_data,
        "Microsoft",
        "WinGet",
        "Packages"
    )

    if os.path.exists(search_root):
        for root, dirs, files in os.walk(search_root):
            for file in files:
                if file.lower() in {
                    name.lower(),
                    name.lower() + ".exe",
                    name.lower() + ".cmd"
                }:
                    return os.path.join(root, file)

    return None


def run_command(command):
    """Run a security command safely."""

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "returncode": result.returncode,
            "stdout": result.stdout or "",
            "stderr": result.stderr or ""
        }

    except subprocess.TimeoutExpired:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "Security scan timed out after 120 seconds."
        }

    except Exception as error:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": str(error)
        }


def run_checkov(folder):
    tool = find_tool("checkov")

    if not tool:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "Checkov executable not found."
        }

    return run_command([
        tool,
        "-d",
        folder,
        "--compact"
    ])


def run_tflint(folder):
    tool = find_tool("tflint")

    if not tool:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "TFLint executable not found."
        }

    return run_command([
        tool,
        "--chdir",
        folder
    ])


def run_gitleaks(folder):
    tool = find_tool("gitleaks")

    if not tool:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "Gitleaks executable not found."
        }

    return run_command([
        tool,
        "detect",
        "--source",
        folder,
        "--no-banner",
        "--exit-code",
        "1"
    ])


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/scan", methods=["POST"])
def scan():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No scan data received."
        }), 400

    terraform_code = data.get("code", "")

    if not terraform_code.strip():
        return jsonify({
            "error": "Please enter Terraform code."
        }), 400

    with tempfile.TemporaryDirectory() as temp_dir:

        terraform_file = os.path.join(
            temp_dir,
            "main.tf"
        )

        with open(
            terraform_file,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(terraform_code)

        print("\n🔍 Running Checkov...")
        checkov = run_checkov(temp_dir)

        print("🔍 Running TFLint...")
        tflint = run_tflint(temp_dir)

        print("🔍 Running Gitleaks...")
        gitleaks = run_gitleaks(temp_dir)

        checkov_output = (
            checkov["stdout"] +
            checkov["stderr"]
        ).strip()

        tflint_output = (
            tflint["stdout"] +
            tflint["stderr"]
        ).strip()

        gitleaks_output = (
            gitleaks["stdout"] +
            gitleaks["stderr"]
        ).strip()

        checks = {
            "checkov": checkov["returncode"] == 0,
            "tflint": tflint["returncode"] == 0,
            "gitleaks": gitleaks["returncode"] == 0
        }

        passed_count = sum(checks.values())

        score = round(
            (passed_count / 3) * 100
        )

        if score == 100:
            status = "SECURE"
        elif score >= 66:
            status = "NEEDS ATTENTION"
        else:
            status = "SECURITY ISSUES"

        report = f"""
========================================
        SECUREIAC SECURITY REPORT
========================================

Security Score: {score}/100
Status: {status}

----------------------------------------
CHECKOV
----------------------------------------

Status: {"PASSED" if checks["checkov"] else "ISSUES DETECTED"}

{checkov_output if checkov_output else "No Checkov findings."}

----------------------------------------
TFLINT
----------------------------------------

Status: {"PASSED" if checks["tflint"] else "ISSUES DETECTED"}

{tflint_output if tflint_output else "No TFLint findings."}

----------------------------------------
GITLEAKS
----------------------------------------

Status: {"PASSED" if checks["gitleaks"] else "ISSUES DETECTED"}

{gitleaks_output if gitleaks_output else "No secrets detected."}

========================================
"""

        print("\n" + report)

        return jsonify({
    "success": True,
    "score": score,
    "status": status,

    "passed": score == 100,

    "checks": checks,

    "checkov": {
        "passed": checks["checkov"],
        "output": checkov_output
    },

    "tflint": {
        "passed": checks["tflint"],
        "output": tflint_output
    },

    "gitleaks": {
        "passed": checks["gitleaks"],
        "output": gitleaks_output
    },

    "report": report
})


if __name__ == "__main__":

    print("\n========================================")
    print("        SecureIaC Web Scanner")
    print("========================================")
    print("Open: http://127.0.0.1:5000")
    print("========================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )