"""Matriz de confusion de las alarmas y concordancia con la Defensoria del Pueblo.

Dos preguntas distintas:
  A. Si el modelo enciende una alarma, ¿acierta? -> matriz de confusion contra la
     ocurrencia real, fuera de muestra, a tres umbrales declarados.
  B. ¿Coincide con quien ya advierte? -> contraste con las alertas tempranas de la
     Defensoria. Ojo: 30 de 31 municipios tienen alerta, de modo que la coincidencia
     binaria es degenerada y hay que comparar INTENSIDADES y ordenamientos.
"""
import numpy as np, pandas as pd, json, itertools, warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.isotonic import IsotonicRegression
from scipy import stats

SEED = 42
rng = np.random.default_rng(SEED)
datos = pd.read_csv('/home/claude/curaduria/panel_modelable.csv')
FEATS = ['lag1','lag2','lag3','media_movil3','acum_prev',
         'anios_activos_prev','racha_prev','anios_desde_ultimo','depto_lag1']
R = {}

# ---------- pool fuera de muestra, sin reponderar (calibrado) ----------
P = []
for ae in range(2006, 2017):
    tr, te = datos[datos.anio < ae], datos[datos.anio == ae]
    m = make_pipeline(StandardScaler(),
                      LogisticRegression(max_iter=2000, random_state=SEED)
                      ).fit(tr[FEATS], tr.ocurrencia)
    P.append(pd.DataFrame({'anio': te.anio.values, 'mun': te.municipio.values,
                           'y': te.ocurrencia.values, 'h': te.hechos.values,
                           'p': m.predict_proba(te[FEATS])[:, 1]}))
P = pd.concat(P, ignore_index=True)
# recalibracion isotonica honesta: se ajusta con 2006-2011, se aplica a 2012-2016
iso = IsotonicRegression(out_of_bounds='clip').fit(P[P.anio <= 2011].p, P[P.anio <= 2011].y)
P['pc'] = np.where(P.anio <= 2011, P.p, iso.transform(P.p))

def matriz(y, a):
    y = np.asarray(y).astype(bool); a = np.asarray(a).astype(bool)
    VP = int((y & a).sum()); FP = int((~y & a).sum())
    FN = int((y & ~a).sum()); VN = int((~y & ~a).sum())
    prec = VP / (VP + FP) if VP + FP else np.nan
    sens = VP / (VP + FN) if VP + FN else np.nan
    espe = VN / (VN + FP) if VN + FP else np.nan
    f1 = 2 * prec * sens / (prec + sens) if prec and sens else np.nan
    return dict(VP=VP, FP=FP, FN=FN, VN=VN, precision=prec, sensibilidad=sens,
                especificidad=espe, f1=f1, encendidas=VP + FP,
                pct_encendidas=100 * (VP + FP) / len(y))

# ---------- A. tres politicas de alarma ----------
print('=== A. MATRIZ DE CONFUSION DE LAS ALARMAS ===')
print(f"pool fuera de muestra: {len(P)} municipio-año, {int(P.y.sum())} con reclutamiento "
      f"registrado (prevalencia {P.y.mean():.3f})\n")

pol = {}
# 1. tercil superior del riesgo (el semaforo ALTA)
u_ter = P.p.quantile(2/3)
pol['Semáforo en ALTA (tercil superior)'] = (P.p >= u_ter).values
# 2. los cinco de mayor riesgo cada año
top5 = P.sort_values(['anio','p'], ascending=[True,False]).groupby('anio').head(5).index
pol['Los 5 de mayor riesgo cada año'] = P.index.isin(top5)
# 3. probabilidad calibrada por encima de la prevalencia
pol['Probabilidad calibrada ≥ 0,33 (la prevalencia)'] = (P.pc >= P.y.mean()).values

fil = []
for nom, a in pol.items():
    m = matriz(P.y, a)
    fil.append(dict(politica=nom, **m))
T = pd.DataFrame(fil)
print(T[['politica','VP','FP','FN','VN','encendidas','pct_encendidas']].round(1).to_string(index=False))
print()
print(T[['politica','precision','sensibilidad','especificidad','f1']].round(3).to_string(index=False))
R['politicas'] = T.to_dict('records')

# intervalos por remuestreo de municipios
MUN = P.mun.unique()
print('\nintervalos del 95 % (remuestreo de bloques de municipio, B = 2.000):')
ic_out = []
for nom, a in pol.items():
    P2 = P.assign(a=a)
    acc = {k: [] for k in ['precision','sensibilidad','especificidad']}
    for _ in range(2000):
        el = rng.choice(MUN, len(MUN), replace=True)
        d = pd.concat([P2[P2.mun == mm] for mm in el], ignore_index=True)
        m = matriz(d.y, d.a)
        for k in acc: acc[k].append(m[k])
    row = {'politica': nom}
    for k in acc:
        v = np.array(acc[k], float); v = v[~np.isnan(v)]
        row[k] = f"{np.percentile(v,2.5):.3f} – {np.percentile(v,97.5):.3f}"
    ic_out.append(row)
