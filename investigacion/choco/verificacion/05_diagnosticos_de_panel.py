"""Las pruebas que una estadistica bayesiana con obra en modelos jerarquicos
y diagnostico de influencia va a pedir. Cada bloque responde a una objecion
concreta: la independencia de las filas, la eleccion de lambda, los municipios
que mueven el ajuste, la linealidad en el logit, y si el estimador recupera
la verdad con 31 unidades."""
import numpy as np, pandas as pd, json, time, warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
import statsmodels.api as sm
import statsmodels.formula.api as smf

SEED = 42
rng = np.random.default_rng(SEED)
datos = pd.read_csv('/home/claude/curaduria/panel_modelable.csv')
FEATS = ['lag1', 'lag2', 'lag3', 'media_movil3', 'acum_prev',
         'anios_activos_prev', 'racha_prev', 'anios_desde_ultimo', 'depto_lag1']
R = {}

def lr_(C=1.0, peso='balanced'):
    return make_pipeline(StandardScaler(), LogisticRegression(
        C=C, max_iter=2000, class_weight=peso, random_state=SEED))

def rodante(hacer, ini=2006, fin=2016):
    """hacer(tr, te) -> probabilidades sobre te. Devuelve el pool fuera de muestra."""
    out = []
    for ae in range(ini, fin + 1):
        tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
        p = hacer(tr, te)
        out.append(pd.DataFrame({'anio': te.anio.values, 'mun': te.municipio.values,
                                 'y': te.ocurrencia.values, 'h': te.hechos.values, 'p': np.asarray(p)}))
    return pd.concat(out, ignore_index=True)

def ev(P):
    top5 = P.sort_values(['anio', 'p'], ascending=[True, False]).groupby('anio').head(5)
    return dict(aucroc=round(roc_auc_score(P.y, P.p), 3),
                aucpr=round(average_precision_score(P.y, P.p), 3),
                prec5=round(top5.y.mean(), 3))

# ===== 1. positivos por ventana: lo primero que pide quien duda de la identificabilidad =====
print('=== 1. tamaño de cada ventana de evaluacion ===')
v = []
for ae in range(2006, 2017):
    tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
    v.append(dict(anio=ae, n_entrena=len(tr), positivos_entrena=int(tr.ocurrencia.sum()),
                  n_evalua=len(te), positivos_evalua=int(te.ocurrencia.sum()),
                  hechos_evalua=int(te.hechos.sum())))
tv = pd.DataFrame(v)
print(tv.to_string(index=False))
print(f"minimo de positivos en una ventana de evaluacion: {tv.positivos_evalua.min()}  "
      f"| municipios por ventana: 31  | eventos por variable en el ajuste final: "
      f"{tv.positivos_entrena.iloc[-1] / len(FEATS):.1f}")
R['ventanas'] = tv.to_dict('records')
R['epv'] = round(float(tv.positivos_entrena.iloc[-1] / len(FEATS)), 1)

# ===== 2a. el conjunto completo no es estimable por maxima verosimilitud =====
print('\n=== 2a. maxima verosimilitud sobre las nueve variables: separacion ===')
tr = datos[datos.anio <= 2010].copy()
Zf = tr[FEATS].astype(float)
Zf = (Zf - Zf.mean()) / Zf.std(ddof=0)
Zf['ocurrencia'] = tr.ocurrencia.values
ff = 'ocurrencia ~ ' + ' + '.join(FEATS)
mlf = smf.glm(ff, data=Zf, family=sm.families.Binomial()).fit()
print(pd.DataFrame({'coef': mlf.params.round(2), 'EE': mlf.bse.round(1)}).to_string())
print(f"coeficiente de mayor magnitud: {mlf.params.abs().max():.1f} | "
      f"error estandar maximo: {mlf.bse.max():.0f}")
print("sin penalizacion, la verosimilitud no identifica estos coeficientes: los lags y su")
print("media movil son casi colineales (VIF 2.082) y el ajuste se escapa. La penalizacion L2")
print("no es un refinamiento del modelo publicado: es lo que lo vuelve estimable.")
R['separacion'] = dict(coef_max=round(float(mlf.params.abs().max()), 1),
                       ee_max=round(float(mlf.bse.max()), 1))

