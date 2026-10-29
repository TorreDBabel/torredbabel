"""Reconstruye el panel y replica el cuaderno. Objetivo: comprobar que la
reconstruccion es fiel antes de calcular cualquier cifra nueva."""
import numpy as np, pandas as pd, json
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from xgboost import XGBClassifier
import os
DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
os.makedirs(SALIDA, exist_ok=True)

SEED = 42
np.random.seed(SEED)
FUENTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fuente',
                      'series_anuales_municipales_choco_1983_2016.xlsx')

# ---------- 1. panel 31 x 34 ----------
s = pd.read_excel(FUENTE, sheet_name='Serie larga municipal')
s = s.rename(columns={'MUNICIPIO': 'municipio', 'ANIO': 'anio',
                      'HECHOS_UNICOS': 'hechos', 'COD_MPIO': 'cod'})
base = pd.read_csv(os.path.join(DATOS, 'base_municipal.csv'))
cero = sorted(set(base.municipio) - set(s.municipio))
anios = sorted(s.anio.unique())
extra = pd.DataFrame([{'municipio': m, 'anio': a, 'hechos': 0} for m in cero for a in anios])
panel = pd.concat([s[['municipio', 'anio', 'hechos']], extra], ignore_index=True)

print(f"panel: {panel.shape[0]} filas (esperado 1054) | municipios {panel.municipio.nunique()} "
      f"| hechos {int(panel.hechos.sum())} (esperado 361)")
assert panel.shape[0] == 1054 and int(panel.hechos.sum()) == 361

# ---------- 2. variables, identicas a la celda 13 del cuaderno ----------
df = panel.sort_values(['municipio', 'anio']).reset_index(drop=True)
g = df.groupby('municipio')['hechos']
df['lag1'] = g.shift(1)
df['lag2'] = g.shift(2)
df['lag3'] = g.shift(3)
df['media_movil3'] = g.transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
df['acum_prev'] = g.transform(lambda x: x.shift(1).cumsum()).fillna(0)
df['anios_activos_prev'] = g.transform(lambda x: (x.shift(1) > 0).cumsum()).fillna(0)

def racha_previa(x):
    out, c = [], 0
    for v in x.shift(1).fillna(0):
        c = c + 1 if v > 0 else 0
        out.append(c)
    return pd.Series(out, index=x.index)

def anios_desde_ultimo(x):
    out, ultimo = [], None
    for i, v in enumerate(x.shift(1).fillna(0)):
        if v > 0:
            ultimo = i
        out.append(i - ultimo if ultimo is not None else 99)
    return pd.Series(out, index=x.index)

df['racha_prev'] = df.groupby('municipio')['hechos'].transform(racha_previa)
df['anios_desde_ultimo'] = df.groupby('municipio')['hechos'].transform(anios_desde_ultimo)
df['depto_lag1'] = df['anio'].map(df.groupby('anio')['hechos'].sum().shift(1))
df['ocurrencia'] = (df['hechos'] > 0).astype(int)

FEATS = ['lag1', 'lag2', 'lag3', 'media_movil3', 'acum_prev',
         'anios_activos_prev', 'racha_prev', 'anios_desde_ultimo', 'depto_lag1']
datos = df.dropna(subset=['lag1', 'depto_lag1']).copy()
datos[FEATS] = datos[FEATS].fillna(0)
print(f"panel modelable: {datos.shape[0]} filas (el cuaderno reporta 1023)")

# ---------- 3. particion fija ----------
train = datos[datos.anio <= 2010].copy()
test = datos[datos.anio > 2010].copy()
y_test = test['ocurrencia']
print(f"train {len(train)} (837) prev {train.ocurrencia.mean():.1%} (13,5%) | "
      f"test {len(test)} (186) prev {test.ocurrencia.mean():.1%} (33,3%)")
print(f"hechos train {int(train.hechos.sum())} (202) | test {int(test.hechos.sum())} (158)")

def lr_nuevo(seed=SEED):
    return make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=1000, class_weight='balanced',
                                            random_state=seed))

def xgb_nuevo(peso, seed=SEED, md=3, lr_=0.05):
    return XGBClassifier(n_estimators=300, max_depth=md, learning_rate=lr_,
                         subsample=0.9, scale_pos_weight=peso,
                         random_state=seed, eval_metric='logloss')

