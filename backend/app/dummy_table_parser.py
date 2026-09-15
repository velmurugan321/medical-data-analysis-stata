import io, re
from typing import Any
import pandas as pd
from docx import Document

ALIASES = {
    'gender': ['sex','gender'],
    'age': ['age','age years','age in years','age group'],
    'monthly income': ['monthly income','income','monthly household income'],
    'occupation': ['occupation','job','employment'],
    'phase of therapy': ['phase of therapy','therapy phase','treatment phase'],
    'category of tb': ['category of tb','tb category','previous treatment','previously treated'],
    'type of tb': ['type of tb','tb type','disease type'],
    'transport mode to clinic': ['transport mode to clinic','transport mode','mode of transport','transport'],
    'money spent to collect medication refills': ['money spent to collect medication refills','money spent to collect refills','money spent','refill cost'],
    'time spent to collect medication refills': ['time spent to collect medication refills','time spent to collect refills','time spent','refill time'],
    'current tobacco use': ['current tobacco use','tobacco use','smoking','tobacco'],
    'probable alcohol use': ['probable alcohol use','alcohol use','alcohol'],
}
OUTCOME_WORDS = ['outcome','adherence','urine','result','status','event','unfavourable','unfavorable','positive','negative']


def norm(value: Any) -> str:
    return re.sub(r'[^a-z0-9]+', ' ', str(value or '').lower()).strip()


def tokens(value):
    return set(norm(value).split())


def best_column(columns, label, categories=None):
    target = norm(label)
    if not target:
        return None, 0, 'empty label'
    canonical = next((k for k,v in ALIASES.items() if target == k or target in {norm(x) for x in v}), target)
    aliases = ALIASES.get(canonical, [label])
    best = (None, 0.0, 'no match')
    category_tokens = [tokens(x) for x in (categories or []) if norm(x)]
    for c in columns:
        cn = norm(c)
        if not cn or cn.startswith('__'):
            continue
        score, reason = 0.0, 'token similarity'
        if cn == target or cn == canonical:
            score, reason = 1.0, 'exact name'
        elif any(cn == norm(a) for a in aliases):
            score, reason = 0.98, 'known alias'
        else:
            a = max((len(tokens(a)) for a in aliases), default=1)
            overlap = len(tokens(cn) & set().union(*(tokens(a) for a in aliases))) / max(1, len(tokens(cn)))
            direct = len(tokens(cn) & tokens(target)) / max(1, len(tokens(target)))
            score = max(overlap * 0.78, direct * 0.86)
        if category_tokens:
            # Category labels provide useful evidence even when the dataset
            # uses a different variable name (e.g. "sex" for "gender").
            sample = set(norm(x) for x in columns)
            # Actual value matching is performed by build_spec, where df is available.
        if score > best[1]:
            best = (c, round(score,2), reason)
    return best if best[1] >= 0.45 else (None, round(best[1],2), best[2])


def best_dataframe_column(dataset, label, categories=None):
    columns = [str(c) for c in dataset.columns]
    col, score, reason = best_column(columns, label, categories)
    if col is None:
        return None, score, reason
    vals = set(dataset[col].dropna().astype(str).map(norm).unique())
    cats = [norm(x) for x in (categories or []) if norm(x)]
    hits = sum(1 for x in cats if x in vals)
    if cats and hits:
        bonus = min(0.18, 0.05 * hits)
        score = min(0.99, round(score + bonus, 2))
        reason = reason + f'; {hits} category label(s) found'
    return col, score, reason


def outcome_candidates(dataset):
    out=[]
    for c in dataset.columns:
        if str(c).startswith('__'):
            continue
        s=dataset[c].dropna()
        unique=s.astype(str).map(norm).unique().tolist()
        if len(unique)!=2:
            continue
        n=norm(c)
        score=sum(0.12 for w in OUTCOME_WORDS if w in n)
        if set(unique) <= {'0','1'}: score += .35
        if any(x in {'yes','positive','unfavourable','unfavorable','no adherence','non adherence','non adherence'} for x in unique): score += .45
        if any(x in {'no','negative','adherent','favourable','favorable'} for x in unique): score += .12
        out.append({'variable':str(c),'values':unique,'confidence':round(min(score,0.99),2)})
    out.sort(key=lambda x:x['confidence'], reverse=True)
    return out[:20]


def _docx_frames(content: bytes):
    doc = Document(io.BytesIO(content)); frames={}
    for i, table in enumerate(doc.tables,1):
        rows=[[cell.text.strip() for cell in row.cells] for row in table.rows]
        if rows:
            width=max(len(r) for r in rows)
            frames[f'Table {i}']=pd.DataFrame([r+['']*(width-len(r)) for r in rows])
    return frames


def read_dummy(content: bytes, filename: str):
    ext=filename.lower().rsplit('.',1)[-1] if '.' in filename else ''
    if ext in ('xlsx','xls'):
        book=pd.ExcelFile(io.BytesIO(content)); sheets=book.sheet_names
        frames={s:pd.read_excel(io.BytesIO(content),sheet_name=s,header=None) for s in sheets}
    elif ext=='docx':
        frames=_docx_frames(content); sheets=list(frames.keys()) or ['DOCX']
    elif ext=='csv': sheets=['CSV']; frames={'CSV':pd.read_csv(io.BytesIO(content),header=None)}
    elif ext=='tsv': sheets=['TSV']; frames={'TSV':pd.read_csv(io.BytesIO(content),sep='\t',header=None)}
    elif ext=='json': sheets=['JSON']; frames={'JSON':pd.DataFrame(pd.read_json(io.BytesIO(content)))}
    else: sheets=['TEXT']; frames={'TEXT':pd.read_csv(io.BytesIO(content),sep='\t',header=None)}
    return sheets,frames


def build_spec(dataset: pd.DataFrame, dummy_content: bytes, dummy_filename: str):
    sheets,frames=read_dummy(dummy_content,dummy_filename)
    rows_spec=[]; columns=[str(c) for c in dataset.columns]
    current_variable=None
    variable_names=set(ALIASES)
    for sheet,frame in frames.items():
        for idx,row in frame.iterrows():
            vals=[x for x in row.tolist() if pd.notna(x) and str(x).strip()]
            if not vals: continue
            label=str(vals[0]).strip(); n=norm(label)
            if len(label)<2 or n in {'total','case','control','p value','pvalue'}: continue
            canonical=next((k for k,v in ALIASES.items() if n==k or n in {norm(x) for x in v}),None)
            if canonical in variable_names:
                current_variable=label
                rows_spec.append({'sheet':sheet,'row_index':int(idx),'label':label,'variable':None,'confidence':0,'match_reason':'variable heading','analysis':'variable heading'})
                continue
            if current_variable:
                # Treat the first column as a category under the active variable.
                category_values=[str(x).strip() for x in vals[1:] if str(x).strip()]
                variable,confidence,reason=best_dataframe_column(dataset,current_variable,category_values or [label])
                rows_spec.append({'sheet':sheet,'row_index':int(idx),'label':label,'variable':variable,'confidence':confidence,'match_reason':reason,'analysis':'categorical n (%) + group comparison' if variable else 'needs variable mapping'})
    seen=set(); unique=[]
    for r in rows_spec:
        key=(r['sheet'],r['row_index'])
        if key not in seen:
            seen.add(key); unique.append(r)
    return {'sheets':sheets,'rows_spec':unique[:300],'outcome_candidates':outcome_candidates(dataset)}
