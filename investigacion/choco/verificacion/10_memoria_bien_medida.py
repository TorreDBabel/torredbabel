"""La prueba que decide si nuestro hallazgo central es real o un artefacto.

Publicamos que la memoria historica no ordena los ataques de 2026 (AUC 0,337).
Pero nuestro panel contaba SOLO hechos de la era FARC, y verdata muestra que en
el Choco las FARC son el 41,8% y el ELN el 39,3%. Si la memoria mal medida no
predice, hay que ver si la memoria bien medida tampoco.
"""
import sys, os, glob, json
import pandas as pd, numpy as np
from sklearn.metrics import roc_auc_score
from scipy import stats
import itertools
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, '..', 'datos')
SALIDA = os.path.join(AQUI, 'resultados')
os.makedirs(SALIDA, exist_ok=True)

if len(sys.argv) < 2:
    raise SystemExit(
        __doc__
        + '\nUso: python '
        + os.path.basename(__file__)
        + ' <carpeta con los verdata-reclutamiento-R*.csv>\n'
        + 'La carpeta se obtiene del catalogo 795 de microdatos del DANE.'
    )
RUTA = sys.argv[1]
rng = np.random.default_rng(42)
arch = sorted(glob.glob(os.path.join(RUTA, 'verdata-reclutamiento-R*.csv')))
R = []
for a in arch:
    d = pd.read_csv(a, usecols=['replica', 'muni_code_hecho', 'dept_code_hecho',
                                'yy_hecho', 'p_str'], low_memory=False,
                    dtype={'muni_code_hecho': str, 'dept_code_hecho': str})
    R.append(d[d.dept_code_hecho == '27'])
C = pd.concat(R, ignore_index=True)

b = pd.read_csv(os.path.join(DATOS, 'base_municipal_corredor.csv'))
b['cod'] = b.cod_divipola.astype(str).str.zfill(5)
y = b.dron_2026.values.astype(int)
ATAC = b[b.dron_2026 == 1].municipio.tolist()
print(f"municipios atacados en 2026: {', '.join(sorted(ATAC))}\n")

def conteo(sub):
    s = sub.groupby(['replica', 'muni_code_hecho']).size().groupby('muni_code_hecho').mean()
    return b.cod.map(s).fillna(0.0).values

VAR = {
    'verdata, todo el periodo y todos los actores': conteo(C),
    'verdata, solo FARC': conteo(C[C.p_str == 'GUE-FARC']),
    'verdata, sin FARC (ELN, paras, otros)': conteo(C[C.p_str != 'GUE-FARC']),
    'verdata, solo ELN': conteo(C[C.p_str == 'GUE-ELN']),
    'verdata, ultimos 10 años (2008-2017)': conteo(C[C.yy_hecho >= 2008]),
    'verdata, ultimos 5 años (2013-2017)': conteo(C[C.yy_hecho >= 2013]),
    'nuestro panel (hechos era FARC)': b.farc_total.values.astype(float),
    'nuestro semaforo publicado': b.riesgo_2016.values.astype(float),
}

# permutacion exacta: C(31,6) = 736.281
n, k = len(b), int(y.sum())
pos = tuple(np.where(y == 1)[0])
def exacta(s):
    rangos = pd.Series(s).rank(method='average').values
    obs = (rangos[list(pos)].sum() - k*(k+1)/2) / (k*(n-k))
    todas = np.fromiter((rangos[list(c)].sum() for c in itertools.combinations(range(n), k)),
                        dtype=float, count=736281)
    aucs = (todas - k*(k+1)/2) / (k*(n-k))
    return obs, float((aucs >= obs).mean()), float((np.abs(aucs-0.5) >= abs(obs-0.5)).mean())

P, Ng = np.where(y == 1)[0], np.where(y == 0)[0]
def ic(s, B=10000):
    v = []
    for _ in range(B):
        ip = rng.choice(P, k, replace=True); ineg = rng.choice(Ng, n-k, replace=True)
        yy = np.r_[np.ones(k), np.zeros(n-k)]; ss = np.r_[s[ip], s[ineg]]
        if len(np.unique(ss)) > 1:
            v.append(roc_auc_score(yy, ss))
    return np.percentile(v, [2.5, 97.5])

print("=== ¿ORDENA LA MEMORIA LOS ATAQUES DE 2026, SEGUN COMO SE MIDA? ===")
print(f"{'como se mide la memoria':46} {'AUC':>6}  {'IC 95%':>16}  {'p exacta':>9}")
res = []
for et, s in VAR.items():
    auc, p1, p2 = exacta(s)
    lo, hi = ic(s)
    marca = '  <<' if lo > 0.5 else ''
    print(f"{et:46} {auc:6.3f}  [{lo:.3f}; {hi:.3f}]  {p2:9.4f}{marca}")
    res.append(dict(medida=et, auc=round(float(auc), 3), ic=[round(lo, 3), round(hi, 3)],
                    p_bilateral=round(p2, 4)))

print("\n=== LOS SEIS ATACADOS, CON LAS DOS MEDIDAS ===")
t = b[b.dron_2026 == 1][['municipio', 'farc_total', 'rank_hist', 'nivel_2016']].copy()
vd = C.groupby(['replica', 'muni_code_hecho']).size().groupby('muni_code_hecho').mean()
t['verdata'] = b[b.dron_2026 == 1].cod.map(vd).fillna(0).values
b['vd'] = b.cod.map(vd).fillna(0.0)
b['rank_vd'] = b.vd.rank(ascending=False, method='min').astype(int)
t['rank_vd'] = b[b.dron_2026 == 1].rank_vd.values
print(t.sort_values('rank_vd').to_string(index=False))
print(f"\n  de los 10 primeros por verdata, {int(b.nsmallest(10,'rank_vd').dron_2026.sum())} "
      f"de los 6 atacados")
print(f"  de los 10 primeros por nuestro panel, "
      f"{int(b.nsmallest(10,'rank_hist').dron_2026.sum())} de los 6")

json.dump(res, open(os.path.join(SALIDA, 'prueba_critica.json'), 'w'),
          indent=1, ensure_ascii=False, default=float)
print("\nguardado en prueba_critica.json")
