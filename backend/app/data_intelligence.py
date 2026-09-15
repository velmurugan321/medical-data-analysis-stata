"""Conservative workbook-wide data profiling and variable type inference.

The engine never silently recodes data. It reports observed types, coding candidates,
quality signals and confidence so downstream statistical analysis can require confirmation
when a variable is ambiguous.
"""
import io
import re
from typing import Any
import numpy as np
import pandas as pd

ID_RE = re.compile(r"(^|_)(id|identifier|record|mrn|uhid|uid|patient|participant|serial|sl|code)(_|$)")
DATE_RE = re.compile(r"date|dob|birth|admission|discharge|visit", re.I)


def norm(x: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(x or "").lower()).strip()


def _numeric_conversion(s: pd.Series):
    raw = s.dropna().astype(str).str.strip()
    if raw.empty:
        return None, 0.0
    cleaned = raw.str.replace(",", "", regex=False).str.replace(r"%$", "", regex=True).str.strip()
    num = pd.to_numeric(cleaned, errors="coerce")
    return num, float(num.notna().mean())


def _value_family(s: pd.Series):
    vals = s.dropna()
    if vals.empty:
        return "empty"
    text = vals.astype(str).str.strip()
    numeric, numeric_rate = _numeric_conversion(vals)
    if numeric_rate >= 0.98:
        return "numeric"
    if text.str.match(r"^\d{1,4}[-/]\d{1,2}[-/]\d{1,4}$").mean() >= 0.8:
        return "date-like"
    if text.str.fullmatch(r"[A-Za-z]", na=False).mean() >= 0.8:
        return "short-code"
    return "text"


def _candidate_semantics(name: str, s: pd.Series):
    n = norm(name)
    vals = s.dropna().astype(str).str.strip()
    unique = set(vals.str.lower().unique())
    candidates = []
    if ID_RE.search(n) or (len(vals) and vals.nunique() / len(vals) > 0.98 and not pd.api.types.is_numeric_dtype(s)):
        candidates.append(("identifier", 0.96 if ID_RE.search(n) else 0.78))
    if DATE_RE.search(n):
        candidates.append(("date/time", 0.92))
    if unique and unique <= {"m", "f", "male", "female", "man", "woman"}:
        candidates.append(("binary categorical", 0.99))
    if unique and unique <= {"y", "n", "yes", "no", "true", "false"}:
        candidates.append(("binary categorical", 0.99))
    if unique and unique <= {"positive", "negative", "pos", "neg"}:
        candidates.append(("binary categorical", 0.99))
    if unique and len(unique) <= 10:
        candidates.append(("categorical/code", 0.88))
    return candidates


def profile_variable(df: pd.DataFrame, col: str):
    s = df[col]
    n = int(len(s)); nonmissing = int(s.notna().sum()); missing = n - nonmissing
    numeric, numeric_rate = _numeric_conversion(s)
    family = _value_family(s)
    semantics = _candidate_semantics(col, s)
    unique = int(s.nunique(dropna=True))
    examples = [str(x) for x in s.dropna().head(8).tolist()]
    warnings = []

    if numeric_rate >= 0.80 and numeric_rate < 0.98:
        warnings.append("Mixed numeric/text values; numeric conversion is incomplete")
    if family == "short-code" and unique > 10:
        warnings.append("Short letter codes detected; coding dictionary may be required")
    if family == "numeric" and unique <= 10:
        warnings.append("Numeric values may be category codes rather than continuous measurements")
    if unique == 0:
        detected, confidence = "empty", 1.0
    elif any(x[0] == "identifier" for x in semantics):
        detected, confidence = "identifier", max(x[1] for x in semantics if x[0] == "identifier")
    elif any(x[0] == "date/time" for x in semantics):
        detected, confidence = "date/time", max(x[1] for x in semantics if x[0] == "date/time")
    elif family == "numeric":
        detected, confidence = ("binary/code" if unique <= 10 else "numeric"), min(0.99, 0.90 + 0.09 * numeric_rate)
    elif family == "short-code":
        detected, confidence = "categorical/code", 0.86
    elif family == "date-like":
        detected, confidence = "date/time", 0.88
    else:
        detected, confidence = "categorical/text", min(0.95, 0.70 + 0.20 * (unique <= 30))

    if warnings:
        confidence = min(confidence, 0.75)
    recommended = {
        "numeric": "continuous/summary or regression predictor",
        "binary/code": "binary categorical after code confirmation",
        "categorical/code": "categorical analysis after code confirmation",
        "categorical/text": "categorical analysis",
        "identifier": "exclude from statistical modelling",
        "date/time": "date/time analysis or derive duration",
        "empty": "exclude until populated",
    }.get(detected, "manual review")

    return {
        "name": str(col), "detected_type": detected, "raw_dtype": str(s.dtype),
        "n": n, "nonmissing": nonmissing, "missing": missing,
        "missing_percent": round(100 * missing / n, 2) if n else 0,
        "unique": unique, "numeric_parse_percent": round(100 * numeric_rate, 2),
        "examples": examples, "min": float(numeric.min()) if numeric is not None and numeric.notna().any() else None,
        "max": float(numeric.max()) if numeric is not None and numeric.notna().any() else None,
        "confidence": round(float(confidence), 2), "confidence_percent": round(100 * float(confidence), 1),
        "recommended_analysis": recommended, "warnings": warnings,
        "coding_candidates": [x[0] for x in semantics],
    }


def read_excel_all(content: bytes):
    book = pd.ExcelFile(io.BytesIO(content))
    sheets = []
    for sheet in book.sheet_names:
        try:
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet)
            if df.shape[0] == 0 and df.shape[1] == 0:
                continue
            sheets.append((sheet, df))
        except Exception as exc:
            sheets.append((sheet, None, str(exc)))
    return sheets


def profile_workbook(content: bytes, filename: str):
    sheets = read_excel_all(content)
    result = []
    all_profiles = []
    for item in sheets:
        sheet, df = item[0], item[1]
        if df is None:
            result.append({"sheet": sheet, "status": "error", "error": item[2]})
            continue
        profiles = [profile_variable(df, c) for c in df.columns]
        all_profiles.extend([{**p, "sheet": sheet} for p in profiles])
        result.append({"sheet": sheet, "status": "read", "rows": int(df.shape[0]), "columns": int(df.shape[1]), "variables": profiles})
    return {"filename": filename, "sheet_count": len(result), "sheets": result, "variables": all_profiles}


def profile_multiple_workbooks(files):
    workbooks = [profile_workbook(content, name) for name, content in files]
    return {"file_count": len(workbooks), "files": workbooks}
