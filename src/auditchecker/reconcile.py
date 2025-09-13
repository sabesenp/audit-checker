from __future__ import annotations
import pandas as pd
from typing import List, Tuple

#input file reader supporting CSV and Excel formats
def _read(path: str) -> pd.DataFrame:
    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    elif lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, dtype=str).fillna("")
    else:
        raise ValueError(f"Unsupported file type: {path}")
    

#normalize specified columns by case folding and/or stripping whitespace
def _normalize(df: pd.DataFrame, cols: List[str], casefold: bool, strip: bool) -> pd.DataFrame:
    df = df.copy()
    for c in cols:
        if c in df.columns:
            s = df[c].astype(str)
            if strip:
                s = s.str.strip()
            if casefold:
                s = s.str.casefold()
            df[c] = s
    return df

def _dedupe(df: pd.DataFrame, keys: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    dup_mask = df.duplicated(subset=keys, keep=False)
    dups = df.loc[dup_mask].sort_values(keys)
    deduped = df.drop_duplicates(subset=keys, keep="first")
    return deduped, dups

def reconcile(path_a: str, path_b: str, keys: List[str], compare_cols: List[str] | None = None,
              casefold: bool = False, strip_ws: bool = True) -> dict:
    a = _read(path_a)
    b = _read(path_b)

    if compare_cols is None:
        compare_cols = [c for c in a.columns.intersection(b.columns) if c not in keys]

    norm_cols = list(set(keys + compare_cols))
    a = _normalize(a, norm_cols, casefold, strip_ws)
    b = _normalize(b, norm_cols, casefold, strip_ws)

    a_dedup, dups_a = _dedupe(a, keys)
    b_dedup, dups_b = _dedupe(b, keys)

    a_idx = a_dedup.set_index(keys, drop=False)
    b_idx = b_dedup.set_index(keys, drop=False)

    missing_in_b = a_idx.loc[~a_idx.index.isin(b_idx.index)].reset_index(drop=True)
    missing_in_a = b_idx.loc[~b_idx.index.isin(a_idx.index)].reset_index(drop=True)

    common = a_idx.join(b_idx[compare_cols], how="inner", rsuffix="_b")
    mismatch_mask = False
    for c in compare_cols:
        mismatch_mask = mismatch_mask | (common[c] != common[f"{c}_b"])
    mismatches = common.loc[mismatch_mask].reset_index(drop=True)

    summary = {
        "rows_a": int(len(a)),
        "rows_b": int(len(b)),
        "duplicates_a": int(len(dups_a)),
        "duplicates_b": int(len(dups_b)),
        "missing_in_b": int(len(missing_in_b)),
        "missing_in_a": int(len(missing_in_a)),
        "mismatches": int(len(mismatches)),
        "keys": keys,
        "compare_cols": compare_cols,
    }

    return {
        "missing_in_b": missing_in_b,
        "missing_in_a": missing_in_a,
        "mismatches": mismatches,
        "duplicates_a": dups_a,
        "duplicates_b": dups_b,
        "summary": summary,
    }
