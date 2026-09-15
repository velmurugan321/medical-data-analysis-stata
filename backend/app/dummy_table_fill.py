import io
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, ttest_ind
from openpyxl import load_workbook


SECTION_NAMES = {
    "demographic factors",
    "clinical factors",
    "structural factors",
    "psychosocial factors",
}
VARIABLE_ALIASES = {
    "gender": ["sex", "gender"],
    "age": ["age", "age years", "age in years"],
    "monthly income": ["monthly income", "income", "monthly household income"],
    "occupation": ["occupation", "job", "employment"],
    "phase of therapy": ["phase of therapy", "therapy phase", "treatment phase"],
    "category of tb": ["category of tb", "tb category", "category", "previous treatment", "previously treated"],
    "type of tb": ["type of tb", "tb type", "disease type"],
    "transport mode to clinic": ["transport mode to clinic", "transport mode", "mode of transport", "transport"],
    "money spent to collect medication refills": ["money spent to collect medication refills", "money spent", "cost of refill", "refill cost"],
    "time spent to collect medication refills": ["time spent to collect medication refills", "time spent", "refill time", "time to collect medication"],
    "current tobacco use": ["current tobacco use", "tobacco use", "smoking", "tobacco"],
    "probable alcohol use": ["probable alcohol use", "alcohol use", "alcohol"],
}


def norm(v: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(v or "").lower()).strip()


def _header_map(ws):
    for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 15)):
        vals = [norm(c.value) for c in row]
        if any(x in vals for x in ("total", "case", "control", "p value", "pvalue", "dindigul")):
            return {norm(c.value): c.column for c in row if c.value is not None}
    return {}


def _canonical_variable(label):
    n = norm(label)
    if n in VARIABLE_ALIASES:
        return n
    for canonical, aliases in VARIABLE_ALIASES.items():
        if n == canonical or any(n == norm(a) for a in aliases):
            return canonical
    for canonical, aliases in VARIABLE_ALIASES.items():
        if any(norm(a) in n or n in norm(a) for a in aliases if norm(a)):
            return canonical
    return n


def _find_dataset_column(df, variable, categories):
    canonical = _canonical_variable(variable)
    aliases = VARIABLE_ALIASES.get(canonical, [variable])
    best = (None, 0.0)
    for col in df.columns:
        if str(col).startswith("__"):
            continue
        cn = norm(col)
        score = 0.0
        if cn == norm(variable) or cn == canonical:
            score = 1.0
        elif any(norm(a) == cn for a in aliases):
            score = 0.98
        elif any(norm(a) in cn or cn in norm(a) for a in aliases if norm(a)):
            score = 0.82
        if categories:
            vals = set(df[col].dropna().astype(str).map(norm).unique())
            hits = 0
            for cat in categories:
                cnorm = norm(cat)
                if cnorm in vals:
                    hits += 1
                    continue
                # Numeric/range categories are handled below by category rules.
                if any(cnorm == v or cnorm in v or v in cnorm for v in vals):
                    hits += 1
            if hits:
                score = max(score, min(0.94, 0.55 + 0.35 * hits / len(categories)))
        if score > best[1]:
            best = (col, score)
    return best


def _group_column(df):
    preferred = [c for c in df.columns if norm(c) in {
        "group", "arm", "study arm", "case control", "case control group", "intervention control", "treatment arm"
    }]
    if preferred:
        return preferred[0]
    for c in df.columns:
        vals = set(df[c].dropna().astype(str).map(norm).unique())
        if {"case", "control"}.issubset(vals) or {"intervention", "control"}.issubset(vals):
            return c
    return None


def _site_arm_from_filename(name):
    n = norm(name)
    site = None
    for candidate in ("dindigul", "perambalur", "theni", "tiruvallur"):
        if candidate in n:
            site = candidate
            break
    arm = None
    if "intervention" in n:
        arm = "intervention"
    elif "control" in n:
        arm = "control"
    return site, arm


def _format_p(p):
    if p is None or not np.isfinite(p):
        return ""
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def _category_mask(series, category, variable):
    raw = series
    s = raw.astype(str).map(norm)
    c = norm(category)
    numeric = pd.to_numeric(raw, errors="coerce")

    # Age bands
    if _canonical_variable(variable) == "age":
        if re.search(r"18\s*29", c):
            return numeric.between(18, 29, inclusive="both")
        if re.search(r"30\s*44", c):
            return numeric.between(30, 44, inclusive="both")
        if "45" in c:
            return numeric >= 45

    # Income bands
    if _canonical_variable(variable) == "monthly income":
        if "<7500" in c or "7500" in c and "14" not in c:
            return numeric < 7500
        if "7500" in c and "14" in c:
            return numeric.between(7500, 14999, inclusive="both")
        if "15000" in c:
            return numeric >= 15000

    # Money spent bands
    if _canonical_variable(variable) == "money spent to collect medication refills":
        if "0 24" in c:
            return numeric.between(0, 24, inclusive="both")
        if "25 49" in c:
            return numeric.between(25, 49, inclusive="both")
        if "50 75" in c:
            return numeric.between(50, 75, inclusive="both")
        if ">75" in c:
            return numeric > 75

    # Time bands
    if _canonical_variable(variable) == "time spent to collect medication refills":
        if "30 minutes" in c and "60" not in c:
            return numeric < 30
        if "30 to 59" in c:
            return numeric.between(30, 59, inclusive="both")
        if "60 to 239" in c:
            return numeric.between(60, 239, inclusive="both")
        if "240" in c:
            return numeric >= 240

    # Direct categorical match, plus tolerant text matching.
    exact = s == c
    if exact.any():
        return exact
    return s.str.contains(re.escape(c), regex=True, na=False) | s.map(lambda v: v in c if v else False)


def _test_p(series, group):
    z = pd.DataFrame({"x": series, "g": group}).dropna()
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
    return float(ttest_ind(groups[0], groups[1], equal_var=False, nan_policy="omit").pvalue), "Welch t-test"


def _parse_table_rows(ws):
    # The supplied Table 1 is commonly formatted with merged cells, so the
    # variable and category may both appear in column A rather than A/B.
    rows = []
    current_variable = None
    variable_keys = {_canonical_variable(x) for x in VARIABLE_ALIASES}
    for r in range(1, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, min(ws.max_column, 4) + 1)]
        texts = [str(v).strip() for v in vals if v is not None and str(v).strip()]
        if not texts:
            continue
        candidates = [t for t in texts if norm(t) not in {"total", "case", "control", "p value", "pvalue", "overall"}]
        if not candidates:
            continue
        first = candidates[0]
        first_norm = norm(first)
        canonical = _canonical_variable(first)
        if first_norm in SECTION_NAMES:
            continue
        if canonical in variable_keys and first_norm != "gender":
            current_variable = first
            continue
        if first_norm == "gender":
            current_variable = first
            continue
        if current_variable:
            rows.append((r, current_variable, first))
    return rows


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
        site, arm = _site_arm_from_filename(name)
        df["__source_dataset"] = name
        df["__source_site"] = site or ""
        df["__source_arm"] = arm or ""
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
    table_rows = _parse_table_rows(ws)
    filled = 0
    unmapped = []

    for r, variable, category in table_rows:
        col, confidence = _find_dataset_column(df, variable, [category])
        if col is None or confidence < 0.50:
            unmapped.append({"row": r, "variable": variable, "category": category, "reason": "dataset variable not confidently mapped"})
            continue
        mask = _category_mask(df[col], category, variable)
        denom = int(df[col].notna().sum())
        n_total = int(mask.sum())
        pct_total = 100 * n_total / denom if denom else None
        if "total" in headers:
            ws.cell(r, headers["total"]).value = f"{n_total} ({pct_total:.1f}%)" if pct_total is not None else ""
            filled += 1

        # Case/control are filled only when the uploaded data actually contain
        # an explicit Case/Control grouping variable; otherwise they stay blank.
        p = None
        if group_col:
            p, _ = _test_p(df[col], df[group_col])
            for g in ["case", "control"]:
                if g not in headers:
                    continue
                gm = df[group_col].astype(str).map(norm) == g
                sub_mask = mask & gm
                denom_g = int((df[col].notna() & gm).sum())
                n_g = int(sub_mask.sum())
                pct_g = 100 * n_g / denom_g if denom_g else None
                ws.cell(r, headers[g]).value = f"{n_g} ({pct_g:.1f}%)" if pct_g is not None else ""
                filled += 1
        if "p value" in headers:
            ws.cell(r, headers["p value"]).value = _format_p(p)
            if p is not None:
                filled += 1

        # Site/arm columns are derived from uploaded filenames. Only columns
        # for sites actually represented by the uploaded datasets are filled.
        for site in ("dindigul", "perambalur", "theni", "tiruvallur"):
            for arm in ("control", "intervention"):
                key = f"{site} {arm}"
                if key not in headers:
                    continue
                sm = df["__source_site"].map(norm) == site
                am = df["__source_arm"].map(norm) == arm
                gm = sm & am
                denom_sa = int((df[col].notna() & gm).sum())
                n_sa = int((mask & gm).sum())
                pct_sa = 100 * n_sa / denom_sa if denom_sa else None
                ws.cell(r, headers[key]).value = f"{n_sa} ({pct_sa:.1f}%)" if pct_sa is not None else ""
                if denom_sa:
                    filled += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue(), {
        "rows_in_dataset": int(df.shape[0]),
        "columns_in_dataset": int(len([c for c in df.columns if not str(c).startswith("__")])),
        "datasets": dataset_names,
        "group_variable": group_col,
        "filled_cells": filled,
        "parsed_table_rows": len(table_rows),
        "unmapped_rows": unmapped[:100],
        "site_arm_sources": [{"dataset": n, "site": _site_arm_from_filename(n)[0], "arm": _site_arm_from_filename(n)[1]} for n in dataset_names],
    }
