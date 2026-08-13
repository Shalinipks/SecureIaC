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
{checkov.stderr}

--- TFLint ---
{tflint.stdout}
{tflint.stderr}

--- Gitleaks ---
{gitleaks.stdout}
{gitleaks.stderr}

========================================
"""

    report_file = report_folder / "guardrail_report.txt"
    report_file.write_text(report, encoding="utf-8")

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