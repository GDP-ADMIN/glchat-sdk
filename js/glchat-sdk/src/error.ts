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
 * StandardSchema definiton.
 *
 * The base schema is directly copied from
 * https://github.com/standard-schema/standard-schema/blob/main/packages/spec/src/index.ts
 * to avoid extra dependencies and trimmed to remove unnecessary additions.
 */

// eslint-disable-next-line @typescript-eslint/no-namespace
declare namespace StandardSchemaV1 {
  /** The result interface if validation fails. */
  export interface FailureResult {
    /** The issues of failed validation. */
    readonly issues: readonly Issue[];
  }

  /** The issue interface of the failure output. */
  export interface Issue {
    /** The error message of the issue. */
    readonly message: string;
    /** The path of the issue, if any. */
    readonly path?: readonly (PropertyKey | PathSegment)[] | undefined;
  }

  /** The path segment interface of the issue. */
  export interface PathSegment {
    /** The key representing a path segment. */
    readonly key: PropertyKey;
  }
}

/**
 * A wrapper class for all GLChat related errors.
 *
 * For now, it contains nothing.
 */
export class GLChatError extends Error { }

/**
 * Errors that are thrown when the user-provided payload
 * doesn't satisfy the constraint.
 *
 * This error accepts a StandardSchema.FailureResult and extract the issues.
 */
export class ValidationError extends GLChatError {
  public readonly issues: readonly StandardSchemaV1.Issue[];

  constructor(public readonly object: string, err: StandardSchemaV1.FailureResult) {
    super(
      'Invalid payload. Please refer to `issues` for detailed information.',
    );

    this.issues = err.issues;
  }
}

/**
 * Errors that are thrown during API calls, including
 * data parsing.
 */
export class APIError extends GLChatError {
  constructor(message: string, public readonly status: number, public readonly headers: Headers) {
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
