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
import { GeneralError, ValidationError } from './error';

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
  public message: MessageAPI;

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
      const error = err as Error;

      if (error instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          error.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw new GeneralError(error.message);
    }
  }

  /**
   * Sets the base URL that will be used for API calls.
   *
   * @param {string} url Base URL to be used
   * @throws `ValidationError` if the provided base URL isn't valid.
   */
  public setBaseUrl(url: string): void {
    try {
      GLChatConfigurationSchema.parse({
        ...this.configuration,
        baseUrl: url,
      });

      this.configuration.baseUrl = url;
    } catch (err) {
      const error = err as Error;

      if (error instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          error.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw new GeneralError(error.message);
    }
  }

  /**
   * Sets the API version that will be used for API calls.
   *
   * @param {string} version API version to be used
   * @throws `ValidationError` if the provided version isn't valid.
   */
  public setAPIVersion(version: APIVersion): void {
    try {
      GLChatConfigurationSchema.parse({
        ...this.configuration,
        __version: version,
      });

      this.configuration.__version = version;
    } catch (err) {
      const error = err as Error;

      if (error instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          error.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw new GeneralError(error.message);
    }
  }

  /**
   * Sets the global API timeout that will be used for API calls.
   *
   * Set to `0` to disable timeout.
   *
   * @param {number} timeout Timeout value in milliseconds.
   * @throws `ValidationError` if the provided timeout isn't valid.
   */
  public setTimeout(timeout: number): void {
    try {
      GLChatConfigurationSchema.parse({
        ...this.configuration,
        timeout,
      });

      this.configuration.timeout = timeout;
    } catch (err) {
      const error = err as Error;

      if (error instanceof ZodError) {
        throw new ValidationError(
          'configuration',
          error.issues.map(
            issue => ({ path: issue.path as string[], message: issue.message })));
      }

      throw new GeneralError(error.message);
    }
  }
}
