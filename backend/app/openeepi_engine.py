from math import log, exp, sqrt, isfinite
from scipy.stats import beta


def _ci(successes: int, total: int, alpha: float = 0.05):
    if total <= 0:
        return [None, None]
    lo = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, total - successes + 1))
    hi = 1.0 if successes == total else float(beta.ppf(1 - alpha / 2, successes + 1, total - successes))
    return [lo, hi]


def _ratio_ci(num_a, den_a, num_b, den_b, alpha=0.05):
    if min(num_a, den_a, num_b, den_b) <= 0:
        return [None, None]
    ratio = (num_a / den_a) / (num_b / den_b)
    se = sqrt(1 / num_a - 1 / den_a + 1 / num_b - 1 / den_b)
    z = 1.959963984540054
    return [exp(log(ratio) - z * se), exp(log(ratio) + z * se)]


def screening(a, b, c, d):
    # Standard 2x2 diagnostic table:
    #              Reference +   Reference -
    # Test +          TP             FP
    # Test -          FN             TN
    vals = [a, b, c, d]
    if any((not isinstance(v, (int, float)) or not isfinite(v) or v < 0) for v in vals):
        raise ValueError("All cell counts must be non-negative finite numbers")
    if any(float(v) != int(v) for v in vals):
        raise ValueError("Cell counts must be whole numbers")
    tp, fp, fn, tn = map(int, vals)
    total = tp + fp + fn + tn
    if total == 0:
        raise ValueError("At least one observation is required")

    def div(x, y):
        return x / y if y else None

    sens = div(tp, tp + fn)
    spec = div(tn, tn + fp)
    ppv = div(tp, tp + fp)
    npv = div(tn, tn + fn)
    acc = (tp + tn) / total
    plr = (sens / (1 - spec)) if sens is not None and spec is not None and spec < 1 else None
    nlr = ((1 - sens) / spec) if sens is not None and spec not in (None, 0) else None
    dor = (plr / nlr) if plr not in (None, 0) and nlr not in (None, 0) else None
    youden = (sens + spec - 1) if sens is not None and spec is not None else None
    f1 = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else None

    return {
        "table": {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "total": total},
        "sensitivity": sens, "sensitivity_95ci": _ci(tp, tp + fn),
        "specificity": spec, "specificity_95ci": _ci(tn, tn + fp),
        "ppv": ppv, "ppv_95ci": _ci(tp, tp + fp),
        "npv": npv, "npv_95ci": _ci(tn, tn + fn),
        "accuracy": acc, "accuracy_95ci": _ci(tp + tn, total),
        "positive_likelihood_ratio": plr,
        "negative_likelihood_ratio": nlr,
        "diagnostic_odds_ratio": dor,
        "youden_j": youden,
        "f1_score": f1,
        "prevalence": div(tp + fn, total),
        "method": "2x2 diagnostic/screening table; exact Clopper-Pearson 95% CI for proportions",
        "interpretation": "Positive test is defined as TP/FP and disease/reference-positive as TP/FN."
    }
