"""Intervalos de confianza, calibracion, colinealidad y errores agrupados.
Todo lo que un evaluador estadistico pide y el cuaderno no trae."""
import numpy as np, pandas as pd, json, time, itertools, warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.isotonic import IsotonicRegression
from xgboost import XGBClassifier
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import os
DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
os.makedirs(SALIDA, exist_ok=True)

SEED = 42
rng = np.random.default_rng(SEED)
datos = pd.read_csv(os.path.join(DATOS, 'panel_modelable_1984_2016.csv'))
FEATS = ['lag1', 'lag2', 'lag3', 'media_movil3', 'acum_prev',
         'anios_activos_prev', 'racha_prev', 'anios_desde_ultimo', 'depto_lag1']
R = {}

def lr_(): return make_pipeline(StandardScaler(), LogisticRegression(
    max_iter=1000, class_weight='balanced', random_state=SEED))
def lr_sin_peso(): return make_pipeline(StandardScaler(), LogisticRegression(
    max_iter=1000, random_state=SEED))
def xgb_(p): return XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
    subsample=0.9, scale_pos_weight=p, random_state=SEED, eval_metric='logloss')

# ============ 1. pool rodante con los dos modelos y la variante sin pesos ============
P = []
t0 = time.perf_counter(); t_lr = t_xgb = 0.0
for ae in range(2006, 2017):
    tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
    pz = (tr.ocurrencia == 0).sum() / (tr.ocurrencia == 1).sum()
    a = time.perf_counter(); m1 = lr_().fit(tr[FEATS], tr.ocurrencia); t_lr += time.perf_counter() - a
    a = time.perf_counter(); m2 = xgb_(pz).fit(tr[FEATS], tr.ocurrencia); t_xgb += time.perf_counter() - a
    m3 = lr_sin_peso().fit(tr[FEATS], tr.ocurrencia)
    P.append(pd.DataFrame({'anio': te.anio.values, 'mun': te.municipio.values,
                           'y': te.ocurrencia.values, 'h': te.hechos.values,
                           'lr': m1.predict_proba(te[FEATS])[:, 1],
                           'xgb': m2.predict_proba(te[FEATS])[:, 1],
                           'lr_np': m3.predict_proba(te[FEATS])[:, 1]}))
P = pd.concat(P, ignore_index=True)
R['tiempo_total_rodante_s'] = round(time.perf_counter() - t0, 2)
R['tiempo_ajuste_lr_s'] = round(t_lr, 3)
R['tiempo_ajuste_xgb_s'] = round(t_xgb, 3)
R['tiempo_ajuste_lr_ventana_ms'] = round(1000 * t_lr / 11, 1)
R['tiempo_ajuste_xgb_ventana_ms'] = round(1000 * t_xgb / 11, 1)
R['n_pool'] = len(P); R['hechos_pool'] = int(P.h.sum()); R['prevalencia_pool'] = round(P.y.mean(), 4)

def prec_k(d, col, k=5):
    top = d.sort_values(['anio', col], ascending=[True, False]).groupby('anio').head(k)
    return top.y.mean(), top.h.sum() / d.h.sum()

def metricas(d, col):
    p5, cob5 = prec_k(d, col, 5)
    return dict(aucroc=roc_auc_score(d.y, d[col]), aucpr=average_precision_score(d.y, d[col]),
                brier=brier_score_loss(d.y, d[col]), prec5=p5, cob5=cob5)

# ============ 2. bootstrap por bloques de municipio ============
MUN = P.mun.unique()
B = 4000
acc = {c: {k: [] for k in ['aucroc', 'aucpr', 'brier', 'prec5', 'cob5']} for c in ['lr', 'xgb']}
for _ in range(B):
    elegidos = rng.choice(MUN, size=len(MUN), replace=True)
    d = pd.concat([P[P.mun == m].assign(mun=f'{m}_{i}') for i, m in enumerate(elegidos)],
                  ignore_index=True)
    if d.y.nunique() < 2:
        continue
    for c in ['lr', 'xgb']:
        m = metricas(d, c)
        for k, v in m.items():
            acc[c][k].append(v)

def ic(v):
    v = np.asarray(v, float)
    return round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)

