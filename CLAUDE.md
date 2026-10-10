# Instrucciones para Claude en este proyecto

- Sitio de Torre D. Babel (Alexander Beltrán). Trate siempre de usted y escriba en español cuidado.
- Textos: skill `voz-maestro-babel`. Aspecto: skill `estilo-libro-subrayado`.
- Lo público no usa lenguaje religioso ni referencias a One Piece: la idea de Babel se explica desde la filosofía.
  Sin autobombo: ni elogios a la empresa ni a Alex.
- La portada (`src/pages/index.astro` + `src/styles/pliego.css`) es copia exacta del artefacto aprobado
  https://claude.ai/artifact/VmnPr7B2d1jyD5f77t8ij3. Si se cambia, cambie primero el artefacto, cópielo aquí
  y compruebe que se ven igual a 1440, 768 y 390 px.
- Las páginas interiores comparten cabecera y pie (`marco.css`); el interior de cada pieza lleva su registro.
- Los logos están en `public/marcas/` y se pintan con máscara CSS: el color lo pone el estilo, no el archivo.
- Cada laboratorio de clase nuevo se publica aquí, en `/<curso><sesión en dos cifras>`
  (`/masvalendatos03`, `/diseñometricas03`), con `src/layouts/Clase.astro`: sin cabecera ni pie de
  Torre D. Babel; el pie solo dice «Brayeam Beltrán · babeltran@universidadean.edu.co». Si la
  dirección lleva eñe, se agrega la versión sin eñe en `redirects` de `astro.config.mjs`.
  Detalles en el README, sección «Laboratorios de clase».
- Antes de entregar: `npm run build` sin errores y revisión a 390, 768 y 1440 px de ancho.
