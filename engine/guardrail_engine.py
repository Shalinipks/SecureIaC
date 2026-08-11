import subprocess
import sys
from pathlib import Path


CHECKOV = "checkov"


def run_checkov():
    print("\n🔍 Running Checkov...\n")

    return subprocess.run(
        [CHECKOV, "-d", "terraform"],
        capture_output=True,
        text=True
    )


def run_tflint():
    print("\n🔍 Running TFLint...\n")

    return subprocess.run(
        ["tflint", "--chdir=terraform"],
        capture_output=True,
        text=True
    )


def run_gitleaks():
    print("\n🔍 Running Gitleaks...\n")

    return subprocess.run(
        ["gitleaks", "dir", "engine"],
        capture_output=True,
        text=True
    )


def main():
    report_folder = Path("reports")
    report_folder.mkdir(exist_ok=True)

    checkov = run_checkov()
    tflint = run_tflint()
    gitleaks = run_gitleaks()

    print(checkov.stdout)
    print(tflint.stdout)
    print(gitleaks.stdout)

    report = report_folder / "security_report.txt"

    with open(report, "w", encoding="utf-8") as file:
        file.write("===== CHECKOV RESULTS =====\n")
        file.write(checkov.stdout)

        file.write("\n\n===== TFLINT RESULTS =====\n")
        file.write(tflint.stdout)

        file.write("\n\n===== GITLEAKS RESULTS =====\n")
        file.write(gitleaks.stdout)

    if checkov.returncode != 0 or tflint.returncode != 0 or gitleaks.returncode != 0:
        print("\n❌ SECURITY/CODE QUALITY ISSUES DETECTED!")
        print(f"📄 Report saved to: {report}")
        sys.exit(1)

    print("\n✅ ALL CHECKS PASSED!")
    print(f"📄 Report saved to: {report}")


if __name__ == "__main__":
    main()