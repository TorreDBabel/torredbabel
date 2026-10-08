// Colección de artículos: cada archivo .md en src/content/articulos es una página.
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const articulos = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articulos' }),
  schema: z.object({
    titulo: z.string(),
    descripcion: z.string().max(170, 'La descripción para buscadores debe tener 170 caracteres o menos.'),
    fecha: z.coerce.date(),
    bajada: z.string().optional(),
    apertura: z.string().optional(),
    epigrafe: z
      .object({ texto: z.string(), autor: z.string(), obra: z.string().optional(), lugar: z.string().optional() })
      .optional(),
    aforismo: z.string().optional(),
    notas: z.array(z.string()).optional(),
    imagen: z.string().optional(),
    borrador: z.boolean().default(false),
  }),
});

export const collections = { articulos };
