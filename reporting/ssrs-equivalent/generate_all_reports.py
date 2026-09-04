"""
Batch Report Generator CLI for PropLedger.
Generates all 14 standard institutional reports in both Excel (.xlsx)
and PDF (.pdf) formats into the output directory.
Fulfills requirement PL-112.
"""
import os
import sys
import time
from pathlib import Path

# Add current directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from registry import ReportRegistry


def generate_all():
    output_dir = CURRENT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    reports = ReportRegistry.list_reports()
    print("=" * 105)
    print(f"PROPLEDGER SSRS-EQUIVALENT BATCH REPORT RUNNER — {len(reports)} REPORTS")
    print("=" * 105)
    print(f"{'Code':<8} {'Report Title':<38} {'Rows':<6} {'Excel':<12} {'PDF':<12} {'Time':<8} {'Status'}")
    print("-" * 105)

    total_start = time.time()
    generated_count = 0

    for meta in reports:
        code = meta["report_code"]
        title = meta["title"]
        report = ReportRegistry.get_report(code)
        if not report:
            continue

        rep_start = time.time()
        try:
            # 1. Fetch data
            data = report.fetch_data()
            row_count = len(data)

            # 2. Export Excel
            safe_name = title.lower().replace(" ", "_").replace("&", "and").replace("/", "_")[:30]
            excel_filename = f"{code.lower()}_{safe_name}.xlsx"
            excel_path = output_dir / excel_filename
            excel_bytes = report.export_excel(output_path=str(excel_path))
            excel_size = f"{len(excel_bytes) / 1024:.1f} KB"

            # 3. Export PDF
            pdf_filename = f"{code.lower()}_{safe_name}.pdf"
            pdf_path = output_dir / pdf_filename
            pdf_bytes = report.export_pdf(output_path=str(pdf_path))
            pdf_size = f"{len(pdf_bytes) / 1024:.1f} KB"

            elapsed = f"{time.time() - rep_start:.2f}s"
            print(f"{code:<8} {title[:36]:<38} {row_count:<6} {excel_size:<12} {pdf_size:<12} {elapsed:<8} SUCCESS")
            generated_count += 1
        except Exception as exc:
            elapsed = f"{time.time() - rep_start:.2f}s"
            print(f"{code:<8} {title[:36]:<38} {'ERR':<6} {'-':<12} {'-':<12} {elapsed:<8} FAILED: {exc}")

    total_time = time.time() - total_start
    print("-" * 105)
    print(f"Total Completed: {generated_count}/{len(reports)} reports ({generated_count * 2} files generated) in {total_time:.2f}s")
    print(f"Artifacts Location: {output_dir}")
    print("=" * 105)


if __name__ == "__main__":
    generate_all()
