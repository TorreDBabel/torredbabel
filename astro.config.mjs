import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://torredbabel.com',
  base: '/',
  // El mapa del sitio para los buscadores (sitemap-index.xml, el que anuncian robots.txt y el README).
  // Solo anuncia lo que ya se alcanza desde el menú: portada, artículos, demos y contacto. Las páginas que
  // se comparten por enlace (laboratorios de clase, visores, /choco) no se anuncian.
  integrations: [
    sitemap({
      filter: (pagina) => {
        const ruta = new URL(pagina).pathname;
        if (ruta.startsWith('/contacto/gracias')) return false;
        return ruta === '/' || ['/articulos/', '/demos/', '/contacto/'].some((r) => ruta.startsWith(r));
      },
    }),
  ],
  // Las clases con eñe en la dirección también se abren sin ella (teclados, QR y mensajes).
  redirects: {
    '/disenometricas03': '/diseñometricas03/',
  },
});
