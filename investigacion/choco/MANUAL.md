# Manual de revisión

Escrito para quien va a evaluar o dirigir este trabajo. Dice en qué orden mirar las cosas, qué
comprobar en cada paso y dónde están los puntos débiles —señalados por nosotros, no escondidos.

Tiempo estimado: **veinte minutos** para la revisión rápida, **dos horas** para la completa.

---

## La revisión rápida (20 minutos)

### 1. Compruebe que el panel es lo que decimos (3 min)

```bash
cd verificacion && python 01_replica_del_cuaderno.py
```

Debe imprimir, en este orden:

```
panel: 1054 filas (esperado 1054) | municipios 31 | hechos 361 (esperado 361)
panel modelable: 1023 filas
train 837 (837) prev 13.5% | test 186 (186) prev 33.3%
```

y luego una tabla donde las siete métricas del cuaderno salen marcadas `OK`. Ese guion
**reconstruye el panel desde la fuente primaria** y vuelve a estimar los modelos; si las siete
coinciden a tres decimales, todo lo demás de este repositorio se apoya en terreno firme.

### 2. Mire el tamaño real de la evidencia (2 min)

Abra `datos/panel_municipal_1983_2016.csv`. Son 1.054 filas, pero la pregunta correcta no es
cuántas filas hay sino **cuántas unidades independientes**: son 31 municipios observados 34
veces. Esa distinción gobierna la lectura de todos los intervalos, y está tratada en el §2b del
guion `05_diagnosticos_de_panel.py`.

Mire también cuántos positivos tiene cada ventana de evaluación: van de **5 a 14**. El año 2016,
con cinco, es el más frágil de los once.

### 3. Lea las métricas con su intervalo (5 min)

Abra `docs/datos.html`, o `verificacion/resultados/intervalos.json`. Ninguna cifra se publica
sin su intervalo del 95 %, obtenido por remuestreo de bloques de municipio (B = 4.000).

Lo que debería saltarle a la vista: **los intervalos son anchos**. El AUC-PR va de 0,463 a
0,843. Con 31 unidades no puede ser de otro modo, y ese ancho es información, no un defecto del
método.

### 4. Vaya directo a lo que falló (10 min)

