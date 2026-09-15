import io
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, ttest_ind, mannwhitneyu
from openpyxl import load_workbook


def norm(v: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(v or "").lower()).strip()


def _header_map(ws):
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 12)):
        vals = [norm(c.value) for c in row]
        if any(x in vals for x in ("total", "case", "control", "p value", "pvalue")):
            return {norm(c.value): c.column for c in row if c.value is not None}
    return {}


def _candidate_column(df, variable, categories):
    target = norm(variable)
    best = (None, 0.0)
    for col in df.columns:
        cn = norm(col)
        score = 0.0
        if target and (target == cn):
            score = 1.0
        elif target and (target in cn or cn in target):
            score = 0.75
        s = df[col].dropna().astype(str).map(norm)
        if categories:
            hits = sum(1 for cat in categories if norm(cat) in set(s.unique()))
            score = max(score, min(0.95, hits / max(1, len(categories))))
        if score > best[1]:
            best = (col, score)
    return best


def _group_column(df):
    preferred = [c for c in df.columns if norm(c) in {"group", "arm", "study arm", "case control", "case control group", "intervention control"}]
    if preferred:
        return preferred[0]
    for c in df.columns:
        vals = set(df[c].dropna().astype(str).map(norm).unique())
        if {"case", "control"}.issubset(vals) or {"intervention", "control"}.issubset(vals):
            return c
    return None


def _format_p(p):
    if p is None or not np.isfinite(p):
        return ""
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def _test_p(x, group):
    z = pd.DataFrame({"x": x, "g": group}).dropna()
    if z.empty or z.g.nunique() != 2:
        return None, ""
    if not pd.api.types.is_numeric_dtype(z.x) or z.x.nunique() <= 10:
        tab = pd.crosstab(z.x, z.g)
        if tab.shape == (2, 2) and (tab.values < 5).any():
            return float(fisher_exact(tab.values)[1]), "Fisher exact"
        return float(chi2_contingency(tab, correction=False)[1]), "Pearson chi-square"
    groups = [z.loc[z.g == g, "x"] for g in z.g.unique()]
    if min(map(len, groups)) < 3:
        return None, ""
    p = ttest_ind(groups[0], groups[1], equal_var=False, nan_policy="omit").pvalue
    return float(p), "Welch t-test"


def fill_dummy_table(dataset_bytes_list, dataset_names, dummy_bytes, dummy_filename):
    frames = []
    for content, name in zip(dataset_bytes_list, dataset_names):
        ext = name.lower().rsplit(".", 1)[-1]
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(content))
        elif ext == "tsv":
            df = pd.read_csv(io.BytesIO(content), sep="\t")
        elif ext in ("xlsx", "xls"):
            df = pd.read_excel(io.BytesIO(content))
        elif ext == "dta":
            df = pd.read_stata(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported dataset type: {name}")
        df = df.copy()
        df["__source_dataset"] = name
        frames.append(df)
    if not frames:
        raise ValueError("At least one dataset is required")
    df = pd.concat(frames, ignore_index=True, sort=False)

    ext = dummy_filename.lower().rsplit(".", 1)[-1]
    if ext not in ("xlsx", "xls"):
        raise ValueError("Result filling currently requires an Excel dummy table (.xlsx/.xls)")
    wb = load_workbook(io.BytesIO(dummy_bytes))
    ws = wb[wb.sheetnames[0]]
    headers = _header_map(ws)
    group_col = _group_column(df)

    # Identify table rows from a common two-column layout: variable in col A, category in col B.
    filled = 0
    unmapped = []
    current_variable = None
    current_categories = []
    row_records = []

    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        b = ws.cell(r, 2).value if ws.max_column >= 2 else None
        if a is None and b is None:
            continue
        an, bn = norm(a), norm(b)
        if an in {"total", "case", "control", "p value", "pvalue", "overall"} or bn in {"total", "case", "control", "p value", "pvalue"}:
            continue
        # A non-empty first cell with a second cell is treated as variable/category when the second cell is specific.
        if a is not None and b is not None and an not in {"demographic factors", "clinical factors", "structural factors", "psychosocial factors"}:
            current_variable = str(a).strip()
            current_categories = [str(b).strip()]
            row_records.append((r, current_variable, str(b).strip()))
        elif a is not None and b is None:
            # Either a variable heading or a category in a one-column table.
            current_variable = str(a).strip()
            current_categories = []
            row_records.append((r, current_variable, None))
        elif b is not None and current_variable:
            current_categories.append(str(b).strip())
            row_records.append((r, current_variable, str(b).strip()))

    for r, variable, category in row_records:
        if not variable or not category:
            continue
        col, confidence = _candidate_column(df, variable, [category])
        if col is None or confidence < 0.50:
            # Try the variable as a category-aware match when labels differ from the dataset name.
            col, confidence = _candidate_column(df, "", [category])
        if col is None or confidence < 0.50:
            unmapped.append({"row": r, "variable": variable, "category": category})
            continue
        s = df[col]
        category_mask = s.astype(str).map(norm) == norm(category)
        denom = int(s.notna().sum())
        n_total = int(category_mask.sum())
        pct_total = 100 * n_total / denom if denom else None
        # Fill total if present.
        if "total" in headers:
            ws.cell(r, headers["total"]).value = f"{n_total} ({pct_total:.1f}%)" if pct_total is not None else ""
            filled += 1
        # Fill case/control when a group column is available.
        p = None
        if group_col:
            groups = [g for g in df[group_col].dropna().astype(str).unique()]
            for g in groups:
                gn = norm(g)
                key = "case" if gn == "case" else "control" if gn == "control" else "intervention" if gn == "intervention" else gn
                if key not in headers:
                    continue
                sub = df.loc[df[group_col].astype(str).map(norm) == gn, col]
                denom_g = int(sub.notna().sum())
                n_g = int((sub.astype(str).map(norm) == norm(category)).sum())
                pct_g = 100 * n_g / denom_g if denom_g else None
                ws.cell(r, headers[key]).value = f"{n_g} ({pct_g:.1f}%)" if pct_g is not None else ""
                filled += 1
            p, _ = _test_p(s, df[group_col])
        if "p value" in headers:
            ws.cell(r, headers["p value"]).value = _format_p(p)
            if p is not None:
                filled += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue(), {"rows_in_dataset": int(df.shape[0]), "columns_in_dataset": int(df.shape[1] - 1), "datasets": dataset_names, "group_variable": group_col, "filled_cells": filled, "unmapped_rows": unmapped[:100]}
