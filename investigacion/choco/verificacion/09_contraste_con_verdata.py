"""Contraste entre verdata y el panel del Choco.

verdata es la estimacion conjunta JEP - Comision de la Verdad - HRDAG: integra 34
listas de registro y entrega 100 replicas de imputacion multiple. El panel de este
trabajo cuenta hechos atribuidos a las antiguas FARC-EP; verdata cuenta victimas
unicas de todos los actores. Son cantidades distintas, y el contraste mide cuanto
del fenomeno queda fuera del panel.

Cuatro preguntas:
  A. ¿Coinciden los conteos municipales?
  B. ¿Cambia el ordenamiento del territorio?
  C. ¿Que queda fuera al contar solo la era FARC?
  D. ¿Estaban vacios los cinco municipios sin registro?

REGLA DE AGREGACION. Una cantidad se calcula DENTRO de cada replica y luego se
resume la distribucion entre las 100 replicas. Las replicas en las que una
categoria no aparece valen cero, no se omiten: promediar solo sobre las replicas
donde algo aparece infla las categorias raras. De ahi el reindex explicito contra
la lista completa de replicas en cada agregacion.

Uso: python 09_contraste_con_verdata.py <carpeta con verdata-reclutamiento-R*.csv>
La carpeta se obtiene del catalogo 795 de microdatos del DANE.
"""
import sys, os, glob, json
import pandas as pd, numpy as np
from scipy import stats

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, '..', 'datos')
SALIDA = os.path.join(AQUI, 'resultados')
os.makedirs(SALIDA, exist_ok=True)

if len(sys.argv) < 2:
    raise SystemExit(__doc__)
RUTA = sys.argv[1]

arch = sorted(glob.glob(os.path.join(RUTA, 'verdata-reclutamiento-R*.csv')))
if not arch:
    raise SystemExit(f"no hay verdata-reclutamiento-R*.csv en {RUTA}")
USA = ['replica', 'match_group_id', 'muni_code_hecho', 'dept_code_hecho',
       'yy_hecho', 'p_str']
R = []
for a in arch:
    d = pd.read_csv(a, usecols=USA, low_memory=False,
                    dtype={'muni_code_hecho': str, 'dept_code_hecho': str})
    R.append(d[d.dept_code_hecho == '27'])
C = pd.concat(R, ignore_index=True)
REPS = sorted(C.replica.unique())
print(f"replicas leidas: {len(REPS)}")
print(f"Choco en verdata: {len(C)/len(REPS):,.0f} victimas por replica\n")


def por_replica(sub, clave):
    """Conteo por <clave> dentro de cada replica, con cero explicito en las
    replicas donde la clave no aparece. Devuelve media y rango del 95%."""
    t = (sub.groupby(['replica', clave]).size().unstack(fill_value=0)
            .reindex(REPS, fill_value=0))
    return (t.mean(), t.quantile(0.025), t.quantile(0.975))


base = pd.read_csv(os.path.join(DATOS, 'base_municipal.csv'))
base['cod'] = base.cod_divipola.astype(str).str.zfill(5)
nom = dict(zip(base.cod, base.municipio))

C['cod'] = C.muni_code_hecho.astype(str).str.split('.').str[0].str.zfill(5)
desconocidos = sorted(set(C.cod) - set(base.cod))
if desconocidos:
    print(f"codigos de verdata que no estan en la base municipal: {desconocidos}")

vm, vlo, vhi = por_replica(C, 'cod')
M = base[['municipio', 'cod', 'casos_total', 'farc_total']].copy()
M['verdata'] = M.cod.map(vm).fillna(0.0)
M['verdata_lo'] = M.cod.map(vlo).fillna(0.0)
M['verdata_hi'] = M.cod.map(vhi).fillna(0.0)

