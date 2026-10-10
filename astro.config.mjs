import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://torredbabel.com',
  base: '/',
  // Las clases con eñe en la dirección también se abren sin ella (teclados, QR y mensajes).
  redirects: {
    '/disenometricas03': '/diseñometricas03/',
  },
});
