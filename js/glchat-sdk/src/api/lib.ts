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

import { ChunkError } from '@/error';

import type { GLChatMessageChunk, GLChatMessageStatus } from './message/types';

/**
 * Process raw chunk from stream into GLChat chunk objects.
 *
 * @param {unknown} value Raw chunk from API.
 * @returns {GLChatMessageChunk} Message chunk in object format.
 * @throws GeneralError, if the chunk is not a string.
 */
export function processGLChatChunk(
  value: unknown,
): GLChatMessageChunk {
  if (typeof value !== 'string') {
    throw new ChunkError('Chunk is not a string', 'raw');
  }

  const stringChunk = value.replace(/^data:/, '');

  let rawChunk: { status: GLChatMessageStatus; message: string };
  try {
    rawChunk = JSON.parse(stringChunk);
  } catch {
    throw new ChunkError('Chunk is not a valid JSON', 'raw');
  }

  let parsedMessage;
  try {
    parsedMessage = rawChunk.status === 'data' ? JSON.parse(rawChunk.message) : rawChunk.message;
  } catch {
    throw new ChunkError('Data chunk is not a valid JSON', 'data');
  }

  return {
    ...rawChunk,
    message: parsedMessage,
  } as GLChatMessageChunk;
}
