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
 * General error class.
 *
 * Extends the original `Error` object with the addition
 * of error codes for quicker error identification.
 */
export class GLChatError extends Error {
  constructor(message: string, public readonly code: string) {
    super(message);
  }
}

/**
 * Errors that doesn't belong to any other error.
 *
 * In normal scenario, this error shouldn't be thrown at all.
 */
export class GeneralError extends GLChatError {
  constructor(message: string) {
    super(message, 'GEN');
  }
}

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
      'Invalid payload. Please refer to the `issues` array for detailed information.',
      'INP',
    );
  }
}

/**
 * Errors that are thrown during API calls, including
 * data parsing.
 */
export class APIError extends GLChatError {
  constructor(message: string, code: string) {
    super(message, `API${code}`);
  }
}
