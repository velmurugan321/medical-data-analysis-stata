import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm


def _require_columns(df, columns):
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing variables: {', '.join(missing)}")


def descriptive(df, variables):
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
            result.append({"variable": col, "type": "categorical",
                           "n": int(s.size),
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
    auc = float(__import__('sklearn').metrics.roc_auc_score(x[outcome], x[test]))
    fpr, tpr, thresholds = __import__('sklearn').metrics.roc_curve(x[outcome], x[test])
    return {"n": len(x), "auc": auc,
            "fpr": fpr.tolist(), "tpr": tpr.tolist(), "thresholds": thresholds.tolist()}
