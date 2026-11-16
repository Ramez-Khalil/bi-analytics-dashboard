import numpy as np
import pandas as pd
import pytest
from analysis import validate, pipeline, FEATURES, NUMERIC, CATEGORICAL
from sklearn.linear_model import LogisticRegression

def sample():
    d=pd.DataFrame({k:['A','B','A','B'] for k in CATEGORICAL})
    d['tenure']=[1,2,3,4];d['MonthlyCharges']=[20,40,60,80];d['TotalCharges']=['','80','180','320'];d['customerID']=['a','b','c','d'];d['Churn']=['Yes','No','Yes','No']
    return d

def test_blank_total_charge_is_missing():
    assert np.isnan(validate(sample()).TotalCharges.iloc[0])

def test_duplicate_id_rejected():
    d=sample();d.loc[1,'customerID']='a'
    with pytest.raises(ValueError,match='unique'):validate(d)

def test_invalid_target_rejected():
    d=sample();d.loc[0,'Churn']='maybe'
    with pytest.raises(ValueError,match='Churn'):validate(d)

def test_negative_charge_rejected():
    d=sample();d.loc[0,'MonthlyCharges']=-1
    with pytest.raises(ValueError,match='Negative'):validate(d)

def test_invalid_numeric_rejected():
    d=sample();d.loc[0,'TotalCharges']='unknown'
    with pytest.raises(ValueError,match='nonnumeric'):validate(d)

def test_missing_required_column_rejected():
    with pytest.raises(ValueError,match='Missing columns'):validate(sample().drop(columns='tenure'))

def test_train_only_imputation_and_unknown_categories():
    d=validate(sample());p=pipeline(LogisticRegression()).fit(d[FEATURES].iloc[:3],[1,0,1])
    imputer=p.named_steps['prepare'].named_transformers_['numeric'].named_steps['imputer']
    assert imputer.statistics_[2]==130 # median of train 80,180, not test320
    test=d[FEATURES].iloc[[3]].copy();test['Contract']='unseen'
    assert p.predict_proba(test).shape==(1,2)

def test_identifiers_and_demographics_excluded():
    assert not set(FEATURES)&{'customerID','Churn','gender','SeniorCitizen','Partner','Dependents'}

def test_published_artifacts_reconcile():
    import json
    from pathlib import Path
    r=json.loads(Path('reports/metrics.json').read_text())
    contract=pd.read_csv('reports/contract_segments.csv')
    tenure=pd.read_csv('reports/tenure_segments.csv')
    assert contract.customers.sum()==tenure.customers.sum()==r['rows']==7043
    assert contract.churned.sum()==tenure.churned.sum()==r['churned']==1869
    assert r['train_rows']+r['test_rows']==r['rows']
    assert r['split_overlap']==0
    for m in r['metrics'].values():
        cm=np.asarray(m['confusion_matrix'])
        assert cm.sum()==r['test_rows']
        assert np.isclose(np.trace(cm)/cm.sum(),m['accuracy'])
        assert np.isclose(cm[1,1]/cm[1].sum(),m['recall'])
    from fetch_data import SHA256
    assert r['source_sha256']==SHA256
