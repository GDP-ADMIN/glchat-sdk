/*
 * config.ts
 *
 * Collection objects and helper functions related
 * to GLChat client,
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

export const AVAILABLE_VERSION = ['v1'] as const;
export const DEFAULT_CONFIG: GLChatConfiguration = {
  baseUrl: 'https://stag-gbe-gdplabs-gen-ai-starter.obrol.id',
  __version: 'v1',
};

export interface GLChatConfiguration {
  /**
   * Base URL of the GLChat API.
   *
   * Useful for connecting to custom deployed instance or
   * testing between different environments.
   *
   * Defaults to `https://stag-gbe-gdplabs-gen-ai-starter.obrol.id`
   */
  baseUrl: string;
  /**
   * API version of the GLChat API.
   *
   * Currently unused.
   */
  __version: typeof AVAILABLE_VERSION[number];
}

/**
 * Validate the given configuration.
 *
 * @param {GLChatConfiguration} config Configuration to be validated
 * @throws Error when of
 */
export function validateConfiguration(config: Required<GLChatConfiguration>) {
  // validate baseUrl
  try {
    new URL(config.baseUrl);
  } catch {
    throw new Error('Invalid base URL. The base URL must be a valid URL');
  }

  // validate version
  if (!AVAILABLE_VERSION.includes(config.__version)) {
    throw new Error(`Invalid API version. Available API versions are: ${AVAILABLE_VERSION.join(', ')}`);
  }
}
