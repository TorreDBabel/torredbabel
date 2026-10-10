# torredbabel.com

Sitio de Torre D. Babel, hecho con [Astro](https://astro.build) y publicado en GitHub Pages.

## La portada se publica idéntica al diseño aprobado

La portada (`src/pages/index.astro`) es copia exacta del artefacto «Torre D. Babel · Noche clara»
(https://claude.ai/artifact/HFjH4CdTu5KDdfQRmXSPDA), aprobado el 10 de octubre de 2026: el mismo
marcado, la misma hoja de estilos (`src/styles/noche.css`) y el mismo guion del cielo, la torre y la
constelación. Las diferencias son solo de lugar: los enlaces a Artículos y Demos son internos, los
logos salen de `public/marcas/` y el formulario de contacto vive en `src/components/Formulario.astro`
(el mismo bloque, con la dirección de envío para quien navega sin guion).

Se comprobó comparando las dos versiones píxel por píxel, pantalla por pantalla, a 1440, 768 y
390 px de ancho, con el cielo quieto: la diferencia fue de 0 %. Las letras (Bitter, Outfit y
Chivo Mono) viajan dentro del sitio, así que no dependen de Google ni cambian con el tiempo.

Para que siga así: cambie primero el artefacto, cópielo aquí y compare de nuevo. No edite
`noche.css` ni el marcado de la portada sin revisar el resultado con `npm run dev` en escritorio y
en celular. La portada anterior (registro Pliego, «De ruido a criterio») queda en el historial del
repositorio.

## Qué hay en el proyecto

| Ruta | Qué es |
| --- | --- |
| `src/pages/index.astro` | La portada (registro Noche clara) |
| `src/styles/noche.css` | El estilo de la portada, idéntico al del artefacto aprobado |
| `src/components/Formulario.astro` | El formulario de contacto (ver «El formulario de contacto») |
| `src/pages/contacto/` | La página de contacto y la de agradecimiento, en Noche clara |
| `src/styles/contacto.css` | Lo propio de las páginas de contacto: el cielo quieto y la torre de estrellas |
| `src/styles/marco.css` | La cabecera con el logo principal y el pie con la firma, para las páginas interiores |
| `src/styles/libro.css` | El interior de los artículos y demos (registro Libro subrayado) |
| `src/content/articulos/` | Un archivo `.md` por artículo. Cada uno es una página propia |
| `src/pages/demos/index.astro` | La página de demos |
| `src/clases/` y `src/layouts/Clase.astro` | Los laboratorios de clase, uno por sesión (ver «Laboratorios de clase») |
| `src/layouts/Noche.astro` | Plantilla del registro Noche clara: letras y estilo de la portada |
| `src/layouts/NocheMarco.astro` | Cabecera, pie y apertura corta de las páginas de contacto |
| `src/layouts/Base.astro` | Plantilla de las páginas interiores: cabecera, pie y datos para buscadores |
| `src/layouts/Articulo.astro` | La plantilla de cada artículo |
| `src/components/Cabeza.astro` | Título, descripción e imagen para Google y redes sociales |
| `src/sitio.ts` | Razón social, correo, sello y descripción del sitio (no se publican NIT ni teléfono) |
| `public/marcas/` | Los dos logos: `torre.png` (principal) y `firma.png` (la firma D'Babel) |
| `public/` | Ícono, imagen para redes, `CNAME` y `robots.txt` |
| `.github/workflows/publicar.yml` | Publica el sitio cada vez que usted sube cambios |

---

## Paso a paso: del computador a torredbabel.com

Necesita una cuenta de GitHub, Git y Node.js 22 o más reciente instalados en su computador.
Los pasos 1 a 5 se hacen una sola vez.

### 1. Ver el sitio en su computador

Descomprima la carpeta, ábrala en una terminal y ejecute:

```bash
npm install
npm run dev
```

Abra `http://localhost:4321` en el navegador. Mientras `npm run dev` siga corriendo, cada cambio
que guarde se ve al instante. Para detenerlo, presione `Ctrl + C`.

### 2. Crear el repositorio en GitHub

1. En GitHub, pulse **New repository**.
2. Nombre: `torredbabel` (o el que prefiera).
3. Visibilidad: **Public**. GitHub Pages es gratuito para repositorios públicos; para uno privado
   se necesita un plan pago.
4. No marque ninguna opción de README, `.gitignore` ni licencia: el proyecto ya los trae.
5. Pulse **Create repository** y deje abierta esa página.

### 3. Subir el proyecto

En la terminal, dentro de la carpeta del proyecto (cambie `SU-USUARIO` por su usuario de GitHub):

```bash
git init
git add .
git commit -m "Primera versión del sitio"
git branch -M main
git remote add origin https://github.com/SU-USUARIO/torredbabel.git
git push -u origin main
```

### 4. Activar GitHub Pages

1. En el repositorio, vaya a **Settings → Pages**.
2. En **Build and deployment → Source**, elija **GitHub Actions**.
3. Vaya a la pestaña **Actions**. Verá el flujo «Publicar el sitio» en marcha. Si no arrancó,
   ábralo y pulse **Run workflow**.
4. Cuando termine con una marca verde (uno o dos minutos), el sitio queda en una dirección
   provisional que aparece en **Settings → Pages**.

### 5. Conectar el dominio torredbabel.com

**En GitHub:** en **Settings → Pages → Custom domain**, escriba `torredbabel.com` y pulse **Save**.
El archivo `public/CNAME` del proyecto ya lleva ese dominio.

**En Squarespace:** entre a **Domains → torredbabel.com → DNS** y agregue estos registros:

| Tipo | Host | Valor |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | SU-USUARIO.github.io |

> **Cuidado con el correo.** No borre los registros **MX** ni los **TXT** que ya existan
> (SPF, DKIM, verificaciones de Google). De ellos depende que babeltran@torredbabel.com siga
> recibiendo correo. Si Squarespace muestra registros **A** o **CNAME www** predeterminados que
> apuntan a Squarespace, elimine solo esos, porque chocan con los de GitHub.

Los cambios de DNS tardan desde minutos hasta 24 horas. Cuando GitHub confirme el dominio,
vuelva a **Settings → Pages** y marque **Enforce HTTPS**.

**Recomendado:** en la configuración de **su cuenta** de GitHub (no del repositorio), en
**Settings → Pages → Add a domain**, verifique torredbabel.com con el registro TXT que GitHub le
indique. Así nadie más puede usar su dominio en GitHub.

### 6. Que Google lo encuentre

1. Entre a [Google Search Console](https://search.google.com/search-console) y agregue la
   propiedad de tipo **Dominio**: `torredbabel.com`.
2. Google le dará un registro **TXT**. Agréguelo en el DNS de Squarespace, igual que en el paso 5.
3. Ya verificado, vaya a **Sitemaps** y envíe `https://torredbabel.com/sitemap-index.xml`.
   El mapa solo anuncia lo que se alcanza desde el menú (portada, artículos, demos y contacto);
   los laboratorios de clase y las páginas que se comparten por enlace no se anuncian
   (se decide en `astro.config.mjs`).

Google suele tardar entre unos días y algunas semanas en mostrar un sitio nuevo. Cada artículo
lleva título, descripción, fecha e imagen para buscadores y redes sociales.

---

## Publicar un artículo nuevo

1. Copie `src/content/articulos/que-es-una-venta.md` con un nombre nuevo, en minúsculas y con
   guiones: `src/content/articulos/el-dato-y-la-pregunta.md`. Ese nombre será la dirección:
   `torredbabel.com/articulos/el-dato-y-la-pregunta/`.
2. Cambie los datos del encabezado (entre las dos líneas `---`):

```yaml
titulo: "El dato y la pregunta"
descripcion: "Lo que aparece en Google bajo el título. Máximo 170 caracteres."
fecha: 2026-10-20
bajada: "Una o dos frases que abren el artículo."
apertura: "Una pregunta o una apuesta que va antes del título (opcional)."
epigrafe:            # opcional
  texto: "La cita, sin comillas."
  autor: "Autor"
  obra: "Obra"
  lugar: "Capítulo o año"
aforismo: "La frase que se lleva el lector (opcional)."
notas:               # notas de método y fuentes (opcional)
  - "De dónde salen los datos o la cita."
borrador: false      # true = no se publica todavía
```

Ponga los textos entre comillas: así un signo de dos puntos dentro de una frase no rompe nada.

3. Escriba el cuerpo en Markdown. Para los resaltadores use estas marcas, con el sentido de siempre:

```html
<mark class="oro">lo que se suele creer</mark>
<mark class="rosa">lo que muestra el dato</mark>
<mark class="lino">el contexto</mark>
<span class="pluma">La única frase subrayada de la sección.</span>
```

Subraye poco: menos de una de cada diez palabras.

4. Revise con `npm run dev` y publique:

```bash
git add .
git commit -m "Artículo: El dato y la pregunta"
git push
```

En uno o dos minutos el artículo está en línea y aparece en la lista de `/articulos/`.

## Agregar una demo

- **Demo que corre en el navegador** (como la de «¿Cuánto se vendió en septiembre?»): se escribe
  en `src/pages/demos/index.astro` o en una página nueva dentro de `src/pages/demos/`. Sirve para
  ejercicios con JavaScript, Python en el navegador (Pyodide o JupyterLite), consultas SQL
  (DuckDB-WASM) o apps de Streamlit (stlite). No necesita servidor.
- **Demo que necesita un servidor** (un modelo pesado, una base de datos, una máquina virtual):
  vive en otro servicio y se muestra dentro de la página con el componente `DemoExterno`:

```astro
---
import DemoExterno from '../../components/DemoExterno.astro';
---
<DemoExterno titulo="Pronóstico de demanda" src="https://demos.torredbabel.com/pronostico/" />
```

## El formulario de contacto

La portada (sección «Conversemos») y `torredbabel.com/contacto/` tienen el mismo formulario. El
mensaje sale de la página y llega a babeltran@torredbabel.com por medio de
[FormSubmit](https://formsubmit.co), un servicio gratuito que no pide cuenta ni servidor propio.
La cabecera y el pie de las páginas interiores llevan a `/contacto/`.

**Activación, una sola vez.** FormSubmit no entrega nada hasta que el dueño del correo lo
confirma:

1. Con el sitio ya publicado, abra `torredbabel.com/contacto/` y envíese un mensaje de prueba.
   Puede que la página diga que no se pudo enviar: antes de activar, es normal.
2. En babeltran@torredbabel.com llegará un correo de FormSubmit con el botón **Activate Form**.
   Púlselo. Si no lo ve, busque en el correo no deseado.
3. Envíe otro mensaje de prueba, ahora desde la portada. Debe llegarle como una tabla con nombre,
   correo, organización, mensaje y la autorización. Si FormSubmit pide activar de nuevo para esa
   página, repita el paso 2.

**Cómo funciona.**

- Con guion (casi todos los visitantes), el mensaje se envía sin salir de la página y aparece
  un agradecimiento con el correo al que se responderá. Si el envío falla, el texto queda en el
  formulario y la página ofrece el correo para escribir desde el programa de cada quien.
- Sin guion, el formulario va a FormSubmit, que pide confirmar que no es un robot y vuelve a
  `/contacto/gracias/`.
- Para responder, basta con **Responder** en el correo: la respuesta va a quien escribió.
- Contra el correo basura hay un campo trampa invisible (`_honey`): si un robot lo llena, el
  mensaje no se envía.

**Datos personales (Ley 1581 de 2012).** El formulario pide solo lo necesario para responder y
una autorización expresa, obligatoria, que dice para qué se usan los datos, que viajan por
FormSubmit y que este guarda una copia, y cómo pedir que se corrijan o se borren.

**Si cambia el correo,** cámbielo en `src/sitio.ts`; en `src/components/Formulario.astro` (las dos
direcciones de FormSubmit, la nota de la autorización y el enlace `mailto:` con su texto); en el pie
de la portada (`src/pages/index.astro`) y en el artefacto. Después vuelva a activar el formulario.
Después de la activación, FormSubmit ofrece una dirección cifrada para usar en lugar del correo
dentro del formulario; es opcional, porque el correo ya es público en la página.

## Laboratorios de clase

Cada laboratorio de clase vive en una dirección con el curso y el número de la sesión, para
seguir el curso lección por lección:

| Dirección | Curso | Sesión |
| --- | --- | --- |
| `torredbabel.com/masvalendatos03` | Más valen datos que percepciones (AFPN0087) | 3 · Laboratorio del promedio |
| `torredbabel.com/diseñometricas03` | Diseño de métricas para el marketing (AFPN0097) | 3 · Laboratorio de adquisición |

- Son material de clase: no llevan la cabecera ni el pie de Torre D. Babel, ni el nombre del
  docente. Lo importante es el mensaje: el pie trae solo el correo de contacto.
- Cada uno tiene tres archivos con el mismo nombre de la dirección:
  `src/clases/<dirección>/laboratorio.css` (estilo), `src/clases/<dirección>/laboratorio.html`
  (cuerpo y guion) y `src/pages/<dirección>.astro` (título, descripción y letras). La plantilla
  común es `src/layouts/Clase.astro`.
- El estilo y el cuerpo son copia del laboratorio publicado como artefacto; se corrigen en su
  fuente y se vuelven a copiar, no se editan aquí a mano. La única diferencia es que las letras
  las aloja el sitio, como en el resto de las páginas.
- Si la dirección lleva eñe, agregue en `astro.config.mjs` la versión sin eñe, que lleva a la
  original: `/disenometricas03` abre `/diseñometricas03`.
- La sesión siguiente es otra dirección (`masvalendatos04`); las anteriores no se borran.

## Comandos

| Comando | Qué hace |
| --- | --- |
| `npm install` | Instala lo necesario (una vez, o al cambiar de computador) |
| `npm run dev` | Abre el sitio en `http://localhost:4321` para revisar |
| `npm run build` | Construye el sitio final en la carpeta `dist/` |
| `npm run preview` | Muestra en el navegador lo que se construyó en `dist/` |