print('=== metricas fuera de muestra, origen rodante 2006-2016 (11 ventanas) ===')
print(f"n = {len(P)} municipio-año | hechos = {int(P.h.sum())} | prevalencia = {P.y.mean():.3f}")
print(f"bootstrap por bloques de municipio, B = {B}, 31 bloques\n")
fil = []
for c, et in [('lr', 'Regresión logística'), ('xgb', 'XGBoost')]:
    pt = metricas(P, c)
    for k, nom in [('aucroc', 'AUC-ROC'), ('aucpr', 'AUC-PR'), ('prec5', 'Precisión@5'),
                   ('cob5', 'Cobertura de hechos con top-5'), ('brier', 'Brier')]:
        lo, hi = ic(acc[c][k])
        fil.append(dict(modelo=et, metrica=nom, valor=round(pt[k], 3), ic95=f'[{lo:.3f}; {hi:.3f}]'))
        R[f'{c}_{k}'] = round(pt[k], 4); R[f'{c}_{k}_ic'] = [lo, hi]
tab = pd.DataFrame(fil)
print(tab.to_string(index=False))

# referencias
R['aucpr_azar'] = round(P.y.mean(), 4)
R['brier_ref'] = round(P.y.mean() * (1 - P.y.mean()), 4)
R['prec5_azar'] = round(P.y.mean(), 4)
R['lift_aucpr_lr'] = round(R['lr_aucpr'] / R['aucpr_azar'], 3)
print(f"\nreferencias del azar: AUC-PR = prevalencia = {R['aucpr_azar']:.3f} | "
      f"Brier constante = p(1-p) = {R['brier_ref']:.3f} | Precisión@5 = {R['prec5_azar']:.3f}")
print(f"ventaja de la logistica en AUC-PR: {R['lift_aucpr_lr']:.2f} veces el azar")

# ============ 3. calibracion ============
print('\n=== calibracion ===')
cal = []
for c, et in [('lr', 'logística con class_weight=balanced'), ('lr_np', 'logística sin reponderar'),
              ('xgb', 'XGBoost con scale_pos_weight')]:
    cal.append(dict(variante=et, brier=round(brier_score_loss(P.y, P[c]), 3),
                    prob_media=round(P[c].mean(), 3), tasa_real=round(P.y.mean(), 3),
                    aucroc=round(roc_auc_score(P.y, P[c]), 3)))
# recalibracion isotonica honesta: ajustada en las 6 primeras ventanas, evaluada en las 5 ultimas
ini, fin = P[P.anio <= 2011], P[P.anio > 2011]
iso = IsotonicRegression(out_of_bounds='clip').fit(ini.lr, ini.y)
cal.append(dict(variante='logística + isotónica (ajuste 2006-2011, prueba 2012-2016)',
                brier=round(brier_score_loss(fin.y, iso.transform(fin.lr)), 3),
                prob_media=round(float(iso.transform(fin.lr).mean()), 3),
                tasa_real=round(fin.y.mean(), 3),
                aucroc=round(roc_auc_score(fin.y, iso.transform(fin.lr)), 3)))
cal.append(dict(variante='   (la misma ventana sin recalibrar, para comparar)',
                brier=round(brier_score_loss(fin.y, fin.lr), 3), prob_media=round(fin.lr.mean(), 3),
                tasa_real=round(fin.y.mean(), 3), aucroc=round(roc_auc_score(fin.y, fin.lr), 3)))
print(pd.DataFrame(cal).to_string(index=False))
R['calibracion'] = cal

# ============ 4. semaforo por terciles ============
print('\n=== semaforo: terciles del riesgo fuera de muestra (logistica) ===')
P['nivel'] = pd.qcut(P.lr, 3, labels=['BAJA', 'MEDIA', 'ALTA'])
t = P.groupby('nivel', observed=True).agg(mun_anios=('y', 'size'), ocurrencias=('y', 'sum'),
                                          hechos=('h', 'sum'), tasa=('y', 'mean')).reset_index()
t['pct_territorio'] = (100 * t.mun_anios / len(P)).round(1)
t['pct_hechos'] = (100 * t.hechos / P.h.sum()).round(1)
print(t.round(3).to_string(index=False))
R['semaforo'] = t.to_dict('records')
lift = t[t.nivel == 'ALTA'].tasa.iloc[0] / t[t.nivel == 'BAJA'].tasa.iloc[0]
R['lift_alta_baja'] = round(float(lift), 2)
# intervalo del lift
lifts = []
for _ in range(2000):
    el = rng.choice(MUN, size=len(MUN), replace=True)
    d = pd.concat([P[P.mun == m] for m in el], ignore_index=True)
    d['nv'] = pd.qcut(d.lr, 3, labels=['B', 'M', 'A'], duplicates='drop')
    g = d.groupby('nv', observed=True).y.mean()
    if 'A' in g and 'B' in g and g.get('B', 0) > 0:
        lifts.append(g['A'] / g['B'])
