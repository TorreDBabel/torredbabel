# Diccionario de datos

Seis archivos. Todos en UTF-8, separador coma, decimal punto. Los nombres de municipio van en
mayúsculas con tilde, como los entrega la fuente.

---

## `panel_municipal_1983_2016.csv` — el panel base

**1.054 filas** = 31 municipios × 34 años. Suma de hechos: **361**.

| columna | tipo | qué es |
|---|---|---|
| `cod_divipola` | entero | código DANE del municipio, la llave de unión |
| `municipio` | texto | nombre oficial |
| `anio` | entero | 1983 a 2016 |
| `hechos` | entero | hechos únicos de reclutamiento registrados ese año |

Un `hechos = 0` significa **sin registro**, no «sin reclutamiento». Ver `FUENTES.md`.

---

## `panel_modelable_1984_2016.csv` — el panel con las variables

**1.023 filas**: el anterior menos las 31 de 1983, donde ninguna variable rezagada existe.

| columna | qué es |
|---|---|
| `hechos` | la variable original |
| `ocurrencia` | 1 si `hechos > 0`. **Es la variable dependiente del modelo.** |
| `lag1`, `lag2`, `lag3` | hechos de hace uno, dos y tres años |
| `media_movil3` | media de los tres años anteriores |
| `acum_prev` | suma de todos los hechos previos del municipio |
| `anios_activos_prev` | cuántos años previos tuvieron al menos un hecho |
| `racha_prev` | años consecutivos con hechos hasta el anterior |
| `anios_desde_ultimo` | años transcurridos desde el último hecho; **99** si nunca hubo |
| `depto_lag1` | total departamental del año anterior |

**Todas llevan `shift(1)`**: ninguna usa información del año que se predice. El valor centinela
99 en `anios_desde_ultimo` marca los municipios sin historia; es una decisión declarada, y en un
modelo estandarizado tiene mucho apalancamiento.

Colinealidad: el VIF de `media_movil3` es **2.081,6**, y el de los tres rezagos va de 262 a 321.
Los coeficientes individuales de ese bloque **no son interpretables**. Ver `MANUAL.md`, punto 2.

---

## `base_municipal.csv` — las 31 fichas municipales

Una fila por municipio. Variables de contexto; **no entran al modelo de ocurrencia**, sino al
análisis territorial y al índice de corredor.

| columna | qué es |
|---|---|
| `casos_total` | hechos acumulados 1983–2016 |
| `farc_total`, `farc_activos`, `farc_ult5`, `farc_racha_max`, `farc_conc` | resúmenes de la era FARC |
| `coca_total` | hectáreas de coca acumuladas (UNODC–SIMCI) |
| `pob_prom` | población media del periodo (DANE) |
| `tasa` | hechos por población |
| `lat`, `lon` | centroide de la cabecera |
| `d_atrato`, `d_san_juan`, `d_baudo` | distancia en km al trazo de cada río |
| `d_rio_min`, `rio_cercano` | distancia al río más cercano y cuál es |
| `riberenidad` | índice 0–100: `100 × e^(−d/15)`, con `d` en km al río más cercano |
| `ocha` | eventos humanitarios 2016–2025 |
| `alertas`, `estructurales`, `inminencia` | conteos de alertas de la Defensoría |
| `actividad_post` | `ocha + alertas`: actividad contemporánea |

---

## `base_municipal_corredor.csv` — las fichas más el ordenamiento

El anterior, más lo que produce el modelo y el índice alternativo.

| columna | qué es |
|---|---|
| `riesgo_2016` | probabilidad estimada al cierre de 2016 |
| `nivel_2016` | ALTA, MEDIA o BAJA |
| `rank_hist` | puesto en el ordenamiento del semáforo (1 = mayor riesgo) |
| `dron_2026` | 1 si registró ataque con dron o artefacto lanzado en 2026 |
| `rank_post` | puesto por actividad contemporánea |
| `razon_post_hist` | `(actividad_post + 1) / (farc_total + 1)`: divergencia presente/pasado |
| `s_corredor`, `s_coca`, `s_divergencia` | los tres componentes, en percentil 0–1 |
| `idx_corredor` | `100 × (0,40·s_corredor + 0,35·s_coca + 0,25·s_divergencia)` |
| `rank_corredor` | puesto en ese índice |

`s_corredor` es el percentil **invertido** de `d_san_juan`: más cerca del río, más alto.

> El índice de corredor es una **hipótesis**, no un resultado validado: sus tres componentes se
> eligieron después de saber qué municipios fueron atacados. Ver `MANUAL.md`, punto 4.

---

## `predicciones_fuera_de_muestra.csv` — las 341 predicciones

Las once ventanas de validación de origen rodante, 2006–2016, acumuladas. **Es el archivo con el
que se puede recalcular cualquier métrica del trabajo sin reentrenar nada.**

| columna | qué es |
|---|---|
| `anio` | año evaluado (2006–2016) |
| `mun` | municipio |
| `y` | ocurrencia real: 1 o 0 |
| `hechos` | número de hechos ese año |
| `base` | predicción de la línea base de persistencia |
| `lr` | probabilidad de la regresión logística |
| `xgb` | probabilidad de XGBoost |

341 filas = 31 municipios × 11 años. Positivos: 114. Prevalencia: 0,334.

Ejemplo de uso:

```python
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score
d = pd.read_csv('predicciones_fuera_de_muestra.csv')
print(roc_auc_score(d.y, d.lr), average_precision_score(d.y, d.lr))
# 0.788  0.704
```

---

## `tablero_choco.json` — los datos del mapa

Lo que alimenta el tablero de torredbabel.com/choco.

| clave | qué es |
|---|---|
| `w`, `h` | dimensiones del espacio de coordenadas proyectado |
| `anios` | los 34 años de la serie |
| `dep` | serie anual del departamento |
| `rios` | los tres cauces, como trazos en el mismo espacio |
| `mun` | una entrada por municipio |

Cada municipio trae `d` (el contorno ya proyectado como ruta SVG), `cx`/`cy` (centro de la
etiqueta), `s` (la serie anual de 34 valores) y todas las variables de `base_municipal_corredor`
con nombres abreviados.
