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
        [gitleaks, "dir", ".", "--no-banner"],
        capture_output=True,
        text=True
    )


def main():
    report_folder = Path("reports")
    report_folder.mkdir(exist_ok=True)

    checkov = run_checkov()
    tflint = run_tflint()
    gitleaks = run_gitleaks()

    print("\n===== SecureIaC Guardrail Report =====")

    print("\n--- Checkov ---")
    print(checkov.stdout)

    if checkov.stderr:
        print(checkov.stderr)

    print("\n--- TFLint ---")
    print(tflint.stdout)

    if tflint.stderr:
        print(tflint.stderr)

    print("\n--- Gitleaks ---")
    print(gitleaks.stdout)

    if gitleaks.stderr:
        print(gitleaks.stderr)

    # Save reports
    (report_folder / "checkov_report.txt").write_text(
        checkov.stdout + checkov.stderr
    )

    (report_folder / "tflint_report.txt").write_text(
        tflint.stdout + tflint.stderr
    )

    (report_folder / "gitleaks_report.txt").write_text(
        gitleaks.stdout + gitleaks.stderr
    )

    # Fail the workflow if any security check fails
    if checkov.returncode != 0:
        print("\n❌ Checkov found security issues.")
        raise SystemExit(1)

    if tflint.returncode != 0:
        print("\n❌ TFLint found issues.")
        raise SystemExit(1)

    if gitleaks.returncode != 0:
        print("\n❌ Gitleaks found secrets or sensitive information.")
        raise SystemExit(1)

    print("\n✅ All SecureIaC security checks passed successfully.")


if __name__ == "__main__":
    main()