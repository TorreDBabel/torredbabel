# El proyecto en media página

## Qué buscamos responder

Un archivo del daño explica la guerra que lo produjo. La pregunta es si explica la siguiente, y
la respuesta no se supone: se mide.

El Chocó tiene treinta y cuatro años de reclutamiento registrado, de 1983 a 2016. Ese archivo
ordena el territorio con solidez **dentro del régimen que lo produjo**, y deja de ordenarlo
después del acuerdo de paz. Entender ese corte —cuándo un instrumento sigue valiendo y cuándo
hay que cambiarlo— es el problema del trabajo.

Hay una segunda pregunta, operativa, que viene del propio territorio. La Defensoría del Pueblo
emitió alertas tempranas en **30 de los 31 municipios**, y los seis atacados con drones en 2026
estaban advertidos los seis. Pero el número de alertas no los distingue del resto: 5,17 frente a
5,24, con un valor p de 0,799. No es un fallo de la Defensoría —advertir donde hay riesgo es su
mandato, no repartir capacidad de respuesta—, pero deja intacto el problema de quien responde con
recursos finitos. Cuando todo está advertido, ¿por dónde se empieza?

## Qué hace hoy

Toma el expediente del Caso 07 de la JEP más siete fuentes oficiales y los convierte en un panel
de 31 municipios por 34 años. Sobre él estima, para cada municipio y cada año, la probabilidad de
que se registre reclutamiento, usando solo información anterior al año que predice y validando
con origen rodante: once ventanas, el modelo reajustado desde cero en cada una.

La salida no es una predicción sino una **prioridad**, con tres resultados demostrados y uno
propuesto:

| afirmación | estado |
|---|---|
| El archivo ordena el territorio **antes** del acuerdo. AUC-ROC 0,788 contra una línea base de 0,714; semáforo monótono con razón de tasas de 5,67 entre el nivel alto y el bajo; el nivel alto cubre el 77 % del daño con el 33 % del territorio. | demostrado |
| Ese mismo archivo **deja de ordenar** después del acuerdo. Sobre los ataques de 2026 el intervalo del AUC contiene el azar. | demostrado como ausencia de señal |
| La disputa por corredores **no explica** el reclutamiento anterior al acuerdo: AUC de 0,470, y añadirla al modelo da −0,005. | demostrado |
| La disputa por corredores explica la violencia **posterior** al acuerdo: AUC de 0,927 sobre seis ataques. | hipótesis: el índice se construyó viendo el desenlace |

Las tres primeras son el aporte verificable. La cuarta es lo que propone probar.

Todo se reporta con su intervalo de confianza y contra su referencia de azar, y toda cifra se
entiende como un piso: el subregistro hace que lo registrado sea siempre menos que lo ocurrido.
El modelo no predice reclutamiento; ordena territorios por riesgo registrado.

## Qué se proyecta que haga

Cuatro cosas faltan, y ninguna es una técnica que no sepamos aplicar: son datos que no tenemos.
Las **alertas de la Defensoría con fecha**, que convertirían la concordancia que medimos en
anticipación. El **reclutamiento registrado de 2017 a 2026**, que permitiría probar el corredor
contra el fenómeno que dice explicar en vez de contra seis ataques. La **estimación del
subregistro** por captura-recaptura, que separaría «no hubo» de «no se registró». Y **variables
de contexto anuales** —hoy solo la coca lo es— que harían del corredor un índice vivo y no una
fotografía.

Más allá: la arquitectura —panel municipio-año, variables estrictamente rezagadas, validación de
origen rodante, intervalos por remuestreo de unidades y una política de alarma con su matriz de
confusión— **no tiene nada específico del reclutamiento**. Sustituir la variable dependiente por
desplazamiento, desaparición, homicidio o amenazas a liderazgos es técnicamente directo.

Lo que no se hereda es la validación. Cada fenómeno exige su propia calibración y su propia
prueba, y la prueba del corredor es justamente la demostración de por qué: un instrumento que
funciona en un régimen puede valer cero en otro, y solo medirlo lo revela.

## Lo que el proyecto no promete

No promete decir cuántas niñas y niños no fueron reclutados. Esa cifra no existe y no puede
construirse: un reclutamiento evitado no deja registro, y cualquier estimación de ese
contrafactual sería una invención. Lo que sí puede medirse es qué parte del daño ocurrió en
territorios que el sistema había priorizado antes, siempre junto a su costo territorial.

Y falta lo que no depende del método. Sin una entidad que se comprometa a responder, el sistema
puede medir si acierta, pero no si sirve.
