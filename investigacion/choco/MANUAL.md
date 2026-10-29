# Manual de lectura del repositorio

Este manual explica qué contiene la carpeta `investigacion/choco`, dónde está cada base de datos,
cómo se encadenan unas con otras y en qué orden conviene leerlas según lo que se busque. No supone
conocimiento previo del proyecto.

El trabajo se cuenta en dos partes, y el repositorio está organizado para ambas. La **primera** es
lo que el archivo del conflicto permitía saber en su momento: el panel, el modelo y sus ocho
verificaciones. La **segunda** es el terreno que se está preparando para responder lo que la primera
dejó abierto: una fuente externa de alcance nacional y los tres guiones que la contrastan. El
argumento completo está en [`PROYECTO.md`](PROYECTO.md).

---

## 1. El mapa de la carpeta

```
investigacion/choco/
├── README.md        qué es el trabajo y la regla que gobierna todo
├── PROYECTO.md      el argumento en dos partes, con las conclusiones de cada una
├── MANUAL.md        este archivo
├── FUENTES.md       las nueve fuentes, qué aporta cada una y dónde se descarga
├── ETICA.md         qué no se publica, y por qué la omisión es parte del diseño
│
├── fuente/          las dos fuentes primarias, tal como llegan
├── datos/           el panel y las bases derivadas, con su diccionario
├── cuaderno/        el cuaderno del modelo, con sus salidas guardadas
├── verificacion/    once guiones que recalculan todo, y sus resultados
└── docs/            una página de datos y el glosario de términos
```

Cinco archivos de texto en la raíz, cinco carpetas. Cada carpeta tiene un papel distinto y no se
solapan: `fuente/` es lo que entró, `datos/` es lo que se derivó, `cuaderno/` es lo que se estimó,
`verificacion/` es lo que lo comprueba y `docs/` es lo que se lee sin correr nada.

---

## 2. Dónde está cada base de datos

### Las dos fuentes primarias — `fuente/`

Son los archivos tal como los entrega la institución, sin tocar. Todo lo demás se deriva de aquí.

| archivo | qué es |
|---|---|
| `series_anuales_municipales_choco_1983_2016.xlsx` | el expediente del **Caso 07** de la JEP, agregado a municipio-año. Cinco hojas; la que se usa es `Serie larga municipal`, con 884 filas. Trae también la bolsa de hechos sin año y los metadatos de la fuente original. |
| `unodc_simci_cultivos_municipal.xlsx` | hectáreas de coca por municipio y por año del **UNODC–SIMCI**, desde 1999. Hoja `CultivosIlicitos`, con la cabecera en la fila 9. |

El expediente del Caso 07 **en bruto** no está aquí ni lo estará: lo que se publica es el agregado
a municipio-año, que es la unidad de análisis del trabajo. Ver [`ETICA.md`](ETICA.md).

### Las bases derivadas — `datos/`

| archivo | filas | qué es |
|---|---|---|
| `panel_municipal_1983_2016.csv` | 1.054 | **el panel base**: 31 municipios × 34 años, con el conteo de hechos. Los ceros son explícitos. Suma 361 hechos. |
| `panel_modelable_1984_2016.csv` | 1.023 | **el panel con las variables**: el anterior sin 1983, más las nueve variables de memoria histórica, todas rezagadas. Aquí está la variable dependiente, `ocurrencia`. |
| `base_municipal.csv` | 31 | **una fila por municipio**: totales acumulados, coca, población, distancias a los tres ríos, alertas de la Defensoría, eventos de OCHA. |
| `base_municipal_corredor.csv` | 31 | la anterior **más** el riesgo estimado para 2016, el nivel del semáforo, el índice de corredor y sus componentes, y la marca de ataque en 2026. Es la base del tablero. |
| `predicciones_fuera_de_muestra.csv` | 341 | **el atajo**: las predicciones fuera de muestra de los tres modelos en las once ventanas. Cualquier métrica se recalcula desde aquí sin reentrenar. |
| `contraste_verdata_municipal.csv` | 31 | el contraste entre el panel y la fuente externa, municipio por municipio, con los dos conteos y los dos ordenamientos. |
| `tablero_choco.json` | — | los datos que pinta la página `/choco`, ya agregados. |

