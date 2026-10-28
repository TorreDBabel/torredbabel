"""¿Tiene el corredor en disputa valor predictivo, o solo valor retrospectivo?

El indice publicado se construyo MIRANDO los ataques de 2026, de modo que su AUC
de 0,927 es circular. Aqui se hace lo contrario: se construye una version del
corredor que varia en el tiempo con la coca anual (UNODC, 1999-2016) y se prueba
contra el reclutamiento registrado en ESE mismo periodo, que es anterior a los
ataques y por tanto no pudo influir en la eleccion de los componentes.

Tres preguntas:
  A. ¿Ordena el corredor el reclutamiento, fuera de muestra?
  B. ¿AÑADE algo sobre el bloque de memoria historica, que ya es buen predictor?
  C. ¿Cuanto de la respuesta es la coca y cuanto la geografia?
"""
import numpy as np, pandas as pd, json, warnings
warnings.filterwarnings('ignore')
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score, average_precision_score

SEED = 42
rng = np.random.default_rng(SEED)

# ---------- 1. coca anual por municipio ----------
d = pd.read_excel('/mnt/user-data/uploads/RPT_CultivosIlicitos_2026-08-26--223513.xlsx',
                  sheet_name='CultivosIlicitos', header=8)
d = d[d['DEPARTAMENTO'].astype(str).str.contains('CHOC', na=False)].copy()
anios = [c for c in d.columns if str(c).replace('.0', '').isdigit()]
coca = d.melt(id_vars=['CODMPIO'], value_vars=anios, var_name='anio', value_name='coca')
coca['anio'] = coca.anio.astype(str).str.replace('.0', '', regex=False).astype(int)
coca['coca'] = pd.to_numeric(coca.coca, errors='coerce').fillna(0.0)
coca['cod_divipola'] = pd.to_numeric(coca.CODMPIO, errors='coerce')
coca = coca.dropna(subset=['cod_divipola'])
coca['cod_divipola'] = coca.cod_divipola.astype(int)
print(f"coca anual: {coca.anio.min()}-{coca.anio.max()}, "
      f"{coca.cod_divipola.nunique()} municipios, total {coca.coca.sum():,.0f} ha")

# ---------- 2. panel + geografia ----------
P = pd.read_csv('/home/claude/curaduria/panel_modelable.csv')
base = pd.read_csv('/home/claude/base_municipal.csv')
P = P.merge(base[['municipio', 'cod_divipola', 'd_san_juan', 'riberenidad']], on='municipio')
P = P.merge(coca[['cod_divipola', 'anio', 'coca']], on=['cod_divipola', 'anio'], how='left')
P['coca'] = P.coca.fillna(0.0)

# la coca del año ANTERIOR: nada contemporaneo
P = P.sort_values(['municipio', 'anio'])
P['coca_lag1'] = P.groupby('municipio')['coca'].shift(1)
P['coca_acum'] = P.groupby('municipio')['coca'].transform(lambda s: s.shift(1).cumsum())
P = P[(P.anio >= 2000) & (P.anio <= 2016)].dropna(subset=['coca_lag1']).copy()
print(f"panel con coca: {len(P)} municipio-año, {P.anio.min()}-{P.anio.max()}, "
      f"{int(P.ocurrencia.sum())} positivos (prevalencia {P.ocurrencia.mean():.3f})")

# ---------- 3. el corredor, año por año ----------
def pct(s):
    return s.rank(pct=True)

P['s_rio'] = 1 - pct(P.d_san_juan)                                  # estatico
P['s_coca'] = P.groupby('anio')['coca_lag1'].transform(pct)         # varia en el tiempo
P['s_coca_ac'] = P.groupby('anio')['coca_acum'].transform(pct)
# pesos del indice publicado, renormalizados sobre los dos componentes disponibles
P['corredor_t'] = 100 * (0.40 * P.s_rio + 0.35 * P.s_coca) / 0.75
P['corredor_ac'] = 100 * (0.40 * P.s_rio + 0.35 * P.s_coca_ac) / 0.75

MEM = ['lag1', 'lag2', 'lag3', 'media_movil3', 'acum_prev',
       'anios_activos_prev', 'racha_prev', 'anios_desde_ultimo', 'depto_lag1']
R = {}

def rodante(cols, ini=2006, fin=2016):
    out = []
    for ae in range(ini, fin + 1):
        tr, te = P[P.anio < ae], P[P.anio == ae]
        if len(tr) < 50 or te.ocurrencia.nunique() < 2:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(
            max_iter=2000, random_state=SEED)).fit(tr[cols], tr.ocurrencia)
        out.append(pd.DataFrame({'anio': te.anio.values, 'mun': te.municipio.values,
                                 'y': te.ocurrencia.values, 'h': te.hechos.values,
                                 'p': m.predict_proba(te[cols])[:, 1]}))
    return pd.concat(out, ignore_index=True)

