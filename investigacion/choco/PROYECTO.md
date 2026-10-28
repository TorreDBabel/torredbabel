# El proyecto en media página

## Qué buscamos responder

Colombia sabe advertir. La Defensoría del Pueblo emitió alertas tempranas en **30 de los 31
municipios del Chocó**, y los seis que fueron atacados con drones en 2026 estaban advertidos los
seis. Y sin embargo el número de alertas no distingue a los atacados del resto: 5,17 en promedio
frente a 5,24, con un valor p de 0,799. No es un fallo de la Defensoría —advertir donde hay
riesgo es su mandato, no repartir capacidad de respuesta—, pero deja intacto el problema de quien
responde con recursos finitos.

La pregunta del proyecto es, entonces, una sola: **cuando todo está advertido, ¿por dónde se
empieza?** El aporte posible no es advertir mejor, es **ordenar dentro de lo advertido**.

## Qué hace hoy

Hoy el sistema toma el archivo del daño —el expediente del Caso 07 de la JEP, más siete fuentes
oficiales— y lo convierte en un panel de 31 municipios por 34 años. Sobre ese panel estima, para
cada municipio y cada año, la probabilidad de que se registre reclutamiento de menores, usando
solo información anterior al año que predice.

La salida operativa no es una predicción sino una **prioridad**: tres niveles de alerta cuyo
nivel alto concentra el 77 % del daño en el 33 % del territorio, con una razón de tasas de 5,67
veces entre el nivel alto y el bajo. Priorizando solo cinco municipios al año —el 16 % del
departamento— cuatro de cada cinco alarmas aciertan.

Todo se reporta con su intervalo de confianza y contra su referencia de azar, y toda cifra se
entiende como un piso: el subregistro hace que lo registrado sea siempre menos que lo ocurrido.
El modelo no predice reclutamiento; ordena territorios por riesgo registrado, que es una cantidad
distinta y más modesta.

## Qué se proyecta que haga

El reclutamiento es el primer hecho, no el único. La arquitectura —panel municipio-año, variables
estrictamente rezagadas, validación de origen rodante, intervalos por remuestreo de municipios y
una política de alarma con su matriz de confusión— **no tiene nada específico del reclutamiento**.
Es un marco para cualquier hecho de violencia que deje registro territorial y fechado.

La ruta es sustituir la variable dependiente y repetir el procedimiento: desplazamiento forzado,
desaparición, homicidio, violencia sexual, amenazas a liderazgos sociales. Cada uno con su propia
calibración, sus propias variables de contexto y su propia validación, porque un modelo que
funciona para uno no se hereda a otro sin volver a probarlo.

Y hay un segundo eje, más ambicioso: pasar de ordenar **dónde** a ordenar **cuándo**. El índice
de corredor en disputa —geografía fluvial, economía de la coca y divergencia entre presente y
pasado— es la primera hipótesis en esa dirección, y está congelada y escrita para que la juzguen
desenlaces que todavía no han ocurrido.

## Lo que el proyecto no promete

No promete decir cuántas niñas y niños no fueron reclutados. Esa cifra no existe y no puede
construirse: un reclutamiento evitado no deja registro, y cualquier estimación de ese
contrafactual sería una invención. Lo que sí puede medirse, y es lo que medimos, es qué parte del
daño ocurrió en territorios que el sistema había priorizado antes, siempre junto a su costo
territorial.

Y falta lo que no depende del método. Sin una entidad que se comprometa a responder, el sistema
puede medir si acierta, pero no si sirve.
