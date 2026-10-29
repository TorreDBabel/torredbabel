"""¿Sirve verdata para nuestro trabajo? Tres preguntas concretas.
Combina las 100 replicas como corresponde: se calcula en cada una y se resume
la distribucion entre replicas, que es la incertidumbre de lo imputado."""
import sys, os, glob, json
import pandas as pd, numpy as np
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
arch = sorted(glob.glob(os.path.join(RUTA, 'verdata-reclutamiento-R*.csv')))
USA = ['replica', 'match_group_id', 'muni_code_hecho', 'muni_code_hecho_imputed',
       'dept_code_hecho', 'yy_hecho', 'edad_jep', 'p_str', 'sexo', 'etnia']
FUENTES = ['in_%d' % i for i in range(1, 35)]

print(f"leyendo {len(arch)} replicas...")
R = []
for a in arch:
    d = pd.read_csv(a, usecols=USA + FUENTES, low_memory=False,
                    dtype={'muni_code_hecho': str, 'dept_code_hecho': str})
    d['n_fuentes'] = d[FUENTES].sum(axis=1)
    R.append(d.drop(columns=FUENTES))
D = pd.concat(R, ignore_index=True)
nrep = D.replica.nunique()
print(f"total {len(D):,} filas = {nrep} replicas x ~{len(D)//nrep:,} victimas\n")

def entre_replicas(serie_por_replica, et, fmt='{:,.0f}'):
    v = np.asarray(serie_por_replica, float)
    print(f"  {et:46} {fmt.format(v.mean())}   "
          f"[{fmt.format(np.percentile(v,2.5))} – {fmt.format(np.percentile(v,97.5))}]")
    return dict(media=float(v.mean()), lo=float(np.percentile(v, 2.5)),
                hi=float(np.percentile(v, 97.5)))

S = {}
print("=== COBERTURA GENERAL (media entre replicas, con rango del 95%) ===")
g = D.groupby('replica')
S['victimas'] = entre_replicas(g.size(), 'victimas unicas registradas, total nacional')
S['municipios'] = entre_replicas(g.muni_code_hecho.nunique(), 'municipios con al menos una victima')
print(f"\n  periodo cubierto: {int(D.yy_hecho.min())}–{int(D.yy_hecho.max())}")
print(f"  departamentos: {D.dept_code_hecho.nunique()}")
S['anio_min'] = int(D.yy_hecho.min()); S['anio_max'] = int(D.yy_hecho.max())

print("\n=== QUE TANTO SE IMPUTO ===")
pm = g.apply(lambda x: (x.muni_code_hecho_imputed.astype(str) == 'True').mean() * 100)
S['muni_imputado'] = entre_replicas(pm, 'municipio del hecho imputado (%)', '{:.1f}%')

print("\n=== EL CHOCO (codigo 27) ===")
C = D[D.dept_code_hecho == '27']
gc = C.groupby('replica')
S['choco_victimas'] = entre_replicas(gc.size(), 'victimas en el Choco')
S['choco_municipios'] = entre_replicas(gc.muni_code_hecho.nunique(), 'municipios del Choco con registro')
pmc = gc.apply(lambda x: (x.muni_code_hecho_imputed.astype(str) == 'True').mean() * 100)
S['choco_muni_imputado'] = entre_replicas(pmc, 'municipio imputado en el Choco (%)', '{:.1f}%')

cmed = C.groupby(['replica', 'muni_code_hecho']).size().groupby('replica').median()
S['choco_mediana_mun'] = entre_replicas(cmed, 'mediana de victimas por municipio chocoano', '{:.1f}')

print("\n  los diez municipios chocoanos con mas victimas (promedio entre replicas):")
top = (C.groupby(['replica', 'muni_code_hecho']).size()
         .groupby('muni_code_hecho').mean().sort_values(ascending=False).head(10))
for m, v in top.items():
    print(f"    {m}  {v:7.1f}")
S['choco_top'] = {k: round(float(v), 1) for k, v in top.items()}

print("\n=== MASA PARA ESTIMAR SUBREGISTRO POR MUNICIPIO ===")
print("  (LCMCR necesita varias fuentes y suficientes capturas por estrato)")
cm = C.groupby(['replica', 'muni_code_hecho']).agg(
    n=('match_group_id', 'size'), multi=('n_fuentes', lambda s: (s > 1).sum())).reset_index()
for umbral in [10, 30, 50, 100]:
    k = cm[cm.n >= umbral].groupby('replica').size()
    if len(k) == 0:
        print(f"  municipios chocoanos con >= {umbral:>3} victimas: ninguno")
        S[f'choco_mun_ge_{umbral}'] = 0.0
        continue
    k = k.reindex(sorted(cm.replica.unique()), fill_value=0)
    print(f"  municipios chocoanos con >= {umbral:>3} victimas: "
          f"{k.mean():.1f} de 31  [{np.percentile(k,2.5):.0f} – {np.percentile(k,97.5):.0f}]")
    S[f'choco_mun_ge_{umbral}'] = round(float(k.mean()), 1)
km = cm[cm.multi >= 10].groupby('replica').size()
print(f"  municipios con >= 10 victimas vistas en 2+ fuentes: {km.mean():.1f} de 31")
S['choco_mun_multi10'] = round(float(km.mean()), 1)

print("\n=== SERIE ANUAL DEL CHOCO ===")
sa = C.groupby(['replica', 'yy_hecho']).size().groupby('yy_hecho').agg(['mean', 'std'])
print("  año   victimas (media entre replicas)")
for a, r in sa.iterrows():
    barra = '#' * int(r['mean'] / 2)
    print(f"  {int(a)}  {r['mean']:7.1f}  {barra}")
S['serie_choco'] = {int(a): round(float(r['mean']), 1) for a, r in sa.iterrows()}

print("\n=== PRESUNTO RESPONSABLE, CHOCO ===")
pr = C.groupby(['replica', 'p_str']).size().groupby('p_str').mean().sort_values(ascending=False)
for p, v in pr.items():
    print(f"  {p:14} {v:7.1f}  ({100*v/pr.sum():.1f}%)")
S['choco_responsable'] = {k: round(float(v), 1) for k, v in pr.items()}

print("\n=== LOS DIEZ DEPARTAMENTOS CON MAS VICTIMAS ===")
dp = D.groupby(['replica', 'dept_code_hecho']).size().groupby('dept_code_hecho').mean()
dp = dp.sort_values(ascending=False)
for i, (dd, v) in enumerate(dp.head(10).items(), 1):
    print(f"  {i:>2}. depto {dd}  {v:8.1f}  ({100*v/dp.sum():.1f}%)")
puesto = list(dp.index).index('27') + 1
print(f"\n  el Choco es el puesto {puesto} de {len(dp)} con {dp['27']:.1f} victimas "
      f"({100*dp['27']/dp.sum():.2f}% del total nacional)")
S['choco_puesto'] = puesto
S['choco_pct_nacional'] = round(100 * float(dp['27']) / float(dp.sum()), 2)

json.dump(S, open(os.path.join(SALIDA, 'verdata_resumen.json'), 'w'), indent=1,
          ensure_ascii=False, default=float)
print("\nguardado en verdata_resumen.json")
