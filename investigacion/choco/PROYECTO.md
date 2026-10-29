# El proyecto, en dos partes

Un archivo del daño explica la guerra que lo produjo. La pregunta es si explica la siguiente, y la
respuesta no se supone: se mide. El Chocó tiene treinta y cuatro años de reclutamiento registrado,
de 1983 a 2016, y seis municipios atacados con drones en 2026. Entre esas dos fechas hay un acuerdo
de paz, y el trabajo consiste en medir qué sobrevive a él y qué no.

El proyecto va en dos partes. La primera establece qué permitía saber ese archivo en su momento, con
su margen. La segunda describe el terreno que se está preparando para responder lo que la primera
dejó abierto. Cada parte cierra con sus conclusiones.

---

# Primera parte · Lo que el archivo permitía saber

## El contexto, y por qué el Caso 07

El **Caso 07** de la Jurisdicción Especial para la Paz investiga el reclutamiento y la utilización
de niñas, niños y adolescentes en el conflicto armado. Su expediente es la única fuente que reúne
hecho, municipio y año con criterio judicial, y es la variable dependiente de todo el trabajo: 401
hechos, de los cuales 361 tienen municipio y año y entran al panel. Los 40 restantes se reportan
aparte y no se imputan.

El Chocó no es un caso elegido por conveniencia. Es el departamento con menor densidad institucional
del país, el que concentra la disputa posterior al acuerdo entre el ELN y las estructuras surgidas
de la desmovilización de las FARC-EP, y el que en 2026 registró los primeros ataques con drones
contra población civil. Es, además, el territorio donde la distancia entre lo ocurrido y lo
registrado es mayor, lo que obliga a tratar cada cifra como un piso.

## Qué se construyó

El expediente, más ocho fuentes oficiales, se convierte en un panel de **municipio-año**: 31
municipios por 34 años, 1.054 filas. La rejilla se construye completa, con los municipio-año sin
hecho en **cero explícito**, porque las bases oficiales solo traen las filas con evento y sin los
ceros un modelo de ocurrencia no se puede estimar.

Sobre ese panel se estima, para cada municipio y cada año, la probabilidad de que se registre
reclutamiento, usando **solo información anterior al año que predice** y validando con origen
rodante: once ventanas, el modelo reajustado desde cero en cada una, 341 observaciones fuera de
muestra.

La salida no es una predicción: es una **prioridad**. El modelo no dice dónde habrá reclutamiento,
ordena territorios por riesgo registrado, que es una cantidad distinta y más modesta.

## Las variables exógenas, y cuál de ellas resultó decisiva

Al bloque de memoria histórica —nueve variables derivadas de la propia serie, todas rezagadas— se
añadieron variables de contexto para probar si aportan algo:

| variable exógena | fuente | qué aportó |
|---|---|---|
| hectáreas de coca, anuales | UNODC–SIMCI, desde 1999 | nada sobre el reclutamiento anterior al acuerdo (AUC 0,526, casi el azar); **ordena los ataques de 2026 con 0,780** |
| cercanía a los ríos Atrato, San Juan y Baudó | geometrías del DANE | −0,002 de ganancia sobre el bloque de memoria |
| alertas tempranas acumuladas | Defensoría del Pueblo | concordancia, no anticipación: faltan las fechas |
| eventos humanitarios 2016–2025 | OCHA | describe el régimen posterior, no el anterior |
| población y área municipal | DANE | normalización de tasas |

El resultado más informativo de esa tabla es la primera fila. La coca, medida con la misma fuente y
el mismo método, no explica dónde se reclutó antes del acuerdo y sí ordena dónde cayeron los ataques
de 2026. Una variable, dos respuestas opuestas según a qué fenómeno se le pregunte: no dice dónde
hay niñas y niños reclutables, dice dónde hay algo por lo que valga la pena pelear.

## Lo que se midió, con su estado