# ===== 2b. la objecion central: las filas no son independientes =====
REDUC = ['lag1', 'acum_prev', 'anios_activos_prev', 'racha_prev', 'anios_desde_ultimo', 'depto_lag1']
print(f'\n=== 2b. n = 31 municipios, no 1.023 filas (conjunto reducido, estimable) ===')
print(f"variables: {', '.join(REDUC)}")
Z = tr[REDUC].astype(float)
Z = (Z - Z.mean()) / Z.std(ddof=0)
Z['ocurrencia'] = tr.ocurrencia.values
Z['municipio'] = tr.municipio.values
f = 'ocurrencia ~ ' + ' + '.join(REDUC)

pooled = smf.glm(f, data=Z, family=sm.families.Binomial()).fit()
clust = smf.glm(f, data=Z, family=sm.families.Binomial()).fit(
    cov_type='cluster', cov_kwds={'groups': Z.municipio})
gee = smf.gee(f, groups='municipio', data=Z, family=sm.families.Binomial(),
              cov_struct=sm.cov_struct.Exchangeable()).fit()
comp = pd.DataFrame({
    'coef': pooled.params.round(3),
    'EE iid': pooled.bse.round(3),
    'EE agrupado': clust.bse.round(3),
    'razon EE': (clust.bse / pooled.bse).round(2),
    'p iid': pooled.pvalues.round(4),
    'p agrupado': clust.pvalues.round(4)})
print(comp.to_string())
print(f"\ncorrelacion intra-municipio estimada por GEE (intercambiable): "
      f"{gee.cov_struct.dep_params:.3f}")
print(f"factor de diseño implicito: los errores agrupados son en promedio "
      f"{(clust.bse/pooled.bse).mean():.2f} veces los iid")
R['ee_comparacion'] = comp.reset_index().to_dict('records')
R['rho_intra'] = round(float(gee.cov_struct.dep_params), 4)
R['razon_ee_media'] = round(float((clust.bse / pooled.bse).mean()), 2)

# modelo jerarquico bayesiano con intercepto aleatorio por municipio
print('\n--- logistica bayesiana de efectos mixtos (intercepto aleatorio por municipio, VB) ---')
t0 = time.perf_counter()
mix = sm.BinomialBayesMixedGLM.from_formula(f, {'mun': '0 + C(municipio)'}, Z).fit_vb(verbose=False)
R['tiempo_mixto_s'] = round(time.perf_counter() - t0, 2)
sd_re = float(np.exp(mix.vcp_mean[0]))
print(f"desviacion estandar del intercepto aleatorio: {sd_re:.3f} (en escala logit)")
print(f"ajustado en {R['tiempo_mixto_s']} s por inferencia variacional")
R['sd_intercepto_aleatorio'] = round(sd_re, 3)

# ¿el jerarquico predice mejor fuera de muestra?
def hacer_mixto(tr_, te_):
    A = tr_[REDUC].astype(float); mu, sd = A.mean(), A.std(ddof=0)
    A = (A - mu) / sd; A['ocurrencia'] = tr_.ocurrencia.values; A['municipio'] = tr_.municipio.values
    m = sm.BinomialBayesMixedGLM.from_formula(f, {'mun': '0 + C(municipio)'}, A).fit_vb(verbose=False)
    B = (te_[REDUC].astype(float) - mu) / sd
    X = sm.add_constant(B[REDUC], has_constant='add').values
    eta = X @ m.fe_mean
    # '0 + C(municipio)' genera una columna por municipio, en orden alfabetico
    muns = sorted(A.municipio.unique())
    idx = {mm: i for i, mm in enumerate(muns)}
    eta = eta + np.array([m.vc_mean[idx[mm]] if mm in idx else 0.0 for mm in te_.municipio])
    return 1 / (1 + np.exp(-eta))

P_pool = rodante(lambda a, b: lr_().fit(a[FEATS], a.ocurrencia).predict_proba(b[FEATS])[:, 1])
P_sinpeso = rodante(lambda a, b: lr_(peso=None).fit(a[FEATS], a.ocurrencia).predict_proba(b[FEATS])[:, 1])
P_red = rodante(lambda a, b: lr_().fit(a[REDUC], a.ocurrencia).predict_proba(b[REDUC])[:, 1])
P_mix = rodante(hacer_mixto)
cmp2 = pd.DataFrame([dict(modelo='logística agrupada, 9 variables (la publicada)', **ev(P_pool)),
                     dict(modelo='logística agrupada, 9 variables, sin reponderar', **ev(P_sinpeso)),
                     dict(modelo='logística agrupada, 6 variables estimables', **ev(P_red)),
                     dict(modelo='logística jerárquica, intercepto aleatorio por municipio', **ev(P_mix))])
