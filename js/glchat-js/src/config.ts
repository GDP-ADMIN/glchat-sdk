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

const AVAILABLE_VERSION = ['v1'] as const;
export const DEFAULT_CONFIG: GLChatConfiguration = {
  baseUrl: 'https://stag-chat-ui-gdplabs-gen-ai-starter.obrol.id/api/proxy/',
  __version: 'v1',
};

export type APIVersion = typeof AVAILABLE_VERSION[number];

export interface GLChatConfiguration {
  /**
   * Base URL of the GLChat API.
   *
   * Useful for connecting to custom deployed instance or
   * testing between different environments.
   *
   * Defaults to `https://stag-chat-ui-gdplabs-gen-ai-starter.obrol.id/api/proxy/`
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
 * Normalize user-provided configuration by providing default values
 * if the field value is nullish.
 *
 * @param {Partial<Configuration>} config User-provided configuration
 * @returns {GLChatConfiguration} A normalized version
 */
export function normalizeConfig(config: Partial<GLChatConfiguration>): GLChatConfiguration {
  return {
    ...DEFAULT_CONFIG,
    ...Object.fromEntries(Object.entries(config).filter(([_, v]) => v)),
  };
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
