/*
 * lib.ts
 *
 * Collection of helper functions for API that can't be included
 * in other files.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import type { GLChatMessageChunk, GLChatMessageStatus } from './message/types';

/**
 * Process raw chunk from stream into GLChat chunk objects.
 *
 * @param {unknown} value Raw chunk from API.
 * @returns {GLChatMessageChunk} Message chunk in object format.
 * @throws Error, if the chunk is not a string.
 */
export function processGLChatChunk(
  value: unknown,
): GLChatMessageChunk {
  if (typeof value !== 'string') {
    throw new Error('Chunk is corrupted!');
  }

  const stringChunk = value.replace(/^data:/, '');
  const rawChunk: { status: GLChatMessageStatus; message: string } = JSON.parse(stringChunk);

  return {
    ...rawChunk,
    message: rawChunk.status === 'data' ? JSON.parse(rawChunk.message) : rawChunk.message,
  } as GLChatMessageChunk;
}
