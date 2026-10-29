"""Corrige dos diagnosticos propios que estaban mal planteados:

(6) el estudio de simulacion generaba los datos con una estandarizacion y los
    estimaba con otra, de modo que el sesgo medido era mio, no del estimador;
(7) el chequeo predictivo simulaba desde las probabilidades reponderadas, que
    ya se sabe que sobrepredicen 2,3 veces: el fallo estaba garantizado.

Aqui el diseño generador y el estimado son identicos, y el chequeo se hace
sobre el modelo sin reponderar y sobre el recalibrado."""
import numpy as np, pandas as pd, json, warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score
import statsmodels.api as sm
import statsmodels.formula.api as smf
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

# ============ 6. simulacion con diseño identico al estimado ============
# y_it ~ Bernoulli(logit^-1( b0 + u_i + b1 * 1[y_i,t-1 > 0] )),  u_i ~ N(0, s^2)
# Se estima exactamente  y ~ lag1 .  Sin reescalados: nada que desalinear.
B0, B1, S_U = -2.0, 1.2, 0.8
N_MUN, N_ANIOS = 31, 34

def simular(semilla):
    r = np.random.default_rng(semilla)
    u = r.normal(0, S_U, N_MUN)
    Y = np.zeros((N_MUN, N_ANIOS), int)
    p0 = 1 / (1 + np.exp(-(B0 + u)))
    Y[:, 0] = r.binomial(1, p0)
    for t in range(1, N_ANIOS):
        eta = B0 + u + B1 * Y[:, t - 1]
        Y[:, t] = r.binomial(1, 1 / (1 + np.exp(-eta)))
    f = [dict(mun=i, y=Y[i, t], lag1=Y[i, t - 1]) for i in range(N_MUN) for t in range(1, N_ANIOS)]
    return pd.DataFrame(f)

print('=== 6. estudio de simulacion, diseño generador = diseño estimado ===')
print(f"verdad: b0 = {B0}, b1 = {B1}, sd del intercepto aleatorio = {S_U}")
print(f"panel: {N_MUN} municipios x {N_ANIOS} años\n")
E = []
for s in range(600):
    d = simular(7000 + s)
    try:
        m = smf.glm('y ~ lag1', data=d, family=sm.families.Binomial()).fit()
        mc = smf.glm('y ~ lag1', data=d, family=sm.families.Binomial()).fit(
            cov_type='cluster', cov_kwds={'groups': d.mun})
        mm = sm.BinomialBayesMixedGLM.from_formula(
            'y ~ lag1', {'mun': '0 + C(mun)'}, d).fit_vb(verbose=False)
        E.append(dict(b=m.params['lag1'], ee_iid=m.bse['lag1'], ee_cl=mc.bse['lag1'],
                      cub_iid=abs(m.params['lag1'] - B1) <= 1.96 * m.bse['lag1'],
                      cub_cl=abs(m.params['lag1'] - B1) <= 1.96 * mc.bse['lag1'],
                      b_mix=mm.fe_mean[1], sd_mix=float(np.exp(mm.vcp_mean[0])),
                      tasa=d.y.mean()))
    except Exception:
        pass
