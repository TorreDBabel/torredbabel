# Alerta territorial del Chocó

Sistema de ordenamiento territorial del riesgo de reclutamiento de niñas, niños y adolescentes en el
departamento del Chocó, Colombia, construido sobre el expediente del **Caso 07** de la Jurisdicción
Especial para la Paz y ocho fuentes oficiales más, y contrastado con una novena de alcance nacional.

Trabajo de grado · Maestría en Ciencia de Datos, Universidad Ean
Alexander Beltrán · Bogotá, 2026 · **versión 1.0**

---

## El trabajo, en dos partes

**Primera parte — lo que el archivo permitía saber.** El Chocó tiene treinta y cuatro años de
reclutamiento registrado, de 1983 a 2016. Ese archivo ordena el territorio con solidez dentro del
régimen que lo produjo —AUC-ROC de 0,788 fuera de muestra contra una línea base de 0,714, con el
nivel alto del semáforo cubriendo el 77 % del daño en el 33 % del territorio— y deja de ordenarlo
después del acuerdo de paz. Las dos cosas están medidas, con su intervalo y contra su referencia de
azar.

**Segunda parte — el terreno que se está preparando.** Una fuente independiente de la JEP, la
Comisión de la Verdad y el Human Rights Data Analysis Group cubre 808 municipios con 19.226 víctimas
únicas entre 1990 y 2017. Con ella se midió el alcance real del panel —cuenta el 41,8 % del
fenómeno— y queda identificado lo que falta para llevar el método al resto del país.

El argumento completo, con las conclusiones de cada parte, está en
**[PROYECTO.md](PROYECTO.md)**.

## Qué hay aquí

```
fuente/           las dos fuentes primarias, tal como llegan
datos/            el panel y las bases derivadas, con su diccionario
cuaderno/         el cuaderno del modelo, con sus salidas guardadas
verificacion/     once guiones que recalculan todo desde cero
docs/             una página de datos, medidas y desempeño, y el glosario
```

Lo que se publica en línea:

- **El tablero** — [torredbabel.com/choco](https://torredbabel.com/choco)
- **La separata técnica** — [torredbabel.com/choco-modelo](https://torredbabel.com/choco-modelo)

## Por dónde empezar

**[MANUAL.md](MANUAL.md)** es el manual de lectura: dice qué contiene cada carpeta, dónde está cada
base de datos, cómo se encadenan unas con otras y en qué orden leerlas según lo que se busque. Trae
tres recorridos —uno de media hora sin correr nada, uno de dos horas y uno de reproducción
completa— y la lista de limitaciones con su medición.

Si solo quiere las cifras, abra **[docs/datos.html](docs/datos.html)** en un navegador.

Si quiere comprobar que las cifras salen de los datos, el primer guion reconstruye el panel desde la
fuente primaria incluida en `fuente/` y replica los veintitrés números del cuaderno, idénticos a
tres decimales. Todos los guiones resuelven sus rutas relativas al repositorio: funcionan después de
un clon, sin ajustar nada.

```bash
pip install -r verificacion/requirements.txt
cd verificacion && python 01_replica_del_cuaderno.py
```

## La regla que gobierna todo lo demás

**Toda cifra de este trabajo es un piso, no una estimación.** El subregistro del conflicto armado
hace que lo registrado sea siempre menos que lo ocurrido, y ninguna técnica estadística repara eso.
Donde una fuente no desagrega, la celda queda vacía y marcada; no se imputa.

De ahí se sigue lo que el modelo puede prometer: **no predice reclutamiento, ordena territorios por
riesgo registrado**, que es una cantidad distinta y más modesta.

## Lo que no está aquí, a propósito

Ninguna salida de este trabajo muestra ubicaciones de grupos armados, rutas, ni dato alguno por
debajo del municipio. Un sistema que señala dónde hay niños reclutables es de doble uso, y la
omisión es parte del diseño, no una limitación de los datos. Ver **[ETICA.md](ETICA.md)**.

Tampoco está el expediente del Caso 07 en bruto, aunque llegue anonimizado. Lo que se publica es su
agregado a municipio-año, que es la unidad de análisis. Y tampoco los microdatos de la novena
fuente, por tamaño: son 397 MB y se descargan del catálogo 795 de microdatos del DANE. Ver
**[FUENTES.md](FUENTES.md)** para el origen de cada dato y cómo obtenerlo.
