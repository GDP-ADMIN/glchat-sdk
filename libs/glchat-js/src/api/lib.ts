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

/**
 * Transform camel-cased string to snake_cased one.
 *
 * Used to transform payload keys to snake_cased keys
 * that the API understands.
 *
 * @param {string} camelString A camelCase string
 * @returns {string} Snake_cased variant of the input string.
 */
export function camelToSnakeCase(camelString: string): string {
  return camelString.replace(/([a-z0-9])([A-Z])/g, '$1_$2').toLowerCase();
}
