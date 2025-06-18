/*
 * lib.ts
 *
 * Collection of helper functions for API that can't be included
 * in other files
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import type { MessageGenerationChunk } from './message/types';

export function processGLChatChunk(value: unknown): MessageGenerationChunk {
  if (typeof value !== 'string') {
    throw new Error('Chunk is corrupted!');
  }

  const stringChunk = value.replace(/^data:/, '');
  return JSON.parse(stringChunk) as MessageGenerationChunk;
}
