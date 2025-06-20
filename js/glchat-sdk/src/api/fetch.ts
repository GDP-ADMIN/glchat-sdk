/*
 * fetch.ts
 *
 * Collection of fetch-related library to be consumed by resource endpoints.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import type { GLChatConfiguration } from '../config';

declare const __packageVersion: string;

/**
 * Get the User-Agent value that will be used during request.
 *
 * On the production build, the value of __packageVersion will be defined
 * and proper version will be used.
 *
 * Fallbacks to `dev` when the __packageVersion isn't available.
 *
 * @returns {string} User-Agent header value.
 */
function getUserAgent(): string {
  const version = typeof __packageVersion !== 'undefined' ? __packageVersion : 'dev';

  return `glchat-js-sdk@${version}`;
}

/**
 * Normalize various fetch-compatible header format to key-value map.
 *
 * @param {Headers} headers
 * @returns A simplified key-value map of HTTP headers.
 */
function normalizeHeaders(headers?: Headers): Record<string, string> {
  if (!headers) {
    return {};
  }

  if (headers instanceof Headers) {
    const result: Record<string, string> = {};
    headers.forEach((value, key) => {
      result[key] = value;
    });

    return result;
  }

  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }

  return headers;
}

/**
 * Bootstraps `fetch` with API key and existing configuration.
 *
 * This function simplifies the HTTP request code as it takes care
 * of authorization and footprinting.
 *
 * @param {string} apiKey GLChat API key that will be used to authorization
 * @param {GLChatConfiguration} config GLChat configuration object. Mainly
 * stores baseURL.
 * @returns {typeof fetch} A bootstrapped `fetch` function, without having
 * to handle authorization and extra logging.
 */
export function createGLChatFetchClient(
  apiKey: string,
  config: GLChatConfiguration,
): typeof fetch {
  return async (resource: string | URL | Request, options?: RequestInit) => {
    try {
      const url = new URL(resource, config.baseUrl);

      const response = await fetch(url, {
        ...options,
        headers: {
          ...normalizeHeaders(options?.headers as Headers),
          'Authorization': `Bearer ${apiKey}`,
          'User-Agent': getUserAgent(),
        },
      });

      if (!response.ok) {
        throw new Error('Response is not OK');
      }

      return response;
    } catch {
      throw new Error('Failed to fetch');
    }
  };
}