print("=== A. ¿COINCIDEN LOS CONTEOS? ===")
print(f"  panel, hechos unicos era FARC 1983-2016:            {M.farc_total.sum():7,.0f}")
print(f"  verdata, victimas unicas todos los actores 1990-2017:{M.verdata.sum():7,.1f}")
r_p, p_p = stats.pearsonr(M.farc_total, M.verdata)
r_s, p_s = stats.spearmanr(M.farc_total, M.verdata)
print(f"\n  correlacion entre municipios: Pearson {r_p:.3f} (p={p_p:.4f})  "
      f"Spearman {r_s:.3f} (p={p_s:.4f})")
print("  las dos series miden cosas distintas (hechos frente a victimas, periodos")
print("  que no coinciden), de modo que la correlacion dice que concuerdan en la")
print("  forma del territorio, no que una valide el conteo de la otra.")

print("\n=== B. ¿CAMBIA EL ORDENAMIENTO? ===")
print("  OJO: rank_panel ordena por HECHOS ACUMULADOS y no es el rank_hist del tablero,")
print("  que ordena por el RIESGO ESTIMADO para 2016. Los dos aparecen abajo porque no")
print("  coinciden: Bajo Baudo es 21 por hechos y 23 por riesgo estimado.")
M['rank_panel'] = M.farc_total.rank(ascending=False, method='min').astype(int)
_tab = pd.read_csv(os.path.join(DATOS, 'base_municipal_corredor.csv'))
M['rank_semaforo'] = M.municipio.map(dict(zip(_tab.municipio, _tab.rank_hist)))
M['nivel_semaforo'] = M.municipio.map(dict(zip(_tab.municipio, _tab.nivel_2016)))
M['rank_verdata'] = M.verdata.rank(ascending=False, method='min').astype(int)
M['salto'] = M.rank_panel - M.rank_verdata
a = M.nsmallest(10, 'rank_panel')
b = M.nsmallest(10, 'rank_verdata')
print(f"  {'panel (hechos FARC)':34} {'verdata (victimas)':34}")
for i in range(10):
    x, y = a.iloc[i], b.iloc[i]
    print(f"  {i+1:>2}. {x.municipio[:22]:22} {x.farc_total:4.0f}   "
          f"{y.municipio[:22]:22} {y.verdata:6.1f}")
comunes = len(set(a.municipio) & set(b.municipio))
print(f"\n  coinciden {comunes} de los 10 primeros")
print("\n  los que mas suben con verdata:")
for _, r in M.nlargest(5, 'salto').iterrows():
    print(f"    {r.municipio[:24]:24} puesto {r.rank_panel:>2} -> {r.rank_verdata:>2}"
          f"   ({r.farc_total:.0f} hechos -> {r.verdata:.1f} victimas)")
print("  los que mas bajan:")
for _, r in M.nsmallest(5, 'salto').iterrows():
    print(f"    {r.municipio[:24]:24} puesto {r.rank_panel:>2} -> {r.rank_verdata:>2}"
          f"   ({r.farc_total:.0f} hechos -> {r.verdata:.1f} victimas)")

print("\n=== C. ¿QUE QUEDA FUERA AL CONTAR SOLO LA ERA FARC? ===")
pm, plo, phi = por_replica(C, 'p_str')
tot = pm.sum()
print(f"  {'presunto responsable':14} {'victimas':>9}  {'%':>6}  {'rango 95%':>16}")
for k in pm.sort_values(ascending=False).index:
    print(f"  {k:14} {pm[k]:9.1f}  {100*pm[k]/tot:5.1f}%  "
          f"[{plo[k]:5.1f} – {phi[k]:5.1f}]")
print(f"\n  el panel cubre el {100*pm.get('GUE-FARC', 0)/tot:.1f}% del fenomeno medido")

