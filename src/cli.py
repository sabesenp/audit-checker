import argparse
from pathlib import Path
from auditchecker.reconcile import reconcile

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
            f.write(f"{k}: {v}\\n")

    print("Reconciliation complete. See output folder.")

if __name__ == "__main__":
    main()
