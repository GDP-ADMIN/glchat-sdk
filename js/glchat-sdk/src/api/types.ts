/*
 * types.ts
 *
 * Collection of types and zod schemas that are shared across all API.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: July 25th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */
import { z } from 'zod/v4';

/**
 * Custom file type of files for message-related functionality.
 *
 * Mainly made to maintain runtime-compatibility with Bun, since Bun
 * doesn't support `File` natively.
 */
export interface UploadedFile extends Blob {
  readonly name?: string;
}

export const UploadedFileSchema = z.instanceof(Blob).refine(
  (file): file is UploadedFile => !('name' in file) || typeof (file as UploadedFile).name === 'string',
);
