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

import { z, ZodType } from 'zod/v4';

const AVAILABLE_VERSION = ['v1'] as const;
export type APIVersion = typeof AVAILABLE_VERSION[number];

/**
 * Configuration object that will be used to interact with GLChat API.
 */
export interface GLChatConfiguration {
  /**
   * Required API key used for authentication to GLChat API.
   *
   * Defaults to `process.env.GLCHAT_API_KEY`.
   */
  apiKey: string;
  /**
   * Base URL of the GLChat API.
   *
   * Useful for connecting to custom deployed instance or
   * testing between different environments.
   *
   * Defaults to `process.env.GLCHAT_BASE_URL` or `https://chat.gdplabs.id/api/proxy/`
   * if the environment variable isn't available.
   */
  baseUrl: string;
  /**
   * Request timeout for API calls to GLChat API in milliseconds.
   *
   * Set to `0` to disable timeout
   *
   * Defaults to to `process.env.GLCHAT_TIMEOUT` or `60_000` if the environment
   * variable isn't available
   */
  timeout: number;
  /**
   * API version of the GLChat API.
   *
   * Currently unused.
   */
  __version: typeof AVAILABLE_VERSION[number];
}

/**
 * Zod schema object for GLChat configuration.
 */
export const GLChatConfigurationSchema = z.object({
  apiKey: z.string().optional().transform((val, ctx) => {
    const final = val ?? process.env.GLCHAT_API_KEY;

    if (!final) {
      ctx.addIssue({
        code: 'custom',
        message: 'GLChat API key is required!',
      });

      return z.NEVER;
    }

    return final;
  }),
  baseUrl: z.url({ error: 'Invalid base URL. The base URL must be a valid URL' })
    .default(() => process.env.GLCHAT_BASE_URL ?? 'https://chat.gdplabs.id/api/proxy/'),
  timeout: z
    .int()
    .nonnegative({ error: 'Timeout value must be a non-negative number' })
    .default(() => Number(process.env.GLCHAT_TIMEOUT ?? 60_000)),
  __version: z
    .enum(
      AVAILABLE_VERSION,
      { error: `Invalid API version. Available API versions are: ${AVAILABLE_VERSION.join(', ')}` },
    ).default('v1'),
}).strict() satisfies ZodType<GLChatConfiguration>;
