// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// La dirección pública del sitio. Se usa para el mapa del sitio y los enlaces canónicos.
export default defineConfig({
  site: 'https://torredbabel.com',
  trailingSlash: 'ignore',
  integrations: [sitemap()],
});