print("\n  el mismo reparto, antes y despues del acuerdo:")
for et, sub in [('1990-2016', C[C.yy_hecho < 2017]), ('2017', C[C.yy_hecho >= 2017])]:
    p2, _, _ = por_replica(sub, 'p_str')
    t2 = p2.sum()
    if t2 == 0:
        continue
    print(f"    {et}: {t2:.0f} victimas por replica")
    for k in p2.sort_values(ascending=False).index[:4]:
        print(f"      {k:12} {p2[k]:7.1f}  ({100*p2[k]/t2:.1f}%)")

print("\n=== D. ¿ESTABAN VACIOS LOS CINCO MUNICIPIOS SIN REGISTRO? ===")
V = M[M.farc_total == 0].sort_values('verdata', ascending=False)
print(f"  {'municipio':26} {'panel':>6} {'verdata':>8}  {'rango 95%':>16}")
for _, r in V.iterrows():
    print(f"  {r.municipio:26} {r.farc_total:6.0f} {r.verdata:8.2f}  "
          f"[{r.verdata_lo:5.2f} – {r.verdata_hi:5.2f}]")
con = int((V.verdata > 0).sum())
print(f"\n  {con} de los {len(V)} municipios sin un solo hecho en el panel SI tienen")
print(f"  victimas documentadas en verdata. El cero del panel era ausencia de")
print(f"  registro en una fuente, no ausencia del hecho en el territorio.")
print(f"  Los otros {len(V)-con} siguen en cero en las dos fuentes, y con dos fuentes")
print(f"  no se puede distinguir un territorio sin hechos de uno sin cobertura.")

print("\n=== E. LOS DOS CASOS QUE CAMBIAN LA LECTURA DEL TABLERO ===")
detalle = {}
for cod, et in [('27580', 'RÍO IRÓ'), ('27077', 'BAJO BAUDÓ')]:
    s = C[C.cod == cod]
    pr, prlo, prhi = por_replica(s, 'p_str')
    an, _, _ = por_replica(s, 'yy_hecho')
    f = M[M.cod == cod].iloc[0]
    print(f"\n  {et} — {pr.sum():.1f} victimas en verdata (puesto {f.rank_verdata}), "
          f"{int(f.farc_total)} hechos en el panel (puesto {f.rank_panel}),")
    print(f"    puesto {f.rank_semaforo} y nivel {f.nivel_semaforo} en el semaforo del tablero")
    for k in pr.sort_values(ascending=False).index:
        if pr[k] < 0.05:
            continue
        print(f"    {k:10} {pr[k]:6.1f} ({100*pr[k]/pr.sum():5.1f}%)  "
              f"[{prlo[k]:.1f} – {prhi[k]:.1f}]")
    serie = {int(a): round(float(v), 1) for a, v in an.items() if v >= 0.05}
    print(f"    serie: " + ', '.join(f'{a}:{v}' for a, v in sorted(serie.items())))
    detalle[et] = dict(total=round(float(pr.sum()), 1),
                       responsable={k: round(float(pr[k]), 1)
                                    for k in pr.index if pr[k] >= 0.05},
                       serie=serie)

M.to_csv(os.path.join(DATOS, 'contraste_verdata_municipal.csv'), index=False)
json.dump(dict(
    replicas=len(REPS),
    verdata_total=round(float(M.verdata.sum()), 1),
    farc_total=int(M.farc_total.sum()),
    pearson=round(float(r_p), 3), spearman=round(float(r_s), 3),
    top10_comunes=int(comunes),
    pct_farc=round(100 * float(pm.get('GUE-FARC', 0) / tot), 1),
    pct_eln=round(100 * float(pm.get('GUE-ELN', 0) / tot), 1),
    responsable={k: round(float(pm[k]), 1) for k in pm.index},
    silenciosos={r.municipio: round(float(r.verdata), 2) for _, r in V.iterrows()},
    silenciosos_con_victimas=con,
    detalle=detalle,
), open(os.path.join(SALIDA, 'contraste.json'), 'w'), indent=1,
    ensure_ascii=False, default=float)
print("\nguardado en datos/contraste_verdata_municipal.csv y resultados/contraste.json")
