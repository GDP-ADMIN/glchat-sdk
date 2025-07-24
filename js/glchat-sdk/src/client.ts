/*
 * client.ts
 *
 * Base client to interact with GLChat API.
 *
 * Encloses all available API in one compact class that
 * simulates namespaces.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import { ZodError } from 'zod/v4';
import { createGLChatFetchClient } from './api/fetch';
import { MessageAPI } from './api/message/handler';

import type { APIVersion, GLChatConfiguration } from './config';
import { GLChatConfigurationSchema } from './config';
import { ValidationError } from './error';

/**
 * API client that serves as an interface to interact with GLChat
 */
export class GLChat {
  /**
   * Configuration object that will be used to interact with GLChat API.
   */
  private readonly configuration: GLChatConfiguration;

  /**
   * Collection of interfaces to interact with message API of
   * GLChat.
   */
  public readonly message: MessageAPI;

  /**
   * API client that serves as an interface to interact with GLChat.
   *
   * @param {Partial<GLChatConfiguration>} config GLChat configuration object
   * @throws `ValidationError` if the provided configuration isn't valid.
   */
  public constructor(config: Partial<GLChatConfiguration> = {}) {
    try {
      this.configuration = GLChatConfigurationSchema.parse(config);

      const fetchClient = createGLChatFetchClient(this.configuration);

      this.message = new MessageAPI(fetchClient);
    } catch (err) {
      if (err instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          err.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw err;
    }
  }

  /**
   * Sets the base URL that will be used for API calls.
   *
   * @param {string} url Base URL to be used
   * @returns {GLChat} The current GLChat client instance.
   * @throws `ValidationError` if the provided base URL isn't valid.
   */
  public setBaseUrl(url: string): GLChat {
    try {
      GLChatConfigurationSchema.parse({
        ...this.configuration,
        baseUrl: url,
      });

      this.configuration.baseUrl = url;

      return this;
    } catch (err) {
      if (err instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          err.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw err;
    }
  }

  /**
   * Sets the API version that will be used for API calls.
   *
   * @param {string} version API version to be used.
   * @returns {GLChat} The current GLChat client instance.
   * @throws `ValidationError` if the provided version isn't valid.
   */
  public setAPIVersion(version: APIVersion): GLChat {
    try {
      GLChatConfigurationSchema.parse({
        ...this.configuration,
        __version: version,
      });

      this.configuration.__version = version;

      return this;
    } catch (err) {
      if (err instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          err.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw err;
    }
  }

  /**
   * Sets the global API timeout that will be used for API calls.
   *
   * Set to `0` to disable timeout.
   *
   * @param {number} timeout Timeout value in milliseconds.
   * @returns {GLChat} The current GLChat client instance.
   * @throws `ValidationError` if the provided timeout isn't valid.
   */
  public setTimeout(timeout: number): GLChat {
    try {
      GLChatConfigurationSchema.parse({
        ...this.configuration,
        timeout,
      });

      this.configuration.timeout = timeout;

      return this;
    } catch (err) {
      if (err instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          err.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw err;
    }
  }
}
