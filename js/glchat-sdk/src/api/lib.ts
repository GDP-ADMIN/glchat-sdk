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

import { ChunkError, ValidationError } from '@/error';

import { ZodError, type ZodType } from 'zod/v4';
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

/**
 * Decorates a class-method to use Zod validation flow and automatically
 * convert it to `ValidationError` whenever the payload doesn't fulfill
 * the schema.
 *
 * @param {ZodType} schema Zod schema that will be used for validation.
 * @returns A function that decorates the target with validation flow.
 */
export function withValidation(schema: ZodType) {
  return function (
    _target: unknown,
    _key: string,
    descriptor: PropertyDescriptor,
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: unknown[]) {
      try {
        schema.parse(args[0]);

        return await originalMethod.apply(this, args);
      } catch (err) {
        if (err instanceof ZodError) {
          throw new ValidationError('payload', err);
        }

        // re-propagate, either it's already handled in other parts of the code.
        // or something unexpected.
        throw err;
      }
    };

    return descriptor;
  };
}
