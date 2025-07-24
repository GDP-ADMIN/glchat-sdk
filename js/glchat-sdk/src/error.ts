/*
 * error.ts
 *
 * Collection of custom errors for GLChat
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 25th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

/**
 * A wrapper class for all GLChat related errors.
 *
 * For now, it contains nothing.
 */
export class GLChatError extends Error {}

/**
 * Issues present in the schema.
 */
interface ValidationIssue {
  /**
   * Human-readable message related with the error.
   */
  message: string;
  /**
   * Object path related with the schema.
   */
  path: string[];
}

/**
 * Errors that are thrown when the user-provided payload
 * doesn't satisfy the constraint.
 */
export class ValidationError extends GLChatError {
  constructor(public readonly object: string, public readonly issues: ValidationIssue[]) {
    super(
      'Invalid payload. Please refer to `issues` for detailed information.',
    );
  }
}

/**
 * Errors that are thrown during API calls, including
 * data parsing.
 */
export class APIError extends GLChatError {
  constructor(message: string, public readonly status: number) {
    super(message);
  }
}

/**
 * Errors that are thrown when the API request timed out
 */
export class TimeoutError extends GLChatError {
  constructor() {
    super('Request timed out');
  }
}

/**
 * Errors that are thrown when the SDK tries
 * to parse invalid chunk.
 *
 * Consist of 2 types:
 *   1. `raw`, which signifies that the chunk itself is not a valid JSON.
 *   2. `data`, which signifies that the data chunk is not a valid JSON.
 *
 * Unlikely to be thrown.
 */
export class ChunkError extends GLChatError {
  constructor(message: string, public readonly type: 'raw' | 'data') {
    super(message);
  }
}

/**
 * Errors that are thrown when `fetch` request failed due to possible
 * network errors.
 *
 * Since the actual cause may vary, this error wraps the original error
 * in scope of `GLChatError`.
 */
export class NetworkError extends GLChatError {
  constructor(public readonly originalError: Error) {
    super(
      'Failed to process request due to network error. Please refer to `originalError` for detailed information.',
    );
  }
}
