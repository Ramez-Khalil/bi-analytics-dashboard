"""Reproducible Telco churn analysis. Rebuilt portfolio pipeline, not original course code."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix, RocCurveDisplay

SEED = 42
NUMERIC = ['tenure', 'MonthlyCharges', 'TotalCharges']
CATEGORICAL = ['Contract','InternetService','PaymentMethod','PaperlessBilling','PhoneService','MultipleLines','OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies']
FEATURES = NUMERIC + CATEGORICAL


def validate(df):
    required = set(FEATURES + ['customerID','Churn'])
    if not required.issubset(df.columns):
        raise ValueError(f'Missing columns: {sorted(required - set(df.columns))}')
    if df.customerID.isna().any() or df.customerID.duplicated().any():
        raise ValueError('Customer IDs must be present and unique.')
    if not set(df.Churn.unique()) <= {'Yes','No'} or df.Churn.nunique() != 2:
        raise ValueError('Churn must contain both Yes and No only.')
    df = df.copy()
    for col in NUMERIC:
        raw = df[col].astype(str).str.strip()
        parsed = pd.to_numeric(raw, errors='coerce')
        if ((raw != '') & parsed.isna()).any():
            raise ValueError(f'Unexpected nonnumeric value in {col}')
        if col != 'TotalCharges' and parsed.isna().any():
            raise ValueError(f'Missing {col}')
        if (parsed.dropna() < 0).any():
            raise ValueError(f'Negative {col}')
        df[col] = parsed
    if df[CATEGORICAL].isna().any().any():
        raise ValueError('Missing categorical values')
    return df


def pipeline(model):
    numeric = Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler())])
    transform = ColumnTransformer([('numeric',numeric,NUMERIC),('category',OneHotEncoder(handle_unknown='ignore', sparse_output=False),CATEGORICAL)])
    return Pipeline([('prepare',transform),('model',model)])


def segments(df, key):
    return df.assign(churn=df.Churn.eq('Yes').astype(int)).groupby(key, observed=True).churn.agg(['size','sum','mean']).rename(columns={'size':'customers','sum':'churned','mean':'churn_rate'})


def run(path, out):
    out.mkdir(parents=True,exist_ok=True)
    df = validate(pd.read_csv(path,keep_default_na=False))
    X,y = df[FEATURES], df.Churn.eq('Yes').astype(int)
    train,test = train_test_split(np.arange(len(df)),test_size=.3,stratify=y,random_state=SEED)
    assert set(train).isdisjoint(test)
    models={'Majority baseline':DummyClassifier(strategy='most_frequent'), 'Logistic regression':LogisticRegression(max_iter=2000,random_state=SEED), 'Decision tree':DecisionTreeClassifier(max_depth=5,min_samples_leaf=30,random_state=SEED)}
    metrics={}; fitted={}
    for name,model in models.items():
        p=pipeline(model).fit(X.iloc[train],y.iloc[train]); fitted[name]=p
        pred=p.predict(X.iloc[test]); prob=p.predict_proba(X.iloc[test])[:,1]
        metrics[name]={'accuracy':accuracy_score(y.iloc[test],pred),'precision':precision_score(y.iloc[test],pred,zero_division=0),'recall':recall_score(y.iloc[test],pred,zero_division=0),'f1':f1_score(y.iloc[test],pred,zero_division=0),'roc_auc':roc_auc_score(y.iloc[test],prob),'average_precision':average_precision_score(y.iloc[test],prob),'confusion_matrix':confusion_matrix(y.iloc[test],pred).tolist()}
    summary={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':len(df),'churned':int(y.sum()),'churn_rate':float(y.mean()),'train_rows':len(train),'test_rows':len(test),'seed':SEED,'missing_total_charges':int(df.TotalCharges.isna().sum()),'features':FEATURES,'metrics':metrics,'split_overlap':0,'train_total_charges_median':float(X.iloc[train].TotalCharges.median())}
    (out/'metrics.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    by_contract=segments(df,'Contract'); by_contract.to_csv(out/'contract_segments.csv')
    df['tenure_band']=pd.cut(df.tenure,[-1,6,12,24,48,72],labels=['0-6','7-12','13-24','25-48','49-72'])
    by_tenure=segments(df,'tenure_band'); by_tenure.to_csv(out/'tenure_segments.csv')
    charge=df.groupby('Churn').MonthlyCharges.agg(['count','mean','median']); charge.to_csv(out/'charge_summary.csv')
    # Three initial hypotheses are addressed descriptively, not as causal effects.
    # Models evaluate held-out classification, not hypothesis significance.
    plt.rcParams.update({'svg.hashsalt':'churn-portfolio-v1','font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#334155','text.color':'#0f172a','figure.facecolor':'#f8fafc','axes.facecolor':'#ffffff'})
    fig,axes=plt.subplots(2,2,figsize=(14,9),layout='constrained')
    fig.suptitle('Customer retention | Evidence overview',fontsize=23,fontweight='bold')
    for ax,table,title in [(axes[0,0],by_contract,'Contract type'),(axes[0,1],by_tenure,'Customer tenure (months)')]:
        bars=ax.bar(table.index.astype(str),100*table.churn_rate,color='#157a93')
        ax.bar_label(bars,fmt='%.1f%%',padding=3);ax.set_ylim(0,65);ax.set_ylabel('Observed churn (%)');ax.set_title(title,loc='left');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    axes[1,0].boxplot([df.loc[df.Churn.eq('No'),'MonthlyCharges'],df.loc[df.Churn.eq('Yes'),'MonthlyCharges']],tick_labels=['Stayed','Churned'],patch_artist=True,boxprops={'facecolor':'#cbd5e1'})
    axes[1,0].set_title('Monthly charges by outcome',loc='left');axes[1,0].set_ylabel('Monthly charge ($)')
    for name in ['Logistic regression','Decision tree']:
        RocCurveDisplay.from_estimator(fitted[name],X.iloc[test],y.iloc[test],name=name,ax=axes[1,1])
    axes[1,1].plot([0,1],[0,1],linestyle='--',color='#94a3b8');axes[1,1].set_title('Held-out discrimination | 30% test set',loc='left')
    fig.savefig(out/'overview.png',dpi=160);fig.savefig(out/'overview.svg',metadata={'Date':None});plt.close(fig)
    svg=out/'overview.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n',encoding='utf-8')
    rows=''.join(f'<tr><td>{name}</td>'+''.join(f'<td>{m[k]:.3f}</td>' for k in ['accuracy','precision','recall','f1','roc_auc','average_precision'])+'</tr>' for name,m in metrics.items())
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Customer Retention | Analytics Review</title><style>body{margin:0;background:#f1f5f9;color:#172b43;font:16px/1.6 system-ui}main{max-width:1100px;margin:40px auto;padding:0 24px}header{background:#102a43;color:white;padding:38px;border-radius:18px}h1{font-size:38px;line-height:1.1;margin:12px 0}.eyebrow{color:#67e8f9;text-transform:uppercase;letter-spacing:2px;font-size:12px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.card,section{background:white;border:1px solid #dce4ed;border-radius:14px;padding:24px;margin-bottom:20px}.num{font-size:32px;font-weight:750;color:#087e8b}img{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:12px;border-bottom:1px solid #dae2eb}th{background:#eaf4f6}.scroll{overflow-x:auto}.muted{color:#53657b;font-size:14px}li{margin:10px 0}@media(max-width:650px){.cards{grid-template-columns:1fr}h1{font-size:30px}header{padding:24px}}</style><main><header><div class="eyebrow">Business intelligence / Customer retention</div><h1>Understand churn.<br>Test the next decision.</h1><p>A reproducible analysis of IBM's Telco customer sample, connecting descriptive segments with held-out model evaluation.</p></header>'''
    html+=f'<div class="cards"><div class="card">Sample customers<div class="num">{len(df):,}</div></div><div class="card">Observed churn<div class="num">{y.mean():.1%}</div></div><div class="card">Untouched test rows<div class="num">{len(test):,}</div></div></div>'
    html+='<section><h2>Patterns and prediction</h2><p class="muted">Segment charts use the full sample descriptively. Model curves use only the held-out test split. Associations are not evidence that an intervention causes lower churn.</p><img src="overview.svg" alt="Churn rates by contract and tenure, monthly charge distributions, and held-out ROC curves"></section>'
    html+='<section><h2>Compare against a baseline</h2><div class="scroll"><table><tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th><th>ROC AUC</th><th>Avg precision</th></tr>'+rows+'</table></div><p class="muted">Churn is the positive class. Logistic threshold: 0.5. Tree: depth 5, minimum 30 records per leaf. All parameters fixed before evaluation; no test-set tuning.</p></section>'
    html+='<section><h2>Business interpretation</h2><ul><li>Investigate onboarding and support in high-churn early-tenure segments; validate explanations with customer research.</li><li>Test voluntary contract incentives with a randomized pilot, measuring incremental retention and net cost.</li><li>Review value perception among higher-bill segments. These data cannot establish that lowering prices will reduce churn.</li></ul></section><section><h2>Scope and limits</h2><p>This is a portfolio reconstruction, not a live scoring system or an exact reproduction of the original coursework run. A random split on one historical sample does not validate future deployment. There is no causal experiment, temporal validation, fairness audit or campaign ROI evidence.</p><p class="muted">Data: IBM Telco sample (Apache-2.0 repository). This report publishes aggregates only. Demographics and customer IDs are excluded from modeling; that does not establish fairness.</p></section></main></html>'
    (out/'index.html').write_text(html,encoding='utf-8')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,default=Path('data/Telco-Customer-Churn.csv'));parser.add_argument('--out',type=Path,default=Path('reports'));args=parser.parse_args(); print(json.dumps(run(args.data,args.out),indent=2))
