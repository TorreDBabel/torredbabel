# Los siete guiones

Corren en orden. Cada uno es independiente salvo que se indique, y todos fijan `SEED = 42`.

```bash
pip install -r requirements.txt
python 01_replica_del_cuaderno.py     # obligatorio: deja panel_modelable.csv y pool_rodante.csv
python 02_rastreo_de_cifras.py
python 03_intervalos_y_calibracion.py
python 04_prueba_exacta_2026.py
python 05_diagnosticos_de_panel.py
python 06_simulacion_y_chequeo.py
python 07_alarmas_y_defensoria.py
```

| guion | qué responde | tiempo |
|---|---|---|
| **01** | ¿Salen los 23 números del cuaderno reconstruyendo el panel desde la fuente? | ~10 s |
| **02** | ¿De qué población salió cada cifra publicada? Prueba 12 candidatas. | ~2 min |
| **03** | Intervalos por remuestreo de bloques (B = 4.000), calibración, VIF, errores agrupados. | ~15 min |
| **04** | Permutación **exacta**: enumera las 736.281 asignaciones de 6 ataques entre 31 municipios. | ~5 min |
| **05** | Independencia de las filas, sensibilidad a C, influencia por municipio, Box–Tidwell. | ~5 min |
| **06** | Simulación de 600 paneles con coeficientes conocidos; chequeo predictivo. | ~10 min |
| **07** | Matriz de confusión a tres políticas y contraste con la Defensoría. | ~5 min |

Los resultados quedan en `resultados/*.json`. Los que ya están en el repositorio son los de
nuestra corrida; si los suyos difieren, es un hallazgo y nos interesa saberlo.

## Rutas

Los guiones esperan encontrar los datos en rutas absolutas de la máquina donde se escribieron.
Para correrlos aquí, ajuste la constante de ruta al principio de cada uno, o sitúese en la raíz
del repositorio y use:

```bash
python - <<'EOF'
import pathlib, re, sys
raiz = pathlib.Path('.').resolve()
for p in pathlib.Path('verificacion').glob('*.py'):
    t = p.read_text(encoding='utf-8')
    t = t.replace('/home/claude/curaduria', str(raiz / 'datos'))
    t = t.replace('/home/claude/base_drones.csv', str(raiz / 'datos/base_municipal_corredor.csv'))
    t = t.replace('/home/claude/base_municipal.csv', str(raiz / 'datos/base_municipal.csv'))
    t = t.replace('/mnt/user-data/uploads/', str(raiz / 'datos') + '/')
    p.write_text(t, encoding='utf-8')
print('rutas ajustadas a', raiz)
EOF
```

El guion **01** necesita además el archivo original de series municipales, que no se
redistribuye aquí; si no lo tiene, empiece por el **03**, que parte de
`datos/panel_modelable_1984_2016.csv`, ya incluido.

## El atajo

Si solo quiere comprobar una métrica y no reentrenar nada, use
`datos/predicciones_fuera_de_muestra.csv`: trae las 341 predicciones fuera de muestra de los tres
modelos. Cualquier métrica del trabajo se recalcula desde ahí en dos líneas.