print(pd.DataFrame(ic_out).to_string(index=False))
R['politicas_ic'] = ic_out

# cuanto daño queda fuera
for nom, a in pol.items():
    cub = P[a].h.sum() / P.h.sum()
    print(f"  {nom}: cubre {100*cub:.1f} % de los {int(P.h.sum())} hechos")
    R.setdefault('cobertura_politica', {})[nom] = round(100 * float(cub), 1)

# ---------- B. concordancia con la Defensoria ----------
print('\n\n=== B. CONCORDANCIA CON LAS ALERTAS DE LA DEFENSORIA ===')
b = pd.read_csv('/home/claude/base_drones.csv')
print(f"municipios con al menos una alerta temprana: {int((b.alertas>0).sum())} de {len(b)}")
print(f"municipios con alerta de inminencia:          {int((b.inminencia>0).sum())} de {len(b)}")
print("\nla coincidencia binaria es degenerada: la Defensoria advirtio casi todo el")
print("departamento, que es lo correcto desde su mandato. La pregunta util es otra:")
print("dado que casi todo esta advertido, ¿coinciden los ORDENAMIENTOS?\n")
R['mun_con_alerta'] = int((b.alertas > 0).sum())
R['mun_con_inminencia'] = int((b.inminencia > 0).sum())
R['n_mun'] = len(b)

# correlaciones de rango
fil = []
for col, et in [('alertas','Alertas tempranas (0–8)'),
                ('inminencia','Alertas de inminencia (0–3)'),
                ('estructurales','Alertas estructurales (0–6)')]:
    rho, p = stats.spearmanr(b.riesgo_2016, b[col])
    fil.append(dict(serie_defensoria=et, rho_spearman=round(float(rho),3),
                    p=round(float(p),4),
                    veredicto='concuerda' if p < 0.05 else 'no distinguible del azar'))
print(pd.DataFrame(fil).to_string(index=False))
R['spearman_defensoria'] = fil

# 2x2 entre los diez primeros de cada ordenamiento, prueba exacta de Fisher
print('\ncoincidencia entre los diez primeros de cada ordenamiento:')
fil = []
for col, et in [('alertas','alertas tempranas'), ('inminencia','alertas de inminencia')]:
    nuestro = set(b.nlargest(10,'riesgo_2016').municipio)
    suyo = set(b.nlargest(10, col).municipio)
    a11 = len(nuestro & suyo); a10 = len(nuestro - suyo)
    a01 = len(suyo - nuestro); a00 = len(b) - a11 - a10 - a01
    odds, pf = stats.fisher_exact([[a11, a10],[a01, a00]], alternative='greater')
    fil.append(dict(serie=et, coinciden=a11, solo_modelo=a10, solo_defensoria=a01,
                    ninguno=a00, p_fisher=round(float(pf),4),
                    esperado_azar=round(10*10/len(b),1)))
print(pd.DataFrame(fil).to_string(index=False))
R['fisher_top10'] = fil

# los seis atacados
d6 = b[b.dron_2026 == 1]
print(f"\nlos seis municipios atacados en 2026:")
print(d6[['municipio','alertas','inminencia','rank_hist','nivel_2016']]
      .sort_values('alertas', ascending=False).to_string(index=False))
print(f"  con alerta temprana previa: {int((d6.alertas>0).sum())} de 6")
print(f"  con alerta de inminencia:   {int((d6.inminencia>0).sum())} de 6")
print(f"  media de alertas, atacados {d6.alertas.mean():.2f} | resto {b[b.dron_2026==0].alertas.mean():.2f}")
u, pu = stats.mannwhitneyu(d6.alertas, b[b.dron_2026==0].alertas, alternative='two-sided')
print(f"  U de Mann-Whitney sobre el numero de alertas: p = {pu:.3f}")
R['atacados_defensoria'] = dict(
    con_alerta=int((d6.alertas>0).sum()), con_inminencia=int((d6.inminencia>0).sum()),
    media_atacados=round(float(d6.alertas.mean()),2),
    media_resto=round(float(b[b.dron_2026==0].alertas.mean()),2),
    p_mannwhitney=round(float(pu),3))

json.dump(R, open('/home/claude/curaduria/alarmas.json','w'), indent=1, ensure_ascii=False, default=float)
print('\nguardado en alarmas.json')
