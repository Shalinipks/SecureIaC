import os
import shutil
import subprocess
from pathlib import Path


def run_checkov():
    print("🔍 Running Checkov...")

    checkov = shutil.which("checkov")

    if not checkov:
        raise FileNotFoundError("Checkov executable not found")

    return subprocess.run(
        [checkov, "-d", ".", "--quiet"],
        capture_output=True,
        text=True
    )


def run_tflint():
    print("🔍 Running TFLint...")

    tflint = shutil.which("tflint")

    if not tflint:
        raise FileNotFoundError("TFLint executable not found")

    return subprocess.run(
        [tflint],
        capture_output=True,
        text=True
    )


def run_gitleaks():
    print("🔍 Running Gitleaks...")

    gitleaks = shutil.which("gitleaks")

    if not gitleaks:
        if os.path.exists("/usr/local/bin/gitleaks"):
            gitleaks = "/usr/local/bin/gitleaks"
        else:
            raise FileNotFoundError("Gitleaks executable not found")

    return subprocess.run(
        [
            gitleaks,
            "dir",
            ".",
            "--no-banner",
            "--gitleaks-ignore-path",
            ".gitignore"
        ],
        capture_output=True,
        text=True
    )


def main():
    report_folder = Path("reports")
    report_folder.mkdir(exist_ok=True)

    checkov = run_checkov()
    tflint = run_tflint()
    gitleaks = run_gitleaks()

    report = f"""
========================================
       SecureIaC Guardrail Report
========================================

--- Checkov ---
{checkov.stdout}

--- TFLint ---
{tflint.stdout}

--- Gitleaks ---
{gitleaks.stdout}

========================================
"""

    report_file = report_folder / "guardrail_report.txt"
    report_file.write_text(report)

    print(report)

    if checkov.returncode != 0:
        print("❌ Checkov found security issues.")
        raise SystemExit(1)

    if tflint.returncode != 0:
        print("❌ TFLint found issues.")
        raise SystemExit(1)

    if gitleaks.returncode != 0:
        print("❌ Gitleaks found secrets.")
        raise SystemExit(1)

    print("✅ All security checks passed.")


if __name__ == "__main__":
    main()