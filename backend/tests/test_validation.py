import numpy as np
import pandas as pd
from backend.app.workflow_engine import diagnostic_validated, data_quality_plus
from backend.app.analysis_engine import categorical_association, robust_poisson


def test_diagnostic_exact_cells_and_metrics():
    df=pd.DataFrame({'test':['P','P','N','N'],'ref':['P','N','P','N']})
    r=diagnostic_validated(df,'test','ref',['P'],['P'],['N'],['N'])
    assert (r['tp'],r['tn'],r['fp'],r['fn'])==(1,1,1,1)
    assert r['sensitivity']==0.5 and r['specificity']==0.5 and r['accuracy']==0.5
    assert r['ci_method']=='Clopper-Pearson exact 95% CI'


def test_quality_finds_duplicates_and_missing():
    df=pd.DataFrame({'patient_id':[1,1,2],'age':[20,np.nan,21],'sex':['M','F','M']})
    q=data_quality_plus(df)
    assert q['duplicate_rows']==0
    assert q['duplicate_id_variables'][0]['variable']=='patient_id'
    age=next(x for x in q['variables'] if x['variable']=='age')
    assert age['missing']==1


def test_association_known_2x2():
    df=pd.DataFrame({'exposure':[1,1,0,0],'outcome':[1,0,1,0]})
    r=categorical_association(df,'exposure','outcome')
    assert abs(r['chi_square']) < 1e-12
    assert r['fisher_p']==1.0


def test_poisson_returns_reference_metadata():
    df=pd.DataFrame({'y':[0,1,0,1,1,0,1,0],'x':['A','A','A','B','B','B','B','A']})
    r=robust_poisson(df,'y',['x'],['x'],{'x':'A'})
    assert r['method'].startswith('Poisson regression')
    assert r['adjusted'][0]['reference']=='A'
