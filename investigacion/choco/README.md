# Alerta territorial del Chocó

Sistema de ordenamiento territorial del riesgo de reclutamiento de niñas, niños y adolescentes
en el departamento del Chocó, Colombia, construido sobre el expediente del **Caso 07** de la
Jurisdicción Especial para la Paz y siete fuentes oficiales más.

Trabajo de grado · Maestría en Ciencia de Datos, Universidad Ean
Alexander Beltrán · Bogotá, 2026

---

## Qué hay aquí

```
datos/            el panel y las bases derivadas, con su diccionario
cuaderno/         el cuaderno del modelo, con sus salidas guardadas
verificacion/     siete guiones que recalculan todo desde cero
docs/             una página de datos, medidas y desempeño
```

Lo que se publica en línea:

- **El tablero** — [torredbabel.com/choco](https://torredbabel.com/choco)
- **La separata técnica** — [torredbabel.com/choco-modelo](https://torredbabel.com/choco-modelo)

## Por dónde empezar

Si va a revisar el trabajo, lea **[MANUAL.md](MANUAL.md)**: está escrito para eso y dice en qué
orden mirar las cosas y qué atacar primero.

Si solo quiere las cifras, abra **[docs/datos.html](docs/datos.html)** en un navegador.

Si quiere comprobar que las cifras salen de los datos, corra los guiones de `verificacion/`
en orden. El primero reconstruye el panel desde la fuente primaria y replica los veintitrés
números del cuaderno; los veintitrés salen idénticos a tres decimales. Solo después de esa
réplica tiene sentido mirar lo demás.

```bash
pip install -r verificacion/requirements.txt
cd verificacion && python 01_replica_del_cuaderno.py
```

## La regla que gobierna todo lo demás

**Toda cifra de este trabajo es un piso, no una estimación.** El subregistro del conflicto
armado hace que lo registrado sea siempre menos que lo ocurrido, y ninguna técnica estadística
repara eso. Donde una fuente no desagrega, la celda queda vacía y marcada; no se imputa.

De ahí se sigue lo que el modelo puede prometer: **no predice reclutamiento, ordena territorios
por riesgo registrado**, que es una cantidad distinta y más modesta.

## Lo que no está aquí, a propósito

Ninguna salida de este trabajo muestra ubicaciones de grupos armados, rutas, ni dato alguno por
debajo del municipio. Un sistema que señala dónde hay niños reclutables es de doble uso, y la
omisión es parte del diseño, no una limitación de los datos. Ver **[ETICA.md](ETICA.md)**.

Tampoco está el expediente del Caso 07 en bruto, aunque llegue anonimizado. Lo que se publica
es el panel agregado a municipio-año que se deriva de él. Ver **[FUENTES.md](FUENTES.md)** para
el origen de cada dato y cómo obtenerlo.