pred_base = (test['lag1'] > 0).astype(int)
m_lr = lr_nuevo().fit(train[FEATS], train['ocurrencia'])
p_lr = m_lr.predict_proba(test[FEATS])[:, 1]
peso = (train.ocurrencia == 0).sum() / (train.ocurrencia == 1).sum()
m_xgb = xgb_nuevo(peso).fit(train[FEATS], train['ocurrencia'])
p_xgb = m_xgb.predict_proba(test[FEATS])[:, 1]

rep = {
    'base_auc': roc_auc_score(y_test, pred_base), 'base_pr': average_precision_score(y_test, pred_base),
    'lr_auc': roc_auc_score(y_test, p_lr), 'lr_pr': average_precision_score(y_test, p_lr),
    'xgb_auc': roc_auc_score(y_test, p_xgb), 'xgb_pr': average_precision_score(y_test, p_xgb),
    'prevalencia': float(y_test.mean()),
}
esperado = {'base_auc': 0.734, 'base_pr': 0.526, 'lr_auc': 0.792, 'lr_pr': 0.723,
            'xgb_auc': 0.769, 'xgb_pr': 0.706, 'prevalencia': 0.333}
print('\n--- replica de la particion fija 2011-2016 ---')
for k, v in rep.items():
    e = esperado[k]
    marca = 'OK' if abs(v - e) < 0.0051 else 'DIFIERE'
    print(f"  {k:<12} obtenido {v:.3f} | cuaderno {e:.3f} | {marca}")

# ---------- 4. origen rodante, 11 ventanas ----------
filas, pool = [], {'y': [], 'base': [], 'lr': [], 'xgb': [], 'anio': [], 'mun': [], 'hechos': []}
for ae in range(2006, 2017):
    tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
    pz = (tr.ocurrencia == 0).sum() / (tr.ocurrencia == 1).sum()
    plr = lr_nuevo().fit(tr[FEATS], tr['ocurrencia']).predict_proba(te[FEATS])[:, 1]
    pxg = xgb_nuevo(pz).fit(tr[FEATS], tr['ocurrencia']).predict_proba(te[FEATS])[:, 1]
    pb = (te['lag1'] > 0).astype(int)
    filas.append({'anio': ae, 'base': roc_auc_score(te.ocurrencia, pb),
                  'lr': roc_auc_score(te.ocurrencia, plr), 'xgb': roc_auc_score(te.ocurrencia, pxg)})
    pool['y'] += list(te.ocurrencia); pool['base'] += list(pb)
    pool['lr'] += list(plr); pool['xgb'] += list(pxg)
    pool['anio'] += list(te.anio); pool['mun'] += list(te.municipio); pool['hechos'] += list(te.hechos)

tr_roll = pd.DataFrame(filas)
print('\n--- origen rodante, 11 ventanas ---')
print(tr_roll.round(3).to_string(index=False))
print(f"promedio anual: base {tr_roll.base.mean():.3f} (0,717) | lr {tr_roll.lr.mean():.3f} (0,798) "
      f"| xgb {tr_roll.xgb.mean():.3f} (0,771)")
print(f"agrupado:       base {roc_auc_score(pool['y'],pool['base']):.3f} (0,714) | "
      f"lr {roc_auc_score(pool['y'],pool['lr']):.3f} (0,789) | "
      f"xgb {roc_auc_score(pool['y'],pool['xgb']):.3f} (0,748)")

P = pd.DataFrame(pool)
P.to_csv(os.path.join(SALIDA, 'pool_rodante.csv'), index=False)
datos.to_csv(os.path.join(DATOS, 'panel_modelable_1984_2016.csv'), index=False)
print(f"\npool rodante: {len(P)} filas | hechos {int(P.hechos.sum())} | prevalencia {P.y.mean():.3f}")
print(f"AUC-PR agrupado lr {average_precision_score(P.y,P.lr):.3f} | base-azar {P.y.mean():.3f}")
print(f"Brier lr {brier_score_loss(P.y,P.lr):.3f} | Brier de referencia (constante=prevalencia) "
      f"{brier_score_loss(P.y,np.full(len(P),P.y.mean())):.3f}")
