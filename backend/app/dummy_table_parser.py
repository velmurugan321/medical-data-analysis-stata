import io, re
from typing import Any
import pandas as pd


def norm(value: Any) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').lower()).strip()


def best_column(columns, label):
    target = norm(label)
    if not target:
        return None, 0
    exact = {norm(c): c for c in columns}
    if target in exact:
        return exact[target], 1.0
    tokens = set(target.split())
    best, score = None, 0
    for c in columns:
        ct = set(norm(c).split())
        if not ct:
            continue
        overlap = len(tokens & ct) / max(1, len(tokens))
        if overlap > score:
            best, score = c, overlap
    return (best, round(score, 2)) if score >= 0.5 else (None, round(score, 2))


def read_dummy(content: bytes, filename: str):
    ext = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''
    if ext in ('xlsx', 'xls'):
        book = pd.ExcelFile(io.BytesIO(content))
        sheets = book.sheet_names
        frames = {s: pd.read_excel(io.BytesIO(content), sheet_name=s, header=None) for s in sheets}
    elif ext == 'csv':
        sheets = ['CSV']
        frames = {'CSV': pd.read_csv(io.BytesIO(content), header=None)}
    elif ext == 'tsv':
        sheets = ['TSV']
        frames = {'TSV': pd.read_csv(io.BytesIO(content), sep='\t', header=None)}
    elif ext == 'json':
        sheets = ['JSON']
        frames = {'JSON': pd.DataFrame(pd.read_json(io.BytesIO(content)))}
    else:
        sheets = ['TEXT']
        frames = {'TEXT': pd.read_csv(io.BytesIO(content), sep='\t', header=None)}
    return sheets, frames


def build_spec(dataset: pd.DataFrame, dummy_content: bytes, dummy_filename: str):
    sheets, frames = read_dummy(dummy_content, dummy_filename)
    rows_spec = []
    columns = [str(c) for c in dataset.columns]
    for sheet, frame in frames.items():
        # Look at the first non-empty column as the row-label column.
        for idx, row in frame.iterrows():
            vals = [x for x in row.tolist() if pd.notna(x) and str(x).strip()]
            if not vals:
                continue
            label = str(vals[0]).strip()
            if len(label) < 2 or norm(label) in {'total', 'case', 'control', 'p value', 'pvalue'}:
                continue
            variable, confidence = best_column(columns, label)
            rows_spec.append({
                'sheet': sheet,
                'row_index': int(idx),
                'label': label,
                'variable': variable,
                'confidence': confidence,
                'analysis': 'categorical n (%) + group comparison' if variable else 'needs variable mapping'
            })
    # Deduplicate repeated labels while preserving first occurrence.
    seen=set(); unique=[]
    for r in rows_spec:
        key=(r['sheet'], r['label'])
        if key not in seen:
            seen.add(key); unique.append(r)
    return {'sheets': sheets, 'rows_spec': unique[:300]}