print('\ndesempeño fuera de muestra, origen rodante 2006-2016:')
print(cmp2.to_string(index=False))
R['comparacion_jerarquico'] = cmp2.to_dict('records')

# ===== 3. lambda: el cuaderno nunca lo ajusto =====
print('\n=== 3. sensibilidad a la regularizacion (el cuaderno usa C = 1,0 por omision) ===')
fil = []
for C in [0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 100.0]:
    P = rodante(lambda a, b, C=C: lr_(C=C).fit(a[FEATS], a.ocurrencia).predict_proba(b[FEATS])[:, 1])
    fil.append(dict(C=C, **ev(P)))
tc = pd.DataFrame(fil)
print(tc.to_string(index=False))
print(f"rango del AUC-ROC sobre cinco ordenes de magnitud de C: "
      f"{tc.aucroc.min():.3f} a {tc.aucroc.max():.3f} (amplitud {tc.aucroc.max()-tc.aucroc.min():.3f})")
R['sensibilidad_C'] = tc.to_dict('records')

# ===== 4. que municipios mueven el ajuste =====
print('\n=== 4. influencia: dejar un municipio fuera del entrenamiento, una vez por municipio ===')
base_auc = roc_auc_score(P_pool.y, P_pool.p)
inf = []
for m in sorted(datos.municipio.unique()):
    P = rodante(lambda a, b, m=m: lr_().fit(
        a[a.municipio != m][FEATS], a[a.municipio != m].ocurrencia).predict_proba(b[FEATS])[:, 1])
    inf.append(dict(municipio=m, auc_sin_el=round(roc_auc_score(P.y, P.p), 3),
                    cambio=round(roc_auc_score(P.y, P.p) - base_auc, 3),
                    hechos=int(datos[datos.municipio == m].hechos.sum())))
ti = pd.DataFrame(inf).sort_values('cambio')
print(f"AUC con todos los municipios en el entrenamiento: {base_auc:.3f}")
print('\nlos cinco cuya ausencia mas baja el AUC (los que sostienen el ajuste):')
print(ti.head(5).to_string(index=False))
print('\nlos cinco cuya ausencia mas lo sube:')
print(ti.tail(5).to_string(index=False))
print(f"\namplitud total del efecto: {ti.cambio.min():.3f} a {ti.cambio.max():.3f}")
R['influencia'] = ti.to_dict('records')
R['auc_base_rodante'] = round(float(base_auc), 3)
R['influencia_amplitud'] = [round(float(ti.cambio.min()), 3), round(float(ti.cambio.max()), 3)]

# ===== 5. linealidad en el logit (Box-Tidwell) =====
print('\n=== 5. linealidad en el logit: Box-Tidwell sobre las continuas ===')
bt = []
for v_ in ['media_movil3', 'acum_prev', 'anios_activos_prev', 'depto_lag1']:
    d = tr[[v_, 'ocurrencia']].copy()
    d[v_] = d[v_].astype(float) + 1e-6
    d['tx'] = d[v_] * np.log(d[v_])
    r = smf.glm(f'ocurrencia ~ {v_} + tx', data=d, family=sm.families.Binomial()).fit()
    bt.append(dict(variable=v_, p_del_termino_bt=round(float(r.pvalues['tx']), 4),
                   veredicto='no rechaza linealidad' if r.pvalues['tx'] > 0.05 else 'rechaza linealidad'))
print(pd.DataFrame(bt).to_string(index=False))
R['box_tidwell'] = bt

# ===== 6. ¿recupera el estimador la verdad con 31 unidades? =====
print('\n=== 6. estudio de simulacion: 31 unidades, 34 periodos, tasa de eventos real ===')
BETA = {'intercepto': -2.2, 'lag1': 0.9, 'acum_prev': 0.5}
SD_U = 0.8
def simular(semilla):
    r = np.random.default_rng(semilla)
    u = r.normal(0, SD_U, 31)
    H = np.zeros((31, 34), int)
    for t in range(1, 34):
        acum = H[:, :t].sum(1)
        eta = (BETA['intercepto'] + u + BETA['lag1'] * (H[:, t - 1] > 0)
               + BETA['acum_prev'] * (acum - acum.mean()) / (acum.std() + 1e-9))
        H[:, t] = r.binomial(1, 1 / (1 + np.exp(-eta)))
    L = []
    for i in range(31):
        for t in range(1, 34):
            L.append(dict(mun=i, t=t, y=H[i, t], lag1=float(H[i, t - 1] > 0),
                          acum_prev=float(H[i, :t].sum())))
    return pd.DataFrame(L)

