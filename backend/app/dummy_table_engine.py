import re
from typing import Any
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, ttest_ind, mannwhitneyu


def _norm(x: Any) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(x).strip().lower()).strip()


def _find_column(df: pd.DataFrame, label: str):
    target = _norm(label)
    cols = {_norm(c): c for c in df.columns}
    if target in cols:
        return cols[target], 1.0
    for key, col in cols.items():
        if target and (target in key or key in target):
            return col, 0.85
    return None, 0.0


def infer_test(series: pd.Series, group: pd.Series):
    x = pd.DataFrame({'x': series, 'g': group}).dropna()
    if x.empty or x['g'].nunique() != 2:
        return {'test': 'not_available', 'p_value': None}
    if not pd.api.types.is_numeric_dtype(x['x']) or x['x'].nunique() <= 5:
        tab = pd.crosstab(x['x'], x['g'])
        if tab.shape == (2, 2) and (tab.values < 5).any():
            _, p = fisher_exact(tab.values)
            return {'test': 'Fisher exact', 'p_value': float(p)}
        _, p, _, _ = chi2_contingency(tab)
        return {'test': 'Pearson chi-square', 'p_value': float(p)}
    groups = [x.loc[x.g == level, 'x'] for level in x.g.unique()]
    if min(len(g) for g in groups) < 3:
        return {'test': 'not_available', 'p_value': None}
    _, p = ttest_ind(groups[0], groups[1], equal_var=False, nan_policy='omit')
    return {'test': 'Welch t-test', 'p_value': float(p)}


def analyse_dummy_table(df: pd.DataFrame, specification: dict):
    group_label = specification.get('group_variable', 'group')
    group, confidence = _find_column(df, group_label)
    if group is None:
        raise ValueError(f'Could not identify grouping variable: {group_label}')
    result = {'group_variable': group, 'mapping_confidence': confidence, 'rows': []}
    for item in specification.get('rows', []):
        label = item.get('label', '')
        col, score = _find_column(df, item.get('variable', label))
        row = {'label': label, 'variable': col, 'mapping_confidence': score, 'cells': [], 'statistics': {}}
        if col is None:
            row['status'] = 'unmapped'
            result['rows'].append(row)
            continue
        s = df[col]
        levels = item.get('categories') or [v for v in s.dropna().unique()]
        for level in levels:
            counts = {}
            for g in df[group].dropna().unique():
                sub = df.loc[df[group] == g, col]
                n = int((sub.astype(str).str.strip() == str(level).strip()).sum())
                denom = int(sub.notna().sum())
                counts[str(g)] = {'n': n, 'percent': round(100*n/denom, 2) if denom else None}
            row['cells'].append({'category': level, 'by_group': counts})
        row['statistics'] = infer_test(s, df[group])
        row['status'] = 'mapped'
        result['rows'].append(row)
    return result