| afirmación | estado |
|---|---|
| El archivo ordena el territorio **antes** del acuerdo. AUC-ROC 0,788 contra una línea base de persistencia de 0,714; semáforo monótono con razón de tasas de 5,67 entre el nivel alto y el bajo; el nivel alto cubre el 77 % del daño con el 33 % del territorio; precisión@5 de 0,836. | demostrado, fuera de muestra, con intervalos |
| Ese mismo archivo **deja de ordenar** después del acuerdo. Sobre los seis ataques de 2026 el intervalo del AUC contiene el azar, y las ocho maneras de medir la memoria dan el mismo resultado. | demostrado como ausencia de señal, no como señal invertida |
| La disputa por corredores **no explica** el reclutamiento anterior al acuerdo: AUC de 0,470 sobre 527 municipio-año, y añadirla al modelo da −0,005. | demostrado |
| La disputa por corredores explica la violencia **posterior** al acuerdo: AUC de 0,927 sobre seis ataques. | hipótesis: el índice se construyó viendo el desenlace |
| El sistema previene reclutamientos. | no afirmable, y no lo será: un reclutamiento evitado no deja registro |

## Conclusiones de la primera parte

**1. El archivo ordenaba el territorio, y se puede decir con cuánta precisión.** AUC-ROC de 0,788
contra una línea base de 0,714, fuera de muestra y en once ventanas sucesivas. El nivel alto del
semáforo concentra el 77 % del daño registrado en el 33 % del territorio, y de los cinco municipios
priorizados cada año, cuatro registraron hecho.

**2. Ese ordenamiento era lo que faltaba, no la advertencia.** La Defensoría del Pueblo emitió
alertas tempranas en 30 de los 31 municipios, y los seis atacados en 2026 estaban los seis
advertidos. Pero el número de alertas no los distingue del resto —5,17 frente a 5,24, con p de
0,799—, de modo que advertir no repartía prioridad. Donde todo está advertido, un orden defendible
es la pieza que no existía.

**3. Nada de esto requería datos que no existieran.** Las nueve fuentes son oficiales y todas
anteriores a los ataques de 2026; ocho de ellas son de descarga abierta, y el panel completo se
reconstruye desde una sola con un guion. Lo que no existía no era el dato ni la técnica: era el panel
con el cero explícito y la validación que permite leer cada cifra con su margen.

**4. El instrumento tiene fecha de caducidad, y está medida.** Un sistema construido sobre este
archivo habría ordenado bien hasta 2016 y habría dejado de hacerlo después. La propia serie avisa del
cambio: en 2017, el primer año tras el acuerdo, el ELN pasa a explicar el 68,4 % del reclutamiento
registrado en el Chocó frente al 26,4 % de las FARC-EP.

**5. El punto ciego más caro era de alcance, no de método.** Contar solo los hechos atribuidos a las
antiguas FARC-EP dejó fuera el 58,2 % del fenómeno y puso a Bajo Baudó en el puesto 23 del semáforo y en su nivel
bajo del semáforo, cuando en la fuente independiente ocupa el puesto 4 y su serie crece justo antes
del acuerdo. Fue atacado en 2026. La corrección no exige un modelo nuevo: exige contar todos los
actores.

---

# Segunda parte · El terreno que se está preparando

## El macrocontexto de violencia, y qué hay ya disponible

El piloto mide un fenómeno —reclutamiento— atribuido a un actor —las antiguas FARC-EP— en un
departamento. Las tres restricciones se levantan con material que ya existe.

La novena fuente del trabajo es la estimación conjunta de la **JEP, la Comisión de la Verdad y el
Human Rights Data Analysis Group**: integra treinta y cuatro listas de registro y reconstruye
**19.226 víctimas únicas** de reclutamiento en **808 municipios** entre 1990 y 2017, con presunto
responsable, sexo, etnia y edad, y cien réplicas de imputación múltiple que propagan la
incertidumbre de lo imputado en lugar de esconderla. Está en el catálogo 795 de microdatos del DANE,
de descarga abierta.

Con ella, el Chocó deja de ser el universo y pasa a ser el 3,4 % de un material que cabe veintinueve
veces. La rejilla pasa de 1.054 municipio-año a más de veintidós mil; las unidades independientes,
de 31 a 808, que es lo que hoy limita cada intervalo; y la variable dependiente deja de ser «hechos
de un actor» para ser «víctimas de todos los actores».

