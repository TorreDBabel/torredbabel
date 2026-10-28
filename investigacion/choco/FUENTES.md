# Fuentes

Ocho fuentes oficiales. Ninguna cifra de este trabajo se estima: cada una viene de una de estas
bases y se cita. Donde una fuente no desagrega, la celda queda vacía y marcada; no se imputa.

---

## 1. JEP · Caso 07 — expediente anonimizado

**Qué aporta.** Los hechos de reclutamiento con municipio y fecha. Es la variable que se modela.

**Granularidad.** Hecho, con código DIVIPOLA y año. Llega anonimizado: sin nombres, sin edades
individuales, sin ubicación por debajo del municipio.

**Conteo.** 401 hechos en el expediente; 361 con municipio y año identificados, que son los que
entran al panel. La reconciliación es exacta: 361 + 13 (sin municipio) + 25 (sin año) + 2 (fuera
de rango) = 401.

**Dónde está.** El expediente **no se redistribuye en este repositorio**, aunque llegue
anonimizado. Lo que se publica aquí es el panel agregado a municipio-año que se deriva de él
(`datos/panel_municipal_1983_2016.csv`). El acceso al expediente se gestiona con la JEP.

Los **autos de determinación de hechos y conductas** de los macrocasos, que suelen traer anexos
estadísticos, se consultan en el portal de la JEP: <https://www.jep.gov.co>

---

## 2. UARIV · Registro Único de Víctimas

**Qué aporta.** Casos y personas con código DANE y fecha. Sirve de contraste del conteo del
expediente y de validación de la serie departamental.

**Corte usado.** Marzo de 2026.

**Dónde se descarga.** <https://www.unidadvictimas.gov.co/registro-unico-de-victimas-ruv/>
y el portal de datos abiertos: <https://www.datos.gov.co>

---

## 3. UARIV · Cifras de víctimas por hecho, nacional

**Qué aporta.** Desagregación nacional por hecho victimizante, sexo, etnia, discapacidad y ciclo
vital. Se usa para situar el Chocó dentro del país y para la caracterización.

**Volumen.** 287.555 filas en el corte de agosto de 2026.

**Dónde se descarga.** <https://www.datos.gov.co> — buscar «Cifras de Víctimas por Hechos».

---

## 4. UNODC–SIMCI · Cultivos ilícitos

**Qué aporta.** Hectáreas de coca por municipio y año. Entra como variable de contexto económico
y es el componente de mayor peso individual en el índice de corredor.

**Dónde se descarga.** <https://www.unodc.org/colombia/es/simci/simci.html> y el visor
de datos del SIMCI.

---

## 5. Defensoría del Pueblo · Alertas tempranas

**Qué aporta.** Tres series por municipio: alertas tempranas, alertas estructurales y alertas de
inminencia. **No entra al modelo**: se usa para contrastar nuestro ordenamiento con el de quien
ya advierte en el territorio.

**Limitación declarada.** Tenemos el **conteo acumulado** por municipio, no el inventario de
alertas con su fecha. Sin fecha no se puede saber si una alerta precede o sigue al riesgo que el
modelo estima, de modo que lo que medimos es concordancia y no anticipación. Conseguir ese
inventario es uno de los pendientes del trabajo.

**Dónde se consulta.** <https://alertastempranas.defensoria.gov.co/>

---

## 6. OCHA · Eventos humanitarios

**Qué aporta.** Eventos humanitarios registrados entre 2016 y 2025. Alimenta la variable de
actividad contemporánea, que es la que permite medir la divergencia entre presente y pasado.

**Dónde se consulta.** <https://www.humanitarianresponse.info/es/operations/colombia>
y <https://data.humdata.org>

---

## 7. DANE · Población y áreas municipales

**Qué aporta.** Proyecciones de población municipal (denominadores de las tasas) y áreas
municipales 1985–2020.

**Dónde se descarga.** <https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/proyecciones-de-poblacion>

---

## 8. Geometrías municipales y trazos fluviales

**Qué aporta.** Contornos de los 31 municipios, usados para el mapa y para calcular la
ribereñidad. Los trazos de los ríos Atrato, San Juan y Baudó se densifican a pasos de 0,02 grados
y se mide la distancia perpendicular de punto a segmento desde cada cabecera municipal.

**Dónde se descarga.** Marco geoestadístico nacional del DANE:
<https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/>

---

## Cómo se unen

Todo se une por **código DIVIPOLA**, nunca por nombre. Los nombres del Chocó varían entre fuentes
—tildes, «Nuevo Belén de Bajirá», «El Cantón del San Pablo»— y unir por texto habría perdido
municipios en silencio.

La rejilla municipio-año se construye como producto cartesiano completo (31 × 34) y luego se le
hace el conteo por la izquierda, de modo que los municipio-año sin hecho quedan en **cero
explícito**. Las bases oficiales llegan en formato largo y solo traen las filas con evento; los
ceros hay que fabricarlos a propósito, y sin ellos un modelo de ocurrencia no se puede estimar.

## Una advertencia sobre el cero

Un cero en este panel **no dice que no hubo reclutamiento**: dice que no hay registro de
reclutamiento. Las dos cosas se confunden en el mismo símbolo, y la distancia entre ellas es la
cobertura del aparato estatal en el departamento con menor densidad institucional del país.
Cinco de los 31 municipios no registran un solo hecho en 34 años; uno de ellos, Río Iró, fue
atacado con drones en 2026.
