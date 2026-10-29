# Los once guiones de verificación

Cada guion recalcula una parte del trabajo desde los datos y deja su salida en `resultados/`.
Todos fijan `SEED = 42` y todos resuelven sus rutas **relativas al repositorio**: funcionan
después de un clon, sin ajustar nada.

```bash
pip install -r requirements.txt
cd verificacion
python 01_replica_del_cuaderno.py
```

El **01** es el primero por una razón: reconstruye el panel desde la fuente primaria incluida en
`../fuente/` y vuelve a estimar los modelos. Si sus veintitrés cifras salen idénticas a tres
decimales, todo lo que sigue se apoya en terreno firme. Los demás son independientes entre sí.

## Los primeros ocho: el piloto del Chocó

| guion | qué responde | tiempo |
|---|---|---|
| **01** `replica_del_cuaderno` | ¿Salen los 23 números del cuaderno reconstruyendo el panel desde la fuente? | ~15 s |
| **02** `rastreo_de_cifras` | ¿De qué población salió cada cifra publicada? Prueba 12 candidatas. | ~2 min |
| **03** `intervalos_y_calibracion` | Intervalos por remuestreo de bloques de municipio (B = 4.000), calibración, VIF, errores agrupados. | ~15 min |
| **04** `prueba_exacta_2026` | Permutación **exacta**: enumera las 736.281 maneras de repartir 6 ataques entre 31 municipios. | ~5 min |
| **05** `diagnosticos_de_panel` | Independencia de las filas, sensibilidad a C, influencia por municipio, Box–Tidwell. | ~5 min |
| **06** `simulacion_y_chequeo` | Simulación de 600 paneles con coeficientes conocidos; chequeo predictivo. | ~10 min |
| **07** `alarmas_y_defensoria` | Matriz de confusión a tres políticas y contraste con la Defensoría. | ~5 min |
| **08** `corredor_en_el_tiempo` | ¿Tiene el índice de corredor valor predictivo, o solo retrospectivo? | ~3 min |

El **08** es el único guion que refuta una hipótesis del propio trabajo, y por eso conviene leerlo
entero. El índice de corredor se construyó mirando los ataques de 2026, de modo que su AUC de 0,927
sobre esos seis ataques es circular. El guion hace lo contrario: reconstruye el índice año por año
con la coca anual del UNODC —disponible desde 1999— y lo confronta con el reclutamiento registrado
entre 2000 y 2016, que es anterior a los ataques y por tanto no pudo influir en la elección de sus
componentes. El resultado es AUC 0,470, con intervalo [0,358; 0,591] que contiene el azar, y una
ganancia de −0,005 al añadirlo al bloque de memoria. **El corredor no predice reclutamiento.**

## Los tres últimos: el contraste con una fuente externa

Los guiones 09 a 11 no usan el panel: usan los microdatos del proyecto conjunto entre la JEP, la
Comisión de la Verdad y el Human Rights Data Analysis Group, que integran treinta y cuatro listas
de registro y entregan cien réplicas de imputación múltiple. **Esa carpeta no está en el
repositorio** por tamaño: se descarga del catálogo 795 de microdatos del DANE y se pasa como
argumento.

```bash
python 09_contraste_con_verdata.py  /ruta/a/Reclutamiento.csv
python 10_memoria_bien_medida.py    /ruta/a/Reclutamiento.csv
python 11_cobertura_de_verdata.py   /ruta/a/Reclutamiento.csv
```

La ruta es la carpeta que contiene los cien archivos `verdata-reclutamiento-R*.csv`. Cada guion
imprime su modo de uso si se invoca sin argumento.

| guion | qué responde | tiempo |
|---|---|---|
| **09** `contraste_con_verdata` | ¿Coinciden los conteos? ¿Cambia el ordenamiento? ¿Qué queda fuera al contar solo la era FARC? ¿Estaban vacíos los cinco municipios sin registro? | ~4 min |
| **10** `memoria_bien_medida` | Si la memoria mal medida no ordena los ataques de 2026, ¿los ordena la memoria bien medida? Ocho operacionalizaciones. | ~8 min |
| **11** `cobertura_de_verdata` | ¿Cuánto cubre la fuente, cuánto se imputó, y hay masa suficiente para estimar subregistro por municipio? | ~4 min |

El **10** es la prueba que decide si el hallazgo central es real o un artefacto del alcance del
panel, y conviene leerlo junto al **09**. Las ocho medidas —todos los actores, solo FARC, sin FARC,
solo ELN, los últimos diez años, los últimos cinco, el panel propio y el semáforo publicado— dan
AUC entre 0,337 y 0,553, los ocho intervalos contienen 0,5 y ninguno de los ocho valores p baja de
0,20. El resultado no depende de cómo se mida la memoria.

## Una regla sobre la agregación de réplicas

Las cien réplicas **no se apilan ni se promedian fila a fila**. Cada cantidad se calcula dentro de
cada réplica y después se resume la distribución entre réplicas, que es la incertidumbre de lo
imputado. Y las réplicas en las que una categoría no aparece **valen cero, no se omiten**:
promediar solo sobre las réplicas donde algo aparece infla las categorías raras, que son
precisamente los municipios pequeños que interesan. De ahí el `reindex` explícito contra la lista
completa de réplicas en cada agregación del guion 09.

Una víctima es un `match_group_id`, no una fila.

## El atajo

Para comprobar una métrica sin reentrenar nada está `../datos/predicciones_fuera_de_muestra.csv`,
con las 341 predicciones fuera de muestra de los tres modelos. Cualquier métrica del trabajo se
recalcula desde ahí en dos líneas:

```python
import pandas as pd
from sklearn.metrics import roc_auc_score
p = pd.read_csv('../datos/predicciones_fuera_de_muestra.csv')
print(roc_auc_score(p.y, p.lr))   # 0,789
```

## Las salidas

Quedan en `resultados/`, en JSON y CSV. Los archivos que vienen en el repositorio son los de la
corrida que respalda lo publicado, y una corrida nueva los sobrescribe con los mismos valores, con
tres excepciones previsibles:

- los **tiempos de ejecución** que guardan los guiones 03 y 05, que dependen de la máquina;
- la **logística jerárquica** del guion 05, que se estima por inferencia variacional
  (`BinomialBayesMixedGLM`) y cuyo AUC se mueve alrededor de una milésima entre corridas aun con
  la semilla fija. Es la única cifra del repositorio que no es reproducible bit a bit, y se dice
  también en `docs/datos.html`;
- los **guiones 09 a 11**, cuyas cifras dependen de la versión de los microdatos descargada.

Todo lo demás sale idéntico a tres decimales.