R['lift_alta_baja_ic'] = list(ic(lifts))
print(f"razon de tasas ALTA/BAJA = {lift:.2f}  IC95% [{R['lift_alta_baja_ic'][0]:.2f}; "
      f"{R['lift_alta_baja_ic'][1]:.2f}]  (B = {len(lifts)})")
# CPA honesta
top5 = P.sort_values(['anio', 'lr'], ascending=[True, False]).groupby('anio').head(5)
top8 = P.sort_values(['anio', 'lr'], ascending=[True, False]).groupby('anio').head(8)
R['cpa_top5'] = round(100 * top5.h.sum() / P.h.sum(), 1); R['terr_top5'] = round(100 * 5 / 31, 1)
R['cpa_top8'] = round(100 * top8.h.sum() / P.h.sum(), 1); R['terr_top8'] = round(100 * 8 / 31, 1)
print(f"CPA con top-5: {R['cpa_top5']}% de los hechos en {R['terr_top5']}% del territorio")
print(f"CPA con top-8: {R['cpa_top8']}% de los hechos en {R['terr_top8']}% del territorio")

# ============ 5. colinealidad ============
print('\n=== factor de inflacion de varianza (panel modelable completo) ===')
X = datos[FEATS].astype(float)
X = (X - X.mean()) / X.std(ddof=0)
X = sm.add_constant(X)
vif = pd.DataFrame({'variable': FEATS,
                    'VIF': [round(variance_inflation_factor(X.values, i + 1), 2) for i in range(len(FEATS))]})
print(vif.sort_values('VIF', ascending=False).to_string(index=False))
R['vif'] = vif.set_index('variable').VIF.to_dict()

# ============ 6. binomial negativa con alfa estimado y errores agrupados ============
print('\n=== conteo: binomial negativa, alfa estimado y errores agrupados por municipio ===')
train = datos[datos.anio <= 2010]
VC = ['media_movil3', 'anios_activos_prev', 'depto_lag1']
Xc = sm.add_constant(train[VC].astype(float))
poi = sm.GLM(train.hechos, Xc, family=sm.families.Poisson()).fit()
print(f"sobredispersion de Poisson: chi2/gl = {poi.pearson_chi2 / poi.df_resid:.2f}")
nb_ml = sm.NegativeBinomial(train.hechos, Xc).fit(disp=0)
alpha = float(nb_ml.params.get('alpha', np.nan))
print(f"alfa estimado por maxima verosimilitud = {alpha:.3f}  (el cuaderno lo fija en 1,000)")
R['alpha_estimado'] = round(alpha, 3)
nb_fijo = sm.GLM(train.hechos, Xc, family=sm.families.NegativeBinomial(alpha=1.0)).fit()
nb_est = sm.GLM(train.hechos, Xc, family=sm.families.NegativeBinomial(alpha=alpha)).fit()
nb_cl = sm.GLM(train.hechos, Xc, family=sm.families.NegativeBinomial(alpha=alpha)).fit(
    cov_type='cluster', cov_kwds={'groups': train.municipio})
print(f"AIC Poisson {poi.aic:.1f} | BN alfa=1 {nb_fijo.aic:.1f} | BN alfa estimado {nb_est.aic:.1f}")
comp = pd.DataFrame({'IRR': np.exp(nb_est.params),
                     'p sin agrupar': nb_est.pvalues.round(4),
                     'p agrupado por municipio': nb_cl.pvalues.round(4),
                     'IC95 inf': np.exp(nb_cl.conf_int()[0]).round(3),
                     'IC95 sup': np.exp(nb_cl.conf_int()[1]).round(3)}).round(3)
print(comp.to_string())
R['negbin'] = comp.reset_index().to_dict('records')
R['aic'] = {'poisson': round(poi.aic, 1), 'bn_alfa1': round(nb_fijo.aic, 1), 'bn_alfa_est': round(nb_est.aic, 1)}
R['n_municipios_conglomerados'] = int(train.municipio.nunique())

json.dump(R, open(os.path.join(SALIDA, 'intervalos.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print('\nguardado en intervalos.json')