def ev(Q, et):
    top5 = Q.sort_values(['anio', 'p'], ascending=[True, False]).groupby('anio').head(5)
    return dict(conjunto=et, n=len(Q), aucroc=round(roc_auc_score(Q.y, Q.p), 3),
                aucpr=round(average_precision_score(Q.y, Q.p), 3),
                prec5=round(top5.y.mean(), 3))

# ---------- A y C: ¿ordena, y quien lo hace? ----------
print('\n=== A/C. ordenamiento directo, sin modelo (todo el periodo 2000-2016) ===')
fil = []
for col, et in [('s_rio', 'Cercania al San Juan (estatica)'),
                ('s_coca', 'Coca del año anterior'),
                ('s_coca_ac', 'Coca acumulada hasta el año anterior'),
                ('corredor_t', 'Corredor con coca anual'),
                ('corredor_ac', 'Corredor con coca acumulada'),
                ('acum_prev', 'Memoria historica (referencia)')]:
    fil.append(dict(ordenamiento=et, auc=round(roc_auc_score(P.ocurrencia, P[col]), 3),
                    aucpr=round(average_precision_score(P.ocurrencia, P[col]), 3)))
T = pd.DataFrame(fil).sort_values('auc', ascending=False)
print(T.to_string(index=False))
print(f"referencia de azar del AUC-PR: {P.ocurrencia.mean():.3f}")
R['ordenamiento_directo'] = T.to_dict('records')

# ---------- B: ¿añade sobre la memoria? ----------
print('\n=== B. ¿añade el corredor sobre el bloque de memoria? (origen rodante) ===')
comb = [(MEM, 'Memoria historica sola (9 variables)'),
        (['s_rio', 's_coca'], 'Corredor solo (rio + coca anual)'),
        (MEM + ['s_rio'], 'Memoria + cercania al rio'),
        (MEM + ['s_coca'], 'Memoria + coca anual'),
        (MEM + ['s_rio', 's_coca'], 'Memoria + corredor completo')]
res = [ev(rodante(c), et) for c, et in comb]
TT = pd.DataFrame(res)
print(TT.to_string(index=False))
base_auc = TT[TT.conjunto.str.startswith('Memoria historica sola')].aucroc.iloc[0]
TT['delta_auc'] = (TT.aucroc - base_auc).round(3)
R['incremental'] = TT.to_dict('records')

# intervalo de la diferencia, por remuestreo de municipios
print('\nintervalo de la ganancia (remuestreo de bloques de municipio, B = 2.000):')
A = rodante(MEM); B = rodante(MEM + ['s_rio', 's_coca'])
J = A.merge(B, on=['anio', 'mun'], suffixes=('_a', '_b'))
MUN = J.mun.unique(); dif = []
for _ in range(2000):
    el = rng.choice(MUN, len(MUN), replace=True)
    q = pd.concat([J[J.mun == m] for m in el], ignore_index=True)
    if q.y_a.nunique() < 2:
        continue
    dif.append(roc_auc_score(q.y_b, q.p_b) - roc_auc_score(q.y_a, q.p_a))
dif = np.array(dif)
lo, hi = np.percentile(dif, [2.5, 97.5])
obs = roc_auc_score(B.y, B.p) - roc_auc_score(A.y, A.p)
print(f"  ganancia observada {obs:+.3f}  IC95% [{lo:+.3f}; {hi:+.3f}]  "
      f"| P(ganancia > 0) = {(dif > 0).mean():.2f}")
R['ganancia'] = dict(observada=round(float(obs), 3), ic=[round(float(lo), 3), round(float(hi), 3)],
                     p_positiva=round(float((dif > 0).mean()), 3))

# ---------- el corredor en el tiempo: ¿se mueve? ----------
print('\n=== ¿se mueve el corredor en el tiempo, o es casi estatico? ===')
piv = P.pivot_table(index='municipio', columns='anio', values='corredor_t')
mov = (piv.max(axis=1) - piv.min(axis=1)).sort_values(ascending=False)
print(f"recorrido del indice por municipio: mediana {mov.median():.1f} puntos, "
      f"maximo {mov.max():.1f} ({mov.index[0]})")
print('\nlos cinco que mas se mueven:')
print(mov.head(5).round(1).to_string())
R['movimiento'] = dict(mediana=round(float(mov.median()), 1), maximo=round(float(mov.max()), 1),
                       mun_max=mov.index[0])

json.dump(R, open('/home/claude/curaduria/corredor_tiempo.json', 'w'),
          indent=1, ensure_ascii=False, default=float)
print('\nguardado en corredor_tiempo.json')