E = pd.DataFrame(E)
fil = [
    dict(cantidad='tasa de ocurrencia simulada', valor=round(float(E.tasa.mean()), 3),
         nota=f'la real del panel es {datos.ocurrencia.mean():.3f}'),
    dict(cantidad='b1 estimado, logística agrupada', valor=round(float(E.b.mean()), 3),
         nota=f'verdad {B1}; sesgo {E.b.mean()-B1:+.3f}'),
    dict(cantidad='desviación empírica de b1', valor=round(float(E.b.std()), 3), nota='la dispersión real'),
    dict(cantidad='EE medio que supone filas independientes', valor=round(float(E.ee_iid.mean()), 3),
         nota=f'cobertura del IC95: {100*E.cub_iid.mean():.1f}%'),
    dict(cantidad='EE medio agrupado por municipio', valor=round(float(E.ee_cl.mean()), 3),
         nota=f'cobertura del IC95: {100*E.cub_cl.mean():.1f}%'),
    dict(cantidad='b1 estimado, jerárquico bayesiano', valor=round(float(E.b_mix.mean()), 3),
         nota=f'sesgo {E.b_mix.mean()-B1:+.3f}'),
    dict(cantidad='sd del intercepto aleatorio recuperada', valor=round(float(E.sd_mix.mean()), 3),
         nota=f'verdad {S_U}'),
]
print(pd.DataFrame(fil).to_string(index=False))
print(f"\nréplicas útiles: {len(E)} de 600")
R['simulacion'] = dict(replicas=len(E), b1_verdadero=B1, sd_verdadero=S_U,
                       b1_agrupada=round(float(E.b.mean()), 3),
                       sesgo_agrupada=round(float(E.b.mean() - B1), 3),
                       sd_empirica=round(float(E.b.std()), 3),
                       ee_iid=round(float(E.ee_iid.mean()), 3),
                       ee_cluster=round(float(E.ee_cl.mean()), 3),
                       cobertura_iid=round(100 * float(E.cub_iid.mean()), 1),
                       cobertura_cluster=round(100 * float(E.cub_cl.mean()), 1),
                       b1_mixto=round(float(E.b_mix.mean()), 3),
                       sesgo_mixto=round(float(E.b_mix.mean() - B1), 3),
                       sd_recuperada=round(float(E.sd_mix.mean()), 3),
                       tasa_simulada=round(float(E.tasa.mean()), 3))

# ============ 7. chequeo predictivo sobre el modelo bien calibrado ============
print('\n=== 7. chequeo predictivo, ahora sobre probabilidades calibradas ===')
P = []
for ae in range(2006, 2017):
    tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
    m = make_pipeline(StandardScaler(), LogisticRegression(
        max_iter=2000, random_state=SEED)).fit(tr[FEATS], tr.ocurrencia)   # sin reponderar
    P.append(pd.DataFrame({'anio': te.anio.values, 'mun': te.municipio.values,
                           'y': te.ocurrencia.values, 'p': m.predict_proba(te[FEATS])[:, 1]}))
P = pd.concat(P, ignore_index=True)
ini, fin = P[P.anio <= 2011], P[P.anio > 2011]
iso = IsotonicRegression(out_of_bounds='clip').fit(ini.p, ini.y)
fin = fin.assign(p_cal=iso.transform(fin.p))

def chequeo(D, col, et, B=2000):
    S = rng.random((B, len(D))) < D[col].values
    pruebas = [
        ('total de ocurrencias', lambda m: m.sum()),
        ('máximo de municipios activos en un año',
         lambda m: pd.DataFrame({'a': D.anio.values, 'y': m}).groupby('a').y.sum().max()),
        ('municipios sin ninguna ocurrencia',
         lambda m: int((pd.DataFrame({'g': D['mun'].values, 'y': m}).groupby('g').y.sum() == 0).sum())),
        ('años consecutivos con ocurrencia (rachas)',
         lambda m: int(pd.DataFrame({'g': D['mun'].values, 'a': D.anio.values, 'y': m})
                       .sort_values(['g', 'a']).groupby('g').y
                       .apply(lambda s: ((s == 1) & (s.shift(1) == 1)).sum()).sum())),
    ]
    out = []
    for nom, fn in pruebas:
        d = np.array([fn(s) for s in S], float)
        o = float(fn(D.y.values))
        p = float(np.mean(d >= o))
        out.append(dict(modelo=et, rasgo=nom, observado=round(o, 1),
                        simulado=round(float(d.mean()), 1), p_predictivo=round(p, 3),
                        veredicto='reproducido' if 0.05 <= p <= 0.95 else 'NO reproducido'))
    return out

res = chequeo(fin, 'p', 'logística sin reponderar') + chequeo(fin, 'p_cal', 'la misma, recalibrada')
print(pd.DataFrame(res).to_string(index=False))
print('\nventana: 2012-2016, 155 municipio-año. La recalibracion isotonica se ajusto en 2006-2011.')
R['chequeo_predictivo'] = res

json.dump(R, open(os.path.join(SALIDA, 'correccion.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print('\nguardado en correccion.json')
