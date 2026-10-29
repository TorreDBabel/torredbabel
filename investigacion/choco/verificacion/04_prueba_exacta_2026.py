"""El punto mas fragil de la pagina: AUC sobre 6 positivos.
Prueba de permutacion EXACTA (enumera las 736.281 asignaciones posibles),
intervalo por remuestreo, y descomposicion del indice compuesto para ver
cuanto de su desempeno es tautologico."""
import numpy as np, pandas as pd, json, itertools
from sklearn.metrics import roc_auc_score
import os
DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultados')
os.makedirs(SALIDA, exist_ok=True)

b = pd.read_csv(os.path.join(DATOS, 'base_municipal_corredor.csv'))
y = b['dron_2026'].values.astype(int)
n, k = len(b), int(y.sum())
rng = np.random.default_rng(42)
R = {'n_municipios': n, 'n_atacados': k}

print(f"poblacion: {n} municipios, {k} con ataque documentado en 2026")
print(f"municipios atacados: {', '.join(sorted(b[b.dron_2026==1].municipio))}\n")

ORD = [('s_historico', 'Semáforo histórico de reclutamiento'),
       ('s_actividad', 'Actividad registrada 2016-2025'),
       ('s_divergencia', 'Divergencia presente/pasado'),
       ('s_coca', 'Coca acumulada'),
       ('s_corredor', 'Cercanía al río San Juan (sola)'),
       ('idx_corredor', 'Índice de corredor en disputa (compuesto)')]

# ---- AUC de Mann-Whitney calculada por rangos, para enumerar rapido ----
def auc_de_indices(rangos, idx):
    """AUC con los k positivos en las posiciones idx, dados los rangos del puntaje."""
    sp = rangos[list(idx)].sum()
    return (sp - k * (k + 1) / 2) / (k * (n - k))

print('=== prueba de permutacion EXACTA: las 736.281 asignaciones de 6 entre 31 ===')
pos_reales = tuple(np.where(y == 1)[0])
fil = []
for col, et in ORD:
    s = b[col].values.astype(float)
    rangos = pd.Series(s).rank(method='average').values
    obs = auc_de_indices(rangos, pos_reales)
    todas = np.fromiter(
        (rangos[list(c)].sum() for c in itertools.combinations(range(n), k)),
        dtype=float, count=736281)
    aucs = (todas - k * (k + 1) / 2) / (k * (n - k))
    p_sup = float((aucs >= obs).mean())          # unilateral: ordena mejor que el azar
    p_dos = float((np.abs(aucs - 0.5) >= abs(obs - 0.5)).mean())
    fil.append(dict(ordenamiento=et, AUC=round(obs, 3),
                    p_exacta_unilateral=round(p_sup, 5),
                    p_exacta_bilateral=round(p_dos, 5),
                    percentil=round(100 * float((aucs < obs).mean()), 1)))
tab = pd.DataFrame(fil).sort_values('AUC', ascending=False)
print(tab.to_string(index=False))
R['permutacion_exacta'] = tab.to_dict('records')

# ---- intervalo del AUC por remuestreo estratificado ----
print('\n=== intervalo del AUC (remuestreo estratificado, B = 10.000) ===')
P, Ng = np.where(y == 1)[0], np.where(y == 0)[0]
ic = []
for col, et in [('idx_corredor', 'Índice compuesto'), ('s_corredor', 'Cercanía al San Juan sola'),
                ('s_historico', 'Semáforo histórico')]:
    s = b[col].values.astype(float)
    v = []
    for _ in range(10000):
        ip = rng.choice(P, k, replace=True); ineg = rng.choice(Ng, n - k, replace=True)
        yy = np.r_[np.ones(k), np.zeros(n - k)]; ss = np.r_[s[ip], s[ineg]]
        if len(np.unique(ss)) > 1:
            v.append(roc_auc_score(yy, ss))
    lo, hi = np.percentile(v, [2.5, 97.5])
    ic.append(dict(ordenamiento=et, AUC=round(float(roc_auc_score(y, s)), 3),
                   ic95=f'[{lo:.3f}; {hi:.3f}]', amplitud=round(float(hi - lo), 3)))
print(pd.DataFrame(ic).to_string(index=False))
R['ic_auc_drones'] = ic

# ---- descomposicion: cuanto aporta cada componente sobre la cercania al rio ----
print('\n=== descomposicion del compuesto: el peso del componente geografico ===')
dec = []
comb = [('s_corredor',), ('s_coca',), ('s_divergencia',),
        ('s_corredor', 's_coca'), ('s_corredor', 's_divergencia'),
        ('s_coca', 's_divergencia'), ('s_corredor', 's_coca', 's_divergencia')]
for c in comb:
    s = b[list(c)].mean(axis=1).values
    dec.append(dict(componentes=' + '.join(x.replace('s_', '') for x in c),
                    AUC=round(float(roc_auc_score(y, s)), 3),
                    top6=int(b.assign(z=s).nlargest(6, 'z').dron_2026.sum())))
print(pd.DataFrame(dec).to_string(index=False))
R['descomposicion'] = dec

# ---- cuantos de los 6 atacados estan en la cuenca del San Juan ----
print('\n=== por que el componente geografico roza la tautologia ===')
at = b[b.dron_2026 == 1][['municipio', 'd_san_juan', 'rio_cercano', 'coca_total']].sort_values('d_san_juan')
print(at.round(1).to_string(index=False))
print(f"\ndistancia al San Juan — atacados: mediana {at.d_san_juan.median():.1f} km | "
      f"resto: mediana {b[b.dron_2026==0].d_san_juan.median():.1f} km")
print(f"de los 6 atacados, {int((at.d_san_juan <= b.d_san_juan.median()).sum())} están por debajo de la mediana departamental")
R['d_san_juan_atacados'] = at.to_dict('records')

json.dump(R, open(os.path.join(SALIDA, 'drones.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print('\nguardado en drones.json')
