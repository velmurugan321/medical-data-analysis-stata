import json
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm


def _require_columns(df, columns):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing variables: {', '.join(missing)}")


def _clean_list(value):
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return list(value or [])


def descriptive(df, variables):
    variables = _clean_list(variables)
    _require_columns(df, variables)
    result = []
    for col in variables:
        s = df[col].dropna()
        if pd.api.types.is_numeric_dtype(s):
            result.append({
                "variable": col, "type": "continuous", "n": int(s.size),
                "mean": float(s.mean()), "sd": float(s.std(ddof=1)),
                "median": float(s.median()), "q1": float(s.quantile(.25)),
                "q3": float(s.quantile(.75)), "min": float(s.min()), "max": float(s.max())
            })
        else:
            counts = s.value_counts(dropna=False)
            result.append({"variable": col, "type": "categorical", "n": int(s.size),
                           "levels": [{"level": str(k), "n": int(v),
                                       "percent": float(v / s.size * 100)}
                                      for k, v in counts.items()]})
    return result


def categorical_association(df, variable, outcome):
    _require_columns(df, [variable, outcome])
    x = df[[variable, outcome]].dropna()
    table = pd.crosstab(x[variable], x[outcome])
    if table.shape[0] < 2 or table.shape[1] < 2:
        raise ValueError("Both variables must have at least two observed categories")
    chi2, p, dof, expected = stats.chi2_contingency(table, correction=False)
    fisher = None
    if table.shape == (2, 2):
        _, fisher = stats.fisher_exact(table.to_numpy())
    return {"table": table.to_dict(), "chi_square": float(chi2),
            "df": int(dof), "p_value": float(p), "fisher_p": fisher,
            "expected_min": float(expected.min())}


def diagnostic_accuracy(df, index_test, reference_standard):
    _require_columns(df, [index_test, reference_standard])
    x = df[[index_test, reference_standard]].dropna()
    if not x[index_test].isin([0, 1]).all() or not x[reference_standard].isin([0, 1]).all():
        raise ValueError("Diagnostic variables must be coded 0/1")
    tp = int(((x[index_test] == 1) & (x[reference_standard] == 1)).sum())
    tn = int(((x[index_test] == 0) & (x[reference_standard] == 0)).sum())
    fp = int(((x[index_test] == 1) & (x[reference_standard] == 0)).sum())
    fn = int(((x[index_test] == 0) & (x[reference_standard] == 1)).sum())
    sens = tp / (tp + fn) if tp + fn else np.nan
    spec = tn / (tn + fp) if tn + fp else np.nan
    ppv = tp / (tp + fp) if tp + fp else np.nan
    npv = tn / (tn + fn) if tn + fn else np.nan
    acc = (tp + tn) / len(x) if len(x) else np.nan
    plr = sens / (1 - spec) if np.isfinite(spec) and spec < 1 else np.inf
    nlr = (1 - sens) / spec if np.isfinite(spec) and spec > 0 else np.nan
    return {"n": len(x), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "sensitivity": sens, "specificity": spec, "ppv": ppv,
            "npv": npv, "accuracy": acc, "plr": plr, "nlr": nlr}


def roc_auc(df, test, outcome):
    _require_columns(df, [test, outcome])
    x = df[[test, outcome]].dropna()
    if x[outcome].nunique() != 2:
        raise ValueError("ROC outcome must contain exactly two observed classes")
    from sklearn.metrics import roc_auc_score, roc_curve
    auc = float(roc_auc_score(x[outcome], x[test]))
    fpr, tpr, thresholds = roc_curve(x[outcome], x[test])
    return {"n": len(x), "auc": auc,
            "fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": thresholds.tolist()}


def _parse_reference_categories(reference_categories):
    if not reference_categories:
        return {}
    if isinstance(reference_categories, str):
        try:
            return json.loads(reference_categories)
        except json.JSONDecodeError as exc:
            raise ValueError("reference_categories must be valid JSON") from exc
    return dict(reference_categories)


def _encode_predictors(df, predictors, categorical_predictors, reference_categories):
    categorical_predictors = set(_clean_list(categorical_predictors))
    for col in categorical_predictors:
        if col not in predictors:
            raise ValueError(f"Categorical predictor '{col}' is not in predictors")
    work = df[predictors].copy()
    pieces = []
    metadata = []
    for col in predictors:
        s = work[col]
        if col in categorical_predictors:
            levels = sorted(s.dropna().astype(str).unique().tolist())
            if len(levels) < 2:
                raise ValueError(f"Categorical predictor '{col}' must have at least two observed levels")
            requested = reference_categories.get(col)
            if requested is not None:
                requested = str(requested)
                if requested not in levels:
                    raise ValueError(f"Reference category '{requested}' not observed for '{col}'")
            else:
                requested = levels[0]
            cat = s.astype("string")
            dummies = pd.get_dummies(cat, prefix=col, dtype=float)
            ref_name = f"{col}_{requested}"
            if ref_name not in dummies.columns:
                raise ValueError(f"Unable to construct reference category for '{col}'")
            dummies = dummies.drop(columns=[ref_name])
            pieces.append(dummies)
            for dummy in dummies.columns:
                level = dummy[len(col) + 1:]
                metadata.append({"term": dummy, "variable": col, "level": level,
                                 "reference": requested})
        else:
            numeric = pd.to_numeric(s, errors="coerce")
            pieces.append(numeric.to_frame(name=col))
            metadata.append({"term": col, "variable": col, "level": None, "reference": None})
    encoded = pd.concat(pieces, axis=1)
    return encoded, metadata


