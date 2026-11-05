// Datos del sitio en un solo lugar. Si cambia el correo, se cambia aquí, en la portada (src/pages/index.astro)
// y en el formulario (src/components/Formulario.astro). El contacto público es el correo y el formulario de
// /contacto/: no se publican teléfono ni NIT.
export const SITIO = {
  nombre: 'Torre D. Babel',
  razonSocial: 'Torre D. Babel S.A.S.',
  descripcion:
    'Torre D. Babel: aprovechamos los datos de su organización y optimizamos los procesos que los producen, con el marco de la ISO 9001:2026. Bogotá.',
  correo: 'contacto@torredbabel.com',
  sello: 'De la riqueza del corazón, la palabra.',
  idioma: 'es-CO',
};