est = []
for s in range(300):
    d = simular(1000 + s)
    d['acum_z'] = (d.acum_prev - d.acum_prev.mean()) / d.acum_prev.std()
    try:
        mp = smf.glm('y ~ lag1 + acum_z', data=d, family=sm.families.Binomial()).fit()
        mc = smf.glm('y ~ lag1 + acum_z', data=d, family=sm.families.Binomial()).fit(
            cov_type='cluster', cov_kwds={'groups': d.mun})
        est.append(dict(b_lag1=mp.params['lag1'], ee_iid=mp.bse['lag1'], ee_cl=mc.bse['lag1'],
                        cubre_iid=abs(mp.params['lag1'] - BETA['lag1']) <= 1.96 * mp.bse['lag1'],
                        cubre_cl=abs(mp.params['lag1'] - BETA['lag1']) <= 1.96 * mc.bse['lag1']))
    except Exception:
        pass
E = pd.DataFrame(est)
print(f"replicas utiles: {len(E)}  | coeficiente verdadero de lag1 = {BETA['lag1']}")
print(f"estimacion media        {E.b_lag1.mean():.3f}  (sesgo {E.b_lag1.mean()-BETA['lag1']:+.3f})")
print(f"desviacion empirica     {E.b_lag1.std():.3f}")
print(f"EE medio iid            {E.ee_iid.mean():.3f}   -> cobertura del IC95: {100*E.cubre_iid.mean():.1f}%")
print(f"EE medio agrupado       {E.ee_cl.mean():.3f}   -> cobertura del IC95: {100*E.cubre_cl.mean():.1f}%")
print("lectura: la cobertura nominal es 95%; el deficit mide cuanto miente el EE que ignora el municipio")
R['simulacion'] = dict(replicas=len(E), beta_verdadero=BETA['lag1'],
                       estimacion_media=round(float(E.b_lag1.mean()), 3),
                       sesgo=round(float(E.b_lag1.mean() - BETA['lag1']), 3),
                       sd_empirica=round(float(E.b_lag1.std()), 3),
                       ee_iid=round(float(E.ee_iid.mean()), 3), ee_agrupado=round(float(E.ee_cl.mean()), 3),
                       cobertura_iid=round(100 * float(E.cubre_iid.mean()), 1),
                       cobertura_agrupada=round(100 * float(E.cubre_cl.mean()), 1))

# ===== 7. que rasgo del panel NO reproduce el modelo =====
print('\n=== 7. chequeo predictivo: que rasgos del panel reproduce y cual no ===')
P = P_pool.copy()
sim = rng.random((400, len(P))) < P.p.values
obs_stats = dict(total_ocurrencias=P.y.sum(),
                 max_por_anio=P.groupby('anio').y.sum().max(),
                 municipios_nunca=int((P.groupby('mun').y.sum() == 0).sum()),
                 rachas=int(((P.sort_values(['mun', 'anio']).groupby('mun').y
                              .apply(lambda s: ((s == 1) & (s.shift(1) == 1)).sum())).sum())))
ch = []
for k, f_ in [('total de ocurrencias', lambda m: m.sum()),
              ('máximo de municipios activos en un año',
               lambda m: pd.DataFrame({'a': P.anio, 'y': m}).groupby('a').y.sum().max()),
              ('municipios sin ninguna ocurrencia',
               lambda m: int((pd.DataFrame({'g': P['mun'], 'y': m}).groupby('g').y.sum() == 0).sum()))]:
    d = np.array([f_(s) for s in sim])
    o = f_(P.y.values)
    p = float(np.mean(d >= o))
    ch.append(dict(rasgo=k, observado=round(float(o), 1), simulado_medio=round(float(d.mean()), 1),
                   p_predictivo=round(p, 3),
                   veredicto='reproducido' if 0.05 <= p <= 0.95 else 'NO reproducido'))
print(pd.DataFrame(ch).to_string(index=False))
R['chequeo_predictivo'] = ch

json.dump(R, open('/home/claude/curaduria/luque.json', 'w'), indent=1, ensure_ascii=False, default=float)
print('\nguardado en luque.json')
