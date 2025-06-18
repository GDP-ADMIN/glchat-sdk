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

import { MessageAPI } from './api/message/handler';

import type { APIVersion, GLChatConfiguration } from './config';
import { normalizeConfig, validateConfiguration } from './config';

/**
 * API client that serves as an interface to interact with GLChat
 */
export class GLChat {
  private configuration: GLChatConfiguration;

  /**
   * Collection of interfaces to interact with message API of
   * GLChat.
   */
  public message: MessageAPI;

  public constructor(config: Partial<GLChatConfiguration> = {}) {
    const normalizedConfig = normalizeConfig(config);
    validateConfiguration(normalizedConfig);

    this.configuration = normalizedConfig;
    this.message = new MessageAPI(this.configuration);
  }

  /**
   * Sets the base URL that will be used for API calls.
   *
   * @param {string} url Base URL to be used
   * @throws Error, if the provided URL isn't a valid URL.
   */
  public setBaseUrl(url: string): void {
    const newConfig: GLChatConfiguration = {
      ...this.configuration,
      baseUrl: url,
    };
    validateConfiguration(newConfig);

    this.configuration = newConfig;
  }

  /**
   * Sets the API version that will be used for API calls.
   *
   * @param {string} version API version to be used
   * @throws Error, if the provided version isn't available.
   */
  public setAPIVersion(version: APIVersion): void {
    const newConfig: GLChatConfiguration = {
      ...this.configuration,
      __version: version,
    };
    validateConfiguration(newConfig);

    this.configuration = newConfig;
  }
}
