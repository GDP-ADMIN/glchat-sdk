/*
 * types.ts
 *
 * Collection of types related with pipeline API.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: July 25th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import { z } from 'zod/v4';
import { UploadedFileSchema } from '../types';

export const PipelineFileSchema = UploadedFileSchema.refine(file =>
  file.type === 'application/zip',
);

export const UnregisterPluginSchema = z.array(z.string());