Lea la sección «Lo que corregimos» de [torredbabel.com/choco-modelo](https://torredbabel.com/choco-modelo).
Nueve cifras publicadas no se sostuvieron al rastrearlas hasta el dato que las produjo. Siete de
los nueve errores iban **en contra** del proyecto; dos lo favorecían, y son los dos que había
que quitar.

Si va a atacar el trabajo por algún lado, empiece por ahí: es donde ya sabemos que hubo
descuido, y la respuesta a «¿qué más habrá?» es que corrimos los siete guiones de
`verificacion/` para contestarla.

---

## La revisión completa (2 horas)

### Orden de lectura

| # | Qué | Dónde |
|---|---|---|
| 1 | Qué pregunta responde el trabajo y qué no | `PROYECTO.md` |
| 2 | De dónde sale cada dato | `FUENTES.md` |
| 3 | Qué significa cada columna | `datos/DICCIONARIO.md` |
| 4 | El modelo, paso a paso | `cuaderno/*.ipynb` |
| 5 | Las verificaciones | `verificacion/01` a `07` |
| 6 | El relato completo | torredbabel.com/choco-modelo |

### Los siete guiones, y qué contesta cada uno

| Guion | Pregunta que responde |
|---|---|
| `01_replica_del_cuaderno.py` | ¿Salen los números del cuaderno desde la fuente primaria? |
| `02_rastreo_de_cifras.py` | ¿De qué población salió cada cifra publicada? |
| `03_intervalos_y_calibracion.py` | ¿Cuánto margen tiene cada métrica? ¿Significa algo la probabilidad? |
| `04_prueba_exacta_2026.py` | Con seis ataques, ¿qué se puede afirmar? (permutación exacta) |
| `05_diagnosticos_de_panel.py` | Independencia, lambda, influencia, linealidad en el logit |
| `06_simulacion_y_chequeo.py` | ¿Recupera el estimador la verdad con 31 unidades? |
| `07_alarmas_y_defensoria.py` | Matriz de confusión y concordancia con quien ya advierte |
| `08_corredor_en_el_tiempo.py` | ¿Tiene el corredor valor predictivo, o solo retrospectivo? |

Cada uno deja su salida en `verificacion/resultados/`. Todos fijan semilla en 42.

El **08** merece atención aparte porque es la única prueba del repositorio que refuta una
hipótesis nuestra. El índice de corredor se construyó mirando los ataques de 2026, de modo que su
AUC de 0,927 es circular. Ese guion hace lo contrario: reconstruye el índice año por año con la
coca anual del UNODC —disponible desde 1999— y lo confronta con el reclutamiento registrado entre
2000 y 2016, que es anterior a los ataques y por tanto no pudo influir en la elección de sus
componentes.

El resultado es inequívoco. El corredor da **AUC 0,470** sobre ese periodo, con intervalo
[0,358; 0,591] que contiene el azar; añadido al bloque de memoria histórica, la ganancia es
**−0,005**, intervalo [−0,015; +0,001]. **El corredor no predice reclutamiento.**

Eso no refuta la hipótesis del giro: la refuerza. Un índice que describe la disputa posterior al
acuerdo y que, probado contra el fenómeno anterior, no ordena nada, se comporta exactamente como
se esperaría si los dos regímenes tuvieran causas distintas. Y cierra una puerta con evidencia:
meter el corredor como variable en el modelo de reclutamiento del Chocó queda descartado.

---

## Los puntos débiles, dichos por nosotros

Esta sección existe porque esconderlos sería peor. En orden de gravedad:

### 1. La especificación debería ser jerárquica

Simulando 600 paneles con coeficientes conocidos (`06_simulacion_y_chequeo.py`), la logística
agrupada **sesga el término de persistencia un 39 % hacia arriba**, y la cobertura de sus
intervalos del 95 % cae al 35 %. La logística jerárquica con intercepto aleatorio por municipio
recupera el coeficiente —sesgo de −0,024— y la componente de varianza, 0,783 frente a una verdad
de 0,8.

En los datos reales la corrección por agrupamiento apenas mueve los errores estándar (0,97 veces
los que suponen independencia; correlación intra-municipio de −0,024 por GEE), porque las
variables rezagadas ya absorben casi toda la heterogeneidad. Pero el punto sigue sesgado aunque
el margen no lo parezca. **El coeficiente de persistencia debe leerse como cota superior**, y la
reespecificación jerárquica es el primer pendiente del trabajo.

### 2. Los coeficientes individuales no son interpretables

El VIF de `media_movil3` es **2.081,6**; los de `lag1`, `lag2` y `lag3`, entre 262 y 321. Peor:
ajustada sin penalización, la especificación **no converge** —coeficiente máximo de −61,5, error
estándar máximo de 52.558—. La penalización L2 no es un refinamiento del modelo: es lo que lo
vuelve estimable.

De ahí se sigue que la lectura de coeficientes individuales, y la atribución por SHAP que se
publicó en una versión anterior, **no están identificadas**. Lo identificado es el bloque de
memoria histórica en conjunto. El conjunto reducido de seis variables es estimable y predice algo
mejor: AUC-ROC 0,798 frente a 0,788.

### 3. La forma funcional está mal especificada

Box–Tidwell rechaza la linealidad en el logit de las cuatro continuas (p < 0,001 en tres,
p = 0,0003 en la cuarta). El modelo ordena bien aun así, pero splines o tramos —con el criterio
de selección declarado— son el segundo pendiente.

### 4. El índice de corredor es una hipótesis para el régimen posterior, y está refutado para el anterior

Los tres componentes del índice que ordena los ataques de 2026 con AUC 0,927 se eligieron
**después** de saber qué municipios fueron atacados. La prueba de permutación exacta (p = 0,00023,
enumerando las 736.281 asignaciones posibles) responde si ese índice separa a esos seis mejor que
el azar, y la respuesta es sí; no responde si lo habríamos elegido antes de verlos.

Solo se vuelve evidencia si el índice se congela hoy —está escrito en `04_prueba_exacta_2026.py`—
y se evalúa contra desenlaces que todavía no han ocurrido.

Lo que sí está medido, y es el resultado del guion `08`, es que **ese índice no explica el
reclutamiento anterior al acuerdo**: AUC de 0,470 sobre 527 municipio-año de 2000 a 2016, y una
ganancia de −0,005 al añadirlo al modelo. La celda de arriba a la derecha del dos por dos de la
separata es la única construida sabiendo el desenlace; las otras tres son limpias, y ya bastan
para establecer el cambio de régimen.

### 5. Lo que medimos con la Defensoría es concordancia, no anticipación

Tenemos el conteo acumulado de alertas por municipio, no su fecha. Sin fecha no se puede saber si
una alerta precede o sigue al riesgo que el modelo estima. Conseguir el inventario con fecha es
el tercer pendiente, y es lo que convertiría esa sección en una prueba de valor incremental.

### 6. Hay una vía de selección declarada

El cuaderno prueba seis configuraciones de XGBoost y anuncia «la mejor por AUC-ROC»
comparándolas en el conjunto de prueba. Esa frase es exploratoria y así debe leerse. No afecta la
conclusión principal —que la logística supera a XGBoost— porque esa comparación usa la
configuración inicial, fijada antes de mirar la prueba.

---

## Preguntas que conviene hacernos

Están aquí porque ya nos las hicimos, y las respuestas con su cifra están en
[torredbabel.com/choco-modelo](https://torredbabel.com/choco-modelo), sección «Notas».

- ¿Por qué AUC-PR y no solo AUC-ROC? → Por la prevalencia de 0,334.
- ¿Con qué criterio eligieron la penalización? → No se eligió: valor por omisión, C = 1,0. El
  rango de sensibilidad va de 0,787 a 0,808 sobre cinco órdenes de magnitud.
- ¿Cuántos municipios deciden el ajuste? → Ninguno. Dejando cada uno fuera, el AUC se mueve entre
  −0,020 y +0,004.
- ¿Hay fuga temporal? → Tres cierres verificables; ver §3 del manual técnico.
- ¿Por qué ocurrencia y no conteo? → Están los dos. El de ocurrencia es el principal por razón
  operativa: lo que una entidad hace con la salida es priorizar territorios.

---

## Cómo citar

> Beltrán, A. (2026). *Alerta territorial del Chocó: ordenamiento del riesgo de reclutamiento de
> NNA a partir del expediente del Caso 07 de la JEP*. Maestría en Ciencia de Datos, Universidad
> Ean, Bogotá.
