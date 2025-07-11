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
export class ValidationError extends Error {
  constructor(public readonly object: string, public readonly issues: ValidationIssue[]) {
    super(
      'Invalid payload. Please refer to the `issues` array for detailed information.',
    );
  }
}

/**
 * Errors that are thrown during API calls, including
 * data parsing.
 */
export class APIError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
  }
}

/**
 * Errors that are thrown when the API request timed out
 */
export class TimeoutError extends Error {
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
export class ChunkError extends Error {
  constructor(message: string, public readonly type: 'raw' | 'data') {
    super(message);
  }
}