El significado exacto de cada columna está en [`datos/DICCIONARIO.md`](datos/DICCIONARIO.md),
incluidos los valores centinela y qué decisión declarada hay detrás de cada uno.

### La fuente externa — no está en el repositorio

Los guiones 09 a 11 usan los microdatos del proyecto conjunto entre la **JEP**, la **Comisión de la
Verdad** y el **Human Rights Data Analysis Group**: 19.226 víctimas únicas de reclutamiento en 808
municipios entre 1990 y 2017, reconstruidas a partir de treinta y cuatro listas de registro, con
cien réplicas de imputación múltiple.

Son 397 MB en cien archivos, de modo que no se redistribuyen aquí. Se descargan del
[catálogo 795 de microdatos del DANE](https://microdatos.dane.gov.co/index.php/catalog/795/get-microdata)
y se pasan como argumento al guion. Lo que **sí** está en el repositorio es el resultado del
contraste: `datos/contraste_verdata_municipal.csv` y
`verificacion/resultados/contraste.json`.

### El cuaderno — `cuaderno/`

`modelo_riesgo_reclutamiento_choco.ipynb` es el cuaderno original, con sus salidas guardadas: se
puede leer sin ejecutar. Construye el panel, estima la regresión logística y el XGBoost, valida con
origen rodante y produce el semáforo. Las veintitrés cifras que imprime son las que replica el guion
01 desde la fuente primaria.

### Lo que se lee sin correr nada — `docs/`

| archivo | qué es |
|---|---|
| `datos.html` | una página con las bases, las medidas, el desempeño con sus intervalos y las referencias al cuaderno. Se abre en cualquier navegador. |
| `terminos-choco.pdf` | glosario de los términos técnicos del trabajo, en seis páginas. |

---

## 3. Tres recorridos, según lo que se busque

### Para entender el argumento, sin correr nada (30 minutos)

1. [`README.md`](README.md) — qué es el trabajo y la regla que gobierna todo: toda cifra es un piso.
2. [`PROYECTO.md`](PROYECTO.md) — el argumento completo en dos partes, con las conclusiones de cada
   una. Es el documento central.
3. [`docs/datos.html`](docs/datos.html) — las medidas con su intervalo, en una sola página.
4. [torredbabel.com/choco-modelo](https://torredbabel.com/choco-modelo) — la separata técnica, que
   es la misma estructura de dos partes con los gráficos.

### Para entender de dónde sale cada cifra (2 horas)

| # | qué | dónde |
|---|---|---|
| 1 | qué pregunta responde el trabajo y qué no | `PROYECTO.md` |
| 2 | de dónde sale cada dato, fuente por fuente | `FUENTES.md` |
| 3 | qué significa cada columna, y qué decisión hay detrás | `datos/DICCIONARIO.md` |
| 4 | el modelo paso a paso, con sus salidas | `cuaderno/*.ipynb` |
| 5 | qué comprueba cada guion y qué devolvió | `verificacion/LEEME.md` |
| 6 | las limitaciones, con su medición | la sección 5 de este manual |

### Para reproducirlo (unos 45 minutos de cómputo)

```bash
pip install -r verificacion/requirements.txt
cd verificacion
python 01_replica_del_cuaderno.py
```

El guion 01 reconstruye el panel desde `fuente/` y vuelve a estimar los modelos. Debe imprimir:

```
panel: 1054 filas (esperado 1054) | municipios 31 | hechos 361 (esperado 361)
panel modelable: 1023 filas
train 837 (837) prev 13.5% | test 186 (186) prev 33.3%
```

y luego una tabla donde las siete métricas del cuaderno salen marcadas `OK`. Si las siete coinciden
a tres decimales, el resto del repositorio se apoya en terreno firme. Los guiones 02 a 08 son
independientes entre sí; los 09 a 11 necesitan la fuente externa descargada aparte.
[`verificacion/LEEME.md`](verificacion/LEEME.md) tiene los tiempos de cada uno.

Todo sale idéntico a tres decimales salvo tres cosas previsibles: los tiempos de ejecución, que
dependen de la máquina; la logística jerárquica del guion 05, que se estima por inferencia
variacional y se mueve alrededor de una milésima entre corridas aun con la semilla fija; y los
guiones 09 a 11, que dependen de la versión de los microdatos descargada.

---

## 4. Cómo se encadena todo

```
fuente/series_anuales_municipales...xlsx
        │
        │  guion 01, hoja «Serie larga municipal» + los 5 municipios sin registro
        ▼
datos/panel_municipal_1983_2016.csv          1.054 filas · 361 hechos
        │
        │  nueve variables de memoria, todas con shift(1)
        ▼
datos/panel_modelable_1984_2016.csv          1.023 filas · dependiente «ocurrencia»
        │
        │  origen rodante: 11 ventanas, reajuste desde cero en cada una
        ▼
datos/predicciones_fuera_de_muestra.csv      341 predicciones · 3 modelos
        │
        ├──► semáforo y riesgo 2016 ──► datos/base_municipal_corredor.csv ──► /choco
        └──► métricas con intervalo ──► verificacion/resultados/*.json ──► /choco-modelo

catálogo 795 del DANE (fuera del repositorio)
        │
        │  guiones 09 a 11, cien réplicas agregadas una por una
        ▼
datos/contraste_verdata_municipal.csv        31 municipios · dos conteos
```

Tres cierres garantizan que ninguna variable usa información del año que predice: `shift(1)` antes
de cada acumulado, el escalado estimado dentro de la tubería y solo con el tramo de entrenamiento de
cada ventana, y el reajuste desde cero en cada una de las once ventanas.

---

## 5. Las limitaciones, con su medición

Cada limitación aquí está medida, no estimada a ojo, y el guion que la mide se nombra al lado. Van
en orden de cuánto afectan la lectura de los resultados.

### 5.1 La especificación debería ser jerárquica

Simulando 600 paneles con coeficientes conocidos (guion **06**), la logística agrupada sesga el
término de persistencia un **39 % hacia arriba**, y la cobertura de sus intervalos del 95 % cae al
35 %. La logística jerárquica con intercepto aleatorio por municipio recupera el coeficiente —sesgo
de −0,024— y la componente de varianza, 0,783 frente a una verdad de 0,8.

En los datos reales la corrección por agrupamiento apenas mueve los errores estándar: quedan en 0,97
veces los que suponen independencia, con una correlación intra-municipio de −0,024 por GEE, porque
las variables rezagadas ya absorben casi toda la heterogeneidad. Pero el punto sigue sesgado aunque
el margen no lo parezca. **El coeficiente de persistencia se lee como cota superior**, y la
reespecificación jerárquica es el primer pendiente del trabajo.

### 5.2 Los coeficientes individuales no son interpretables

El VIF de `media_movil3` es **2.081,6**; los de `lag1`, `lag2` y `lag3`, entre 262 y 321. Ajustada
sin penalización, la especificación **no converge**: coeficiente máximo de −61,5 y error estándar
máximo de 52.558. La penalización L2 no es un refinamiento del modelo, es lo que lo vuelve estimable
(guion **05**).

De ahí se sigue que la lectura de coeficientes individuales, y la atribución por SHAP que apareció
en una versión anterior, **no están identificadas**. Lo identificado es el bloque de memoria
histórica en conjunto. El conjunto reducido de seis variables sí es estimable y predice algo mejor:
AUC-ROC 0,798 frente a 0,788.

### 5.3 La forma funcional está mal especificada

Box–Tidwell rechaza la linealidad en el logit de las cuatro continuas: p < 0,001 en tres y
p = 0,0003 en la cuarta (guion **05**). El modelo ordena bien aun así, pero splines o tramos —con el
criterio de selección declarado— son el segundo pendiente.

### 5.4 El índice de corredor es hipótesis para un régimen y está refutado para el otro

Los tres componentes del índice que ordena los ataques de 2026 con AUC 0,927 se eligieron **después**
de saber qué municipios fueron atacados. La prueba de permutación exacta —p = 0,00023, enumerando
las 736.281 asignaciones posibles (guion **04**)— responde si ese índice separa a esos seis mejor
que el azar, y la respuesta es sí; no responde si se habría elegido antes de verlos. Solo se vuelve
evidencia si el índice se congela, como está escrito en el guion 04, y se evalúa contra desenlaces
que todavía no han ocurrido.

Lo que sí está medido (guion **08**) es que ese índice **no explica el reclutamiento anterior al
acuerdo**: AUC de 0,470 sobre 527 municipio-año de 2000 a 2016, con una ganancia de −0,005 al
añadirlo al modelo. De las cuatro celdas del dos por dos que compara los dos regímenes, solo esa una
está construida sabiendo el desenlace; las otras tres son limpias y ya bastan para establecer el
cambio.

### 5.5 El panel cuenta un solo actor

El expediente contabiliza hechos atribuidos a las antiguas FARC-EP, que explican el **41,8 %** del
fenómeno medido en el Chocó, frente al 39,3 % del ELN y el 11,7 % de las estructuras paramilitares
(guion **09**). Es la limitación de mayor consecuencia práctica: puso a Bajo Baudó en el puesto 23 del semáforo y
en el nivel bajo del semáforo cuando en la fuente independiente ocupa el puesto 4, y tres de los
cinco municipios sin un solo hecho en el panel sí tienen víctimas documentadas. La corrección no
exige un modelo nuevo, exige contar todos los actores.

### 5.6 Con la Defensoría se mide concordancia, no anticipación

Está el conteo acumulado de alertas por municipio, no su fecha. Sin fecha no se puede saber si una
alerta precede o sigue al riesgo que el modelo estima (guion **07**). Conseguir el inventario con
fecha es el tercer pendiente, y es lo que convertiría esa sección en una prueba de valor
incremental.

### 5.7 Hay una vía de selección declarada

El cuaderno prueba seis configuraciones de XGBoost y anuncia «la mejor por AUC-ROC» comparándolas en
el conjunto de prueba. Esa frase es exploratoria y así debe leerse. No afecta la conclusión
principal —que la logística supera a XGBoost— porque esa comparación usa la configuración inicial,
fijada antes de mirar la prueba.

### 5.8 Las cifras publicadas que no se sostuvieron

Al rastrear cada número publicado hasta el dato que lo produjo (guion **02**), nueve no se
sostuvieron. Están corregidos y enumerados en la sección «Lo que corregimos» de
[torredbabel.com/choco-modelo](https://torredbabel.com/choco-modelo). Siete de los nueve errores
iban en contra del trabajo; dos lo favorecían, y son los dos que había que quitar.

---

## 6. Preguntas de método, con su cifra

- **¿Por qué el n no son 1.023 filas sino 31 municipios?** Son 31 unidades observadas 34 veces, y
  esa distinción gobierna la lectura de todos los intervalos. Medida de tres maneras en el §2b del
  guion 05.
- **¿Por qué AUC-PR y no solo AUC-ROC?** Por la prevalencia de 0,334: el AUC-ROC premia aciertos
  sobre la clase mayoritaria, que son los fáciles. Se reportan los dos, cada uno contra su
  referencia.
- **¿Con qué criterio se eligió la penalización?** No se eligió: el cuaderno usa el valor por
  omisión, C = 1,0. Lo que sí se midió es cuánto importa: sobre cinco órdenes de magnitud el AUC
  fuera de muestra va de 0,787 a 0,808, muy por debajo del ancho del intervalo de la propia métrica.
- **¿Cuántos municipios deciden el ajuste?** Ninguno. Dejando cada uno fuera, uno por vez y
  repitiendo las once ventanas —341 reajustes—, el AUC se mueve entre −0,020 y +0,004. El más
  influyente es Riosucio, con 48 hechos acumulados.
- **¿Hay fuga temporal?** Tres cierres verificables, descritos en la sección 4 de este manual.
- **¿Por qué ocurrencia y no conteo?** Están los dos. El de ocurrencia es el principal por razón
  operativa: lo que una entidad hace con la salida es priorizar territorios.
- **¿Por qué los intervalos son tan anchos?** Porque hay 31 unidades independientes. El AUC-PR va de
  0,463 a 0,843, y ese ancho es información sobre lo que el tamaño de la muestra permite afirmar.

---

## 7. Cómo citar

> Beltrán, A. (2026). *Alerta territorial del Chocó: ordenamiento del riesgo de reclutamiento de
> NNA a partir del expediente del Caso 07 de la JEP* (versión 1.0). Maestría en Ciencia de Datos,
> Universidad Ean, Bogotá.

Las fuentes primarias se citan por separado, con el detalle de cada una en
[`FUENTES.md`](FUENTES.md).