## Las cuatro brechas, y de dónde se cierran

Ninguna de las cuatro es una técnica que no sepamos aplicar. Son datos que están en entidades
identificadas, y la vía para pedirlos son derechos de petición con destinatario y plazo.

| lo que falta | qué permitiría | dónde está |
|---|---|---|
| **Alertas de la Defensoría con fecha** — hoy solo el conteo acumulado | pasar de medir *concordancia* a medir *anticipación*: saber si una alerta precede o sigue al riesgo estimado | Defensoría del Pueblo, Sistema de Alertas Tempranas |
| **Reclutamiento registrado 2017–2026** — la serie termina en 2016 | probar el corredor contra el fenómeno que dice explicar, en vez de contra seis ataques; convertiría la hipótesis en resultado | JEP, UARIV |
| **Estimación del subregistro** — primer paso ya dado | separar «no hubo» de «no se registró», que es el límite duro del trabajo | ya en la novena fuente: 19 municipios chocoanos con 10 o más víctimas y 13 con 10 o más vistas en dos fuentes o más |
| **Variables de contexto anuales** — hoy solo la coca lo es | población flotante, deserción escolar, minería, presencia institucional: harían del corredor un índice vivo y no una fotografía | DANE, Ministerio de Educación, Agencia Nacional de Minería |

## Lo que no se hereda al subir de escala

Las ocho fuentes de contexto son del Chocó. La coca del UNODC y la población del DANE son nacionales
y anuales, pero las alertas de la Defensoría, los eventos de OCHA y las geometrías fluviales habría
que reconstruirlos para cada departamento, y la ribereñidad del Atrato no tiene equivalente en un
departamento sin ríos navegables. Un panel nacional no es este panel con más filas: es una decisión
nueva sobre qué variables son comparables entre territorios que no se parecen.

Tampoco se hereda el régimen. El cambio que se mide para el Chocó —memoria que ordena antes del
acuerdo y no después— puede tener otra fecha, otro signo u otra causa en el Catatumbo o en el Cauca,
y afirmarlo sin medirlo repetiría exactamente el error que este trabajo documenta.

## Conclusiones de la segunda parte

**1. Lo demostrado y lo propuesto quedan separados, con su estado explícito.** Tres afirmaciones
están medidas fuera de muestra y con intervalos; una es hipótesis, porque su índice se construyó
viendo el desenlace; y una no será afirmable con ningún diseño.

**2. Lo que falta son datos, no técnicas.** Las cuatro brechas se cierran con información que existe
en entidades identificadas, y la estrategia de solicitud está documentada con destinatario, norma y
plazo.

**3. El material para la escala nacional ya está en la mano.** 808 municipios, 19.226 víctimas
únicas, 34 listas y 100 réplicas, en una fuente oficial de descarga abierta.

**4. Subir de escala estrecha los intervalos y amplía la variable dependiente, pero no traslada el
hallazgo.** Pasar de 31 a 808 unidades independientes es lo que hoy limita cada cifra; contar todos
los actores corrige el punto ciego medido. Lo que no se puede trasladar es el cambio de régimen: en
cada territorio hay que volver a medirlo.

**5. El límite que no se mueve es el otro.** El sistema puede medir si ordena bien y con cuánto
margen; no puede medir si sirve mientras no haya una entidad que se comprometa a responder con
capacidad finita según ese orden. Esa parte no es estadística.

---

## La regla que gobierna las dos partes

**Toda cifra de este trabajo es un piso, no una estimación.** El subregistro del conflicto armado
hace que lo registrado sea siempre menos que lo ocurrido, y ninguna técnica estadística repara eso.
Donde una fuente no desagrega, la celda queda vacía y marcada; no se imputa.

De ahí se sigue lo que el modelo puede prometer: **no predice reclutamiento, ordena territorios por
riesgo registrado**. Y lo que no promete: decir cuántas niñas y niños no fueron reclutados. Esa
cifra no existe y no puede construirse, porque un reclutamiento evitado no deja registro.
