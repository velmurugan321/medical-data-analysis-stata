"""Risk-ratio analysis for binary outcomes used by dummy-table templates.

Crude RR is calculated directly from 2x2 risks. Adjusted RR uses Poisson
regression with robust variance, which is appropriate for binary outcomes when
an RR (rather than an odds ratio) is required. Results are returned in a
machine-readable form for the web application.
"""

from __future__ import annotations

import math
import re
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact
import statsmodels.api as sm
import statsmodels.formula.api as smf


def _norm(x: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(x or "").lower()).strip()


def _find(df: pd.DataFrame, names: list[str]):
    normed = {_norm(c): c for c in df.columns}
    for name in names:
        if _norm(name) in normed:
            return normed[_norm(name)]
    for c in df.columns:
        cn = _norm(c)
        if any(_norm(n) in cn or cn in _norm(n) for n in names):
            return c
    return None


def _binary(series: pd.Series, positive: list[str]) -> pd.Series:
    p = {_norm(x) for x in positive}
    return series.map(lambda x: 1 if _norm(x) in p else (0 if pd.notna(x) else np.nan))


def crude_rr(outcome: pd.Series, exposure: pd.Series):
    z = pd.DataFrame({"y": outcome, "e": exposure}).dropna()
    if z.empty or z.e.nunique() != 2:
        return None
    levels = sorted(z.e.unique())
    ref, exposed = levels[0], levels[1]
    a = int(((z.y == 1) & (z.e == exposed)).sum())
    b = int(((z.y == 0) & (z.e == exposed)).sum())
    c = int(((z.y == 1) & (z.e == ref)).sum())
    d = int(((z.y == 0) & (z.e == ref)).sum())
    # Haldane-Anscombe correction only when a cell is zero.
    aa, bb, cc, dd = [v + 0.5 if v == 0 else v for v in (a, b, c, d)]
    risk_e = aa / (aa + bb)
    risk_r = cc / (cc + dd)
    rr = risk_e / risk_r
    se = math.sqrt(1 / aa - 1 / (aa + bb) + 1 / cc - 1 / (cc + dd))
    lo, hi = math.exp(math.log(rr) - 1.96 * se), math.exp(math.log(rr) + 1.96 * se)
    tab = np.array([[a, b], [c, d]])
    p = fisher_exact(tab)[1] if (tab < 5).any() else chi2_contingency(tab, correction=False)[1]
    return {"rr": float(rr), "ci_low": float(lo), "ci_high": float(hi), "p_value": float(p),
            "exposed_level": exposed, "reference_level": ref}


def adjusted_rr(df: pd.DataFrame, outcome_col: str, exposure_col: str,
                 covariates: list[str], reference: Any | None = None):
    cols = [outcome_col, exposure_col] + [c for c in covariates if c in df.columns]
    z = df[cols].dropna().copy()
    if z.empty or z[outcome_col].nunique() != 2 or z[exposure_col].nunique() != 2:
        return None
    levels = list(z[exposure_col].drop_duplicates())
    ref = reference if reference in levels else levels[0]
    exp = next(x for x in levels if x != ref)
    z["_y"] = pd.to_numeric(z[outcome_col], errors="coerce")
    z["_e"] = (z[exposure_col] == exp).astype(int)
    terms = ["_e"]
    for c in covariates:
        if c in z.columns:
            if pd.api.types.is_numeric_dtype(z[c]) and z[c].nunique() > 5:
                z[f"_c_{len(terms)}"] = pd.to_numeric(z[c], errors="coerce")
                terms.append(f"_c_{len(terms)}")
            else:
                z[c] = z[c].astype("category")
                terms.append(f"C(Q('{c}'))")
    formula = "_y ~ " + " + ".join(terms)
    try:
        fit = smf.glm(formula, data=z, family=sm.families.Poisson()).fit(cov_type="HC0")
        beta = float(fit.params["_e"])
        se = float(fit.bse["_e"])
        return {"rr": float(math.exp(beta)),
                "ci_low": float(math.exp(beta - 1.96 * se)),
                "ci_high": float(math.exp(beta + 1.96 * se)),
                "p_value": float(fit.pvalues["_e"]),
                "reference_level": ref, "exposed_level": exp,
                "n": int(len(z)), "method": "Poisson regression with robust variance"}
    except Exception as exc:
        return {"error": str(exc), "method": "Poisson regression with robust variance"}


def format_rr(x):
    if not x or x.get("error"):
        return ""
    return f"{x['rr']:.2f} ({x['ci_low']:.2f}–{x['ci_high']:.2f})"
