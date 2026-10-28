"""Rastrea el origen de las cinco cifras que kpis.py trae codificadas a mano:
prec5=0.94, brier=0.298, brier_ref=0.239, aucpr=0.834, aucpr_base=0.603.
Prueba poblaciones candidatas hasta encontrar una que las produzca."""
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from xgboost import XGBClassifier

SEED = 42
datos = pd.read_csv('/home/claude/curaduria/panel_modelable.csv')
FEATS = ['lag1', 'lag2', 'lag3', 'media_movil3', 'acum_prev',
         'anios_activos_prev', 'racha_prev', 'anios_desde_ultimo', 'depto_lag1']

def lr_(): return make_pipeline(StandardScaler(), LogisticRegression(
    max_iter=1000, class_weight='balanced', random_state=SEED))
def xgb_(p): return XGBClassifier(n_estimators=300, max_depth=3, learning_rate=0.05,
    subsample=0.9, scale_pos_weight=p, random_state=SEED, eval_metric='logloss')

def rodante(ini, fin, modelo='lr', filtro=None):
    """Acumula predicciones fuera de muestra, una ventana por año."""
    R = []
    for ae in range(ini, fin + 1):
        tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
        if filtro is not None:
            te = te[filtro(te)]
        if len(te) == 0 or te.ocurrencia.nunique() < 2:
            continue
        pz = (tr.ocurrencia == 0).sum() / (tr.ocurrencia == 1).sum()
        m = lr_().fit(tr[FEATS], tr.ocurrencia) if modelo == 'lr' else xgb_(pz).fit(tr[FEATS], tr.ocurrencia)
        p = m.predict_proba(te[FEATS])[:, 1]
        R.append(pd.DataFrame({'anio': te.anio.values, 'mun': te.municipio.values,
                               'y': te.ocurrencia.values, 'h': te.hechos.values, 'p': p}))
    return pd.concat(R, ignore_index=True)

def resumen(P, et):
    pr = average_precision_score(P.y, P.p)
    return dict(poblacion=et, n=len(P), hechos=int(P.h.sum()), prev=round(P.y.mean(), 3),
                aucroc=round(roc_auc_score(P.y, P.p), 3), aucpr=round(pr, 3),
                brier=round(brier_score_loss(P.y, P.p), 3),
                brier_ref=round(P.y.mean() * (1 - P.y.mean()), 3))

print('OBJETIVO publicado:  aucpr 0,834 | aucpr_base 0,603 | brier 0,298 | brier_ref 0,239 | prec5 0,94')
print('nota: brier_ref = p(1-p) exige prevalencia 0,395 o 0,605; aucpr_base publicado = 0,603\n')

cand = []
for mod in ['lr', 'xgb']:
    cand.append(resumen(rodante(2006, 2016, mod), f'rodante 2006-2016, {mod}'))
    cand.append(resumen(rodante(2004, 2016, mod), f'rodante 2004-2016, {mod}'))
    cand.append(resumen(rodante(2011, 2016, mod), f'rodante 2011-2016, {mod}'))
    # solo municipio-años de municipios con historia previa
    cand.append(resumen(rodante(2006, 2016, mod, lambda t: t.acum_prev > 0),
                        f'rodante 2006-2016 con historia, {mod}'))
    cand.append(resumen(rodante(2004, 2016, mod, lambda t: t.acum_prev > 0),
                        f'rodante 2004-2016 con historia, {mod}'))
    cand.append(resumen(rodante(2006, 2016, mod, lambda t: t.anios_activos_prev >= 2),
                        f'rodante 2006-2016, 2+ años activos, {mod}'))
print(pd.DataFrame(cand).to_string(index=False))

# ---------- precision@5 ----------
print('\n--- precision@5 y cobertura, por modelo y periodo ---')
fil = []
for mod in ['lr', 'xgb']:
    for ini, fin in [(2006, 2016), (2011, 2016)]:
        P = rodante(ini, fin, mod)
        for k in [5, 8]:
            top = P.sort_values(['anio', 'p'], ascending=[True, False]).groupby('anio').head(k)
            fil.append(dict(modelo=mod, periodo=f'{ini}-{fin}', k=k,
                            precision_k=round(top.y.mean(), 3),
                            aciertos=f"{int(top.y.sum())}/{len(top)}",
                            cobertura_hechos=round(100 * top.h.sum() / P.h.sum(), 1),
                            territorio=round(100 * k / 31, 1)))
print(pd.DataFrame(fil).to_string(index=False))

# ---------- semaforo por terciles, cuentas reales ----------
print('\n--- semaforo: terciles del riesgo fuera de muestra (lr, rodante 2006-2016) ---')
P = rodante(2006, 2016, 'lr')
P['nivel'] = pd.qcut(P.p, 3, labels=['BAJA', 'MEDIA', 'ALTA'])
t = P.groupby('nivel', observed=True).agg(mun_anios=('y', 'size'), ocurrencias=('y', 'sum'),
                                          hechos=('h', 'sum'), tasa=('y', 'mean')).reset_index()
t['% del territorio'] = (100 * t.mun_anios / len(P)).round(1)
t['% de los hechos'] = (100 * t.hechos / P.h.sum()).round(1)
print(t.round(3).to_string(index=False))
print(f"\nkpis.py codifica a mano: BAJA 222/50/0,532 | MEDIA 100/59/0,650 | ALTA 81/123/0,790")
print(f"suma de ese cuadro: {222+100+81} municipio-años y {50+59+123} hechos")
print(f"el pool real tiene:  {len(P)} municipio-años y {int(P.h.sum())} hechos")
