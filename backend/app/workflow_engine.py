"""Validated helpers for the unified Medical Analytics workflow."""
import io, json, re
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve
from statsmodels.stats.proportion import proportion_confint


def read_dataset(filename, content):
    name=(filename or '').lower()
    if name.endswith('.csv'): return pd.read_csv(io.BytesIO(content))
    if name.endswith('.tsv'): return pd.read_csv(io.BytesIO(content), sep='\t')
    if name.endswith(('.xlsx','.xls','.xlsm')): return pd.read_excel(io.BytesIO(content), sheet_name=0)
    if name.endswith('.ods'): return pd.read_excel(io.BytesIO(content), engine='odf')
    if name.endswith('.dta'): return pd.read_stata(io.BytesIO(content))
    if name.endswith(('.sav','.sas7bdat')):
        import pyreadstat
        return pyreadstat.read_sav(io.BytesIO(content))[0] if name.endswith('.sav') else pyreadstat.read_sas7bdat(io.BytesIO(content))[0]
    if name.endswith('.json'):
        try: return pd.read_json(io.BytesIO(content))
        except ValueError: return pd.json_normalize(json.loads(content.decode('utf-8')))
    if name.endswith('.txt'): return pd.read_csv(io.BytesIO(content), sep=None, engine='python')
    raise ValueError('Unsupported analysis dataset format')


def data_quality_plus(df, id_variables=None):
    ids=set(id_variables or []); rows=[]
    for col in df.columns:
        s=df[col]; miss=int(s.isna().sum()); nonmiss=int(s.notna().sum()); unique=int(s.nunique(dropna=True)); issues=[]
        if miss: issues.append('missing values')
        if unique<=1: issues.append('constant/empty')
        if unique>max(50,int(len(df)*.5)): issues.append('high cardinality')
        rate=float(pd.to_numeric(s.dropna().astype(str).str.replace(',','',regex=False).str.strip(),errors='coerce').notna().mean()) if nonmiss else 0
        if not pd.api.types.is_numeric_dtype(s) and .80<=rate<1: issues.append('mixed numeric/text')
        if pd.api.types.is_numeric_dtype(s) and nonmiss>=5:
            q1,q3=s.quantile(.25),s.quantile(.75); iqr=q3-q1; out=int(((s<q1-1.5*iqr)|(s>q3+1.5*iqr)).sum()) if iqr>0 else 0
            if out: issues.append(f'{out} IQR outlier(s)')
        rows.append({'variable':str(col),'n':nonmiss,'missing':miss,'missing_percent':round(miss/max(len(df),1)*100,2),'unique':unique,'numeric_parse_percent':round(rate*100,2),'issues':issues})
    duplicate_rows=int(df.duplicated().sum()); duplicate_ids=[]
    for col in df.columns:
        name=str(col).lower()
        if col in ids or re.search(r'(^|_)(id|patient|participant|subject|mrn|record)(_|$)',name):
            dup=int(df[col].dropna().duplicated().sum())
            if dup: duplicate_ids.append({'variable':str(col),'duplicate_nonmissing_ids':dup})
    return {'rows':int(len(df)),'columns':int(df.shape[1]),'duplicate_rows':duplicate_rows,'duplicate_id_variables':duplicate_ids,'variables':rows,'warnings':(['Duplicate rows detected'] if duplicate_rows else [])+(['Duplicate identifier values detected'] if duplicate_ids else [])}


def _binary(series, positive, negative=None):
    p={str(x).strip().casefold() for x in (positive or [])}; n={str(x).strip().casefold() for x in (negative or [])}
    vals=series.dropna().map(lambda x:str(x).strip().casefold()); unknown=sorted(set(vals)-p-n)
    if unknown: raise ValueError(f'Unmapped values found: {unknown[:10]}. Confirm coding before analysis.')
    if not p: raise ValueError('At least one positive coding value is required')
    return series.map(lambda x:np.nan if pd.isna(x) else (1 if str(x).strip().casefold() in p else 0))


def _cp(success,total):
    if total==0:return [None,None]
    lo,hi=proportion_confint(success,total,alpha=.05,method='beta'); return [float(lo),float(hi)]


def diagnostic_validated(df,index_test,reference_standard,index_positive,reference_positive,index_negative=None,reference_negative=None):
    a=_binary(df[index_test],index_positive,index_negative); b=_binary(df[reference_standard],reference_positive,reference_negative); x=pd.DataFrame({'a':a,'b':b}).dropna()
    if x.empty: raise ValueError('No complete observations remain after confirmed coding.')
    tp=int(((x.a==1)&(x.b==1)).sum()); tn=int(((x.a==0)&(x.b==0)).sum()); fp=int(((x.a==1)&(x.b==0)).sum()); fn=int(((x.a==0)&(x.b==1)).sum()); n=len(x)
    sens=tp/(tp+fn) if tp+fn else np.nan; spec=tn/(tn+fp) if tn+fp else np.nan; ppv=tp/(tp+fp) if tp+fp else np.nan; npv=tn/(tn+fn) if tn+fn else np.nan; acc=(tp+tn)/n; plr=sens/(1-spec) if spec<1 else np.inf; nlr=(1-sens)/spec if spec>0 else np.nan
    return {'n':n,'tp':tp,'tn':tn,'fp':fp,'fn':fn,'sensitivity':sens,'specificity':spec,'ppv':ppv,'npv':npv,'accuracy':acc,'plr':plr,'nlr':nlr,'metrics_95ci':{k:{'estimate':v[0],'lower':v[1][0],'upper':v[1][1]} for k,v in {'sensitivity':(sens,_cp(tp,tp+fn)),'specificity':(spec,_cp(tn,tn+fp)),'ppv':(ppv,_cp(tp,tp+fp)),'npv':(npv,_cp(tn,tn+fn)),'accuracy':(acc,_cp(tp+tn,n))}.items()},'ci_method':'Clopper-Pearson exact 95% CI'}


def roc_validated(df,test,outcome,positive_values):
    x=df[[test,outcome]].dropna().copy(); y=_binary(x[outcome],positive_values,[v for v in x[outcome].unique() if str(v).strip().casefold() not in {str(z).strip().casefold() for z in positive_values}]); scores=pd.to_numeric(x[test],errors='coerce'); keep=scores.notna()&y.notna(); y=y[keep].astype(int); scores=scores[keep].astype(float)
    if y.nunique()!=2: raise ValueError('ROC outcome must contain exactly two confirmed classes')
    auc=float(roc_auc_score(y,scores)); fpr,tpr,thr=roc_curve(y,scores); spec=1-fpr; youden=tpr+spec-1; finite=np.isfinite(thr); idx=int(np.argmax(np.where(finite,youden,-np.inf)))
    return {'n':int(len(y)),'auc':auc,'fpr':fpr.tolist(),'tpr':tpr.tolist(),'specificity':spec.tolist(),'thresholds':thr.tolist(),'youden_j':youden.tolist(),'optimal_cutoff':float(thr[idx]) if finite[idx] else None,'optimal_sensitivity':float(tpr[idx]),'optimal_specificity':float(spec[idx]),'optimal_youden_j':float(youden[idx])}
