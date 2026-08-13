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
    report_folder.mkdir(parents=True, exist_ok=True)

    print("🔍 Running Checkov...")
    checkov = run_checkov()

    print("🔍 Running TFLint...")
    tflint = run_tflint()

    print("🔍 Running Gitleaks...")
    gitleaks = run_gitleaks()

    report = f"""
========================================
       SecureIaC Guardrail Report
========================================

CHECKOV
----------------------------------------
Return Code: {checkov.returncode}

{checkov.stdout}

{checkov.stderr}


TFLINT
----------------------------------------
Return Code: {tflint.returncode}

{tflint.stdout}

{tflint.stderr}


GITLEAKS
----------------------------------------
Return Code: {gitleaks.returncode}

{gitleaks.stdout}

{gitleaks.stderr}


========================================
             FINAL RESULT
========================================

Checkov : {"FAILED" if checkov.returncode != 0 else "PASSED"}
TFLint  : {"FAILED" if tflint.returncode != 0 else "PASSED"}
Gitleaks: {"FAILED" if gitleaks.returncode != 0 else "PASSED"}

========================================
"""

    # Always create the report BEFORE deciding whether to fail
    report_file = report_folder / "guardrail_report.txt"

    report_file.write_text(
        report,
        encoding="utf-8"
    )

    print(report)
    print(f"📄 Report created: {report_file}")

    # Security gate
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