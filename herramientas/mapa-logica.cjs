// Uso: node herramientas/mapa-logica.cjs
// Necesita las devDependencies topojson-client y world-atlas (npm install).
// Fuente: Natural Earth (dominio público), empaquetada en world-atlas.

// Genera el trazo del Mediterráneo y Europa para la lámina de la página.
// Proyección equirrectangular con paralelo de referencia en 41°N: suficiente
// para una lámina estilizada y sin dependencias de proyección.
const topojson = require('topojson-client');
const topo = require('world-atlas/land-50m.json');
const f = topojson.feature(topo, topo.objects.land);
const polys = f.features ? f.features.flatMap(x => x.geometry.type === 'Polygon' ? [x.geometry.coordinates] : x.geometry.coordinates)
  : (f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates);

const LON0 = -11, LON1 = 50, LAT0 = 24, LAT1 = 59;
const W = 1200, k = Math.cos(41 * Math.PI / 180);
const sx = W / ((LON1 - LON0) * k);
const H = Math.round((LAT1 - LAT0) * sx);
const px = ([lon, lat]) => [ (lon - LON0) * k * sx, (LAT1 - lat) * sx ];
const dentro = ([lon, lat]) => lon >= LON0 - 6 && lon <= LON1 + 6 && lat >= LAT0 - 6 && lat <= LAT1 + 6;

const r = (n) => Math.round(n);
let d = [];
for (const poly of polys) {
  for (const anillo of poly) {
    if (!anillo.some(dentro)) continue;          // fuera del encuadre
    const pts = anillo.map(px);
    // simplificación por distancia mínima, para que el archivo no pese
    const out = [pts[0]];
    for (const p of pts.slice(1)) {
      const q = out[out.length - 1];
      if (Math.hypot(p[0] - q[0], p[1] - q[1]) > 3.2) out.push(p);
    }
    if (out.length < 9) continue;                  // islotes: fuera
    // area por la formula del cordon, para descartar manchas minusculas
    let a = 0;
    for (let i = 0; i < out.length; i++) {
      const [x1,y1] = out[i], [x2,y2] = out[(i+1) % out.length];
      a += x1*y2 - x2*y1;
    }
    if (Math.abs(a / 2) < 90) continue;
    d.push('M' + out.map(p => `${r(p[0])} ${r(p[1])}`).join('L') + 'Z');
  }
}
const trazo = d.join('');

const ESTACIONES = [
  ['Atenas',    37.98,  23.73],
  ['Alejandría',31.20,  29.92],
  ['Bagdad',    33.31,  44.36],
  ['Córdoba',   37.89,  -4.78],
  ['Toledo',    39.86,  -4.03],
  ['París',     48.86,   2.35],
  ['Leiden',    52.16,   4.49],
  ['Jena',      50.93,  11.59],
];
const puntos = ESTACIONES.map(([n, lat, lon]) => {
  const [x, y] = px([lon, lat]);
  return { n, x: r(x), y: r(y) };
});

const salida = 'src/datos/mapa-logica.json';
require('fs').writeFileSync(salida, JSON.stringify({ W, H, trazo, puntos }));
console.log(salida, '·', require('fs').statSync(salida).size, 'bytes · viewBox 0 0', W, H);
console.log(puntos.map((p) => `${p.n.padEnd(11)} ${p.x}, ${p.y}`).join('\n'));
