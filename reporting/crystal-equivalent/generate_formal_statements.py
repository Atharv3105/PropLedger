"""
Batch Generator CLI for Crystal Reports Equivalent Formal Statements.
Generates all 3 institutional statement PDFs into the output directory.
"""
import sys
import time
from pathlib import Path

# Add current directory to sys.path
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CURRENT_DIR))

from statement_registry import StatementRegistry


def generate_all_statements():
    output_dir = CURRENT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    statements = StatementRegistry.list_statements()
    print("=" * 95)
    print(f"PROPLEDGER CRYSTAL-EQUIVALENT FORMAL STATEMENTS RUNNER — {len(statements)} STATEMENTS")
    print("=" * 95)
    print(f"{'Code':<8} {'Statement Title':<45} {'PDF Size':<14} {'Time':<8} {'Status'}")
    print("-" * 95)

    total_start = time.time()
    success_count = 0

    for meta in statements:
        code = meta["statement_code"]
        title = meta["title"]
        stmt = StatementRegistry.get_statement(code)
        if not stmt:
            continue

        start = time.time()
        try:
            safe_name = title.lower().replace(" ", "_").replace("&", "and").replace("/", "_")[:35]
            pdf_filename = f"{code.lower()}_{safe_name}.pdf"
            pdf_path = output_dir / pdf_filename

            pdf_bytes = stmt.export_pdf(output_path=str(pdf_path))
            pdf_size = f"{len(pdf_bytes) / 1024:.1f} KB"
            elapsed = f"{time.time() - start:.2f}s"

            print(f"{code:<8} {title[:43]:<45} {pdf_size:<14} {elapsed:<8} SUCCESS")
            success_count += 1
        except Exception as exc:
            elapsed = f"{time.time() - start:.2f}s"
            print(f"{code:<8} {title[:43]:<45} {'-':<14} {elapsed:<8} FAILED: {exc}")

    total_time = time.time() - total_start
    print("-" * 95)
    print(f"Total Completed: {success_count}/{len(statements)} formal statements generated in {total_time:.2f}s")
    print(f"Artifacts Location: {output_dir}")
    print("=" * 95)


if __name__ == "__main__":
    generate_all_statements()
