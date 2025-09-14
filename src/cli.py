import argparse
from pathlib import Path
from src.auditchecker.reconcile import reconcile


def main():
    ap = argparse.ArgumentParser(description="Audit Checker: reconcile two CSV/Excel files and output exceptions.")
    ap.add_argument("--a", required=True, help="Path to System A file (CSV/XLSX/XLS)")
    ap.add_argument("--b", required=True, help="Path to System B file (CSV/XLSX/XLS)")
    ap.add_argument("--keys", required=True, help="Comma-separated key columns")
    ap.add_argument("--compare", default="", help="Comma-separated columns to compare (default: all shared non-key)")
    ap.add_argument("--out", default="out", help="Output folder")
    args = ap.parse_args()

    keys = [c.strip() for c in args.keys.split(",") if c.strip()]
    compare_cols = [c.strip() for c in args.compare.split(",") if c.strip()] or None

    result = reconcile(args.a, args.b, keys=keys, compare_cols=compare_cols)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    result["missing_in_b"].to_csv(out_dir / "missing_in_b.csv", index=False)
    result["missing_in_a"].to_csv(out_dir / "missing_in_a.csv", index=False)
    result["mismatches"].to_csv(out_dir / "mismatches.csv", index=False)
    result["duplicates_a"].to_csv(out_dir / "duplicates_a.csv", index=False)
    result["duplicates_b"].to_csv(out_dir / "duplicates_b.csv", index=False)

    with open(out_dir / "summary.txt", "w", encoding="utf-8") as f:
        for k, v in result["summary"].items():
            f.write(f"{k}: {v}\n")

    print("Reconciliation complete. See output folder.")

        # --- HTML report ---
    html = f"""
    <html><head><meta charset="utf-8">
    <title>Audit Checker Report</title>
    <style>
    body{{font-family:Arial, sans-serif; padding:20px}}
    table{{border-collapse:collapse; margin:14px 0}}
    th,td{{border:1px solid #ddd; padding:6px 8px}}
    h1,h2,h3{{margin:12px 0}}
    pre{{background:#fafafa; border:1px solid #eee; padding:12px; white-space:pre-wrap}}
    .badge{{display:inline-block; padding:2px 8px; border-radius:12px; background:#eef; margin-left:8px}}
    </style>
    </head><body>
    <h1>Audit Checker Report <span class="badge">{Path(args.a).name} vs {Path(args.b).name}</span></h1>
    <h3>Summary</h3>
    <pre>{(out_dir / "summary.txt").read_text(encoding="utf-8")}</pre>

    <h3>Mismatches</h3>
    {result["mismatches"].to_html(index=False)}
    <h3>Missing in B</h3>
    {result["missing_in_b"].to_html(index=False)}
    <h3>Missing in A</h3>
    {result["missing_in_a"].to_html(index=False)}
    <h3>Duplicates A</h3>
    {result["duplicates_a"].to_html(index=False)}
    <h3>Duplicates B</h3>
    {result["duplicates_b"].to_html(index=False)}
    </body></html>
    """
    (out_dir / "report.html").write_text(html, encoding="utf-8")
    print(f"HTML report saved to {out_dir / 'report.html'}")


if __name__ == "__main__":
    main()


