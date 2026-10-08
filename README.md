# torredbabel.com

Sitio de Torre D. Babel, hecho con [Astro](https://astro.build) y publicado en GitHub Pages.

## La portada se publica idéntica al diseño aprobado

La portada (`src/pages/index.astro`) es copia exacta del artefacto «Torre D. Babel» del
8 de octubre de 2026: el mismo marcado, la misma hoja de estilos (`src/styles/pliego.css`) y el
mismo guion de transiciones. La única diferencia son dos enlaces más en el menú: Artículos y Demos.

Se comprobó comparando las dos versiones píxel por píxel, pantalla por pantalla, a 1440, 768 y
390 px de ancho: la diferencia fue de 0 %. Las letras (Playfair Display, Spectral, Archivo y
Space Mono) viajan dentro del sitio, así que no dependen de Google ni cambian con el tiempo.

Para que siga así: no edite `pliego.css` ni el marcado de la portada sin revisar el resultado con
`npm run dev` en escritorio y en celular.

## Qué hay en el proyecto

| Ruta | Qué es |
| --- | --- |
| `src/pages/index.astro` | La portada (registro Pliego) |
| `src/styles/pliego.css` | El estilo de la portada, idéntico al del artefacto aprobado |
| `src/styles/marco.css` | La cabecera con el logo principal y el pie con la firma, para las páginas interiores |
| `src/styles/libro.css` | El interior de los artículos y demos (registro Libro subrayado) |
| `src/content/articulos/` | Un archivo `.md` por artículo. Cada uno es una página propia |
| `src/pages/demos/index.astro` | La página de demos |
| `src/layouts/Pliego.astro` | Plantilla de la portada |
| `src/layouts/Base.astro` | Plantilla de las páginas interiores: cabecera, pie y datos para buscadores |
| `src/layouts/Articulo.astro` | La plantilla de cada artículo |
| `src/components/Cabeza.astro` | Título, descripción e imagen para Google y redes sociales |
| `src/sitio.ts` | Razón social, NIT, correo, teléfono, sello y descripción del sitio |
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

## Comandos

| Comando | Qué hace |
| --- | --- |
| `npm install` | Instala lo necesario (una vez, o al cambiar de computador) |
| `npm run dev` | Abre el sitio en `http://localhost:4321` para revisar |
| `npm run build` | Construye el sitio final en la carpeta `dist/` |
| `npm run preview` | Muestra en el navegador lo que se construyó en `dist/` |