def _poisson_model(df, outcome, predictors, categorical_predictors, reference_categories):
    _require_columns(df, [outcome] + predictors)
    if not set(df[outcome].dropna().unique()).issubset({0, 1}):
        raise ValueError("Outcome must be coded 0/1 for robust Poisson risk-ratio analysis")
    encoded, metadata = _encode_predictors(df, predictors, categorical_predictors, reference_categories)
    work = pd.concat([df[[outcome]], encoded], axis=1).dropna()
    if len(work) == 0:
        raise ValueError("No complete observations remain for this model")
    y = work[outcome].astype(float)
    X = sm.add_constant(work.drop(columns=[outcome]).astype(float), has_constant="add")
    if X.shape[1] <= 1:
        raise ValueError("At least one predictor is required")
    model = sm.GLM(y, X, family=sm.families.Poisson()).fit(cov_type="HC1")
    params = model.params
    conf = model.conf_int()
    rows = []
    by_term = {m["term"]: m for m in metadata}
    for term in params.index:
        if term == "const":
            continue
        m = by_term[term]
        beta = float(params[term])
        rows.append({"term": term, "variable": m["variable"], "level": m["level"],
                     "reference": m["reference"], "rr": float(np.exp(beta)),
                     "lower_ci": float(np.exp(conf.loc[term, 0])),
                     "upper_ci": float(np.exp(conf.loc[term, 1])),
                     "p_value": float(model.pvalues[term])})
    return {"n": int(len(work)), "rows": rows, "converged": bool(model.converged)}


def robust_poisson(df, outcome, predictors, categorical_predictors=None, reference_categories=None):
    predictors = _clean_list(predictors)
    if not predictors:
        raise ValueError("At least one predictor is required")
    categorical_predictors = _clean_list(categorical_predictors)
    references = _parse_reference_categories(reference_categories)
    crude = []
    warnings = []
    for predictor in predictors:
        try:
            result = _poisson_model(df, outcome, [predictor],
                                    [predictor] if predictor in categorical_predictors else [], references)
            crude.extend(result["rows"])
        except (ValueError, np.linalg.LinAlgError) as exc:
            warnings.append(f"Crude model for {predictor}: {exc}")
    adjusted = _poisson_model(df, outcome, predictors, categorical_predictors, references)
    return {"method": "Poisson regression with HC1 robust covariance", "outcome": outcome,
            "crude": crude, "adjusted": adjusted["rows"], "n": adjusted["n"],
            "converged": adjusted["converged"], "warnings": warnings,
            "note": "RR is exp(beta). Categorical predictors use the explicitly supplied reference category; otherwise the first observed level is used."}


def table_one(df, variables, group=None):
    variables = _clean_list(variables)
    _require_columns(df, variables + ([group] if group else []))
    output = []
    for col in variables:
        s = df[col]
        continuous = pd.api.types.is_numeric_dtype(s)
        item = {"variable": col, "type": "continuous" if continuous else "categorical", "overall": descriptive(df, [col])[0]}
        if group:
            item["groups"] = []
            for level, g in df.groupby(group, dropna=False):
                item["groups"].append({"group": str(level), "summary": descriptive(g, [col])[0]})
            item["p_value"] = None
            item["test"] = "descriptive by group; inferential test available in next table-one validation layer"
        output.append(item)
    return output


def data_quality(df):
    rows = []
    duplicate_rows = int(df.duplicated().sum())
    for col in df.columns:
        s = df[col]
        missing = int(s.isna().sum())
        unique = int(s.nunique(dropna=True))
        issues = []
        if missing:
            issues.append("missing")
        if unique <= 1:
            issues.append("constant_or_empty")
        if unique > max(50, int(len(df) * 0.5)):
            issues.append("high_cardinality")
        rows.append({"variable": str(col), "dtype": str(s.dtype), "n": int(len(s)),
                     "missing": missing, "missing_percent": float(missing / len(df) * 100) if len(df) else 0,
                     "unique": unique, "issues": issues})
    return {"rows": int(len(df)), "columns": int(len(df.columns)),
            "duplicate_rows": duplicate_rows, "variables": rows}
