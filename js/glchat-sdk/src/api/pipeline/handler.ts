/*
 * handler.ts
 *
 * Collection of functions and helpers related with pipeline
 * registry.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: July 25th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import { withValidation } from '@/api/lib';
import type { UploadedFile } from '@/api/types';
import {
  RegisterPluginSchema,
  UnregisterPluginSchema,
  type PipelineRegistrationResponse, type PipelineUnregistrationResponse,
} from './types';

/**
 * An API that serves as an interface to GLChat pipeline registry.
 *
 * Not to be used outside the main GLChat interface.
 */
export class PipelineAPI {
  /**
   * An API that serves as an interface to GLChat pipeline registry.
   *
   * @params {typeof fetch} client Fetch API client, augmented with authentication data.
  */
  public constructor(private readonly client: typeof fetch) {}

  /**
   * Register new pipeline(s) to GLChat pipeline registry.
   *
   * The pipelines must be packaged as a zip file. Please
   * consult our documentation for the complete schema of the
   * zip file.
   *
   * @param {UploadedFile} pipeline Schema of the pipeline packaged
   * as a zip file.
   * @returns {Promise<PipelineRegistrationResponse>} Pipeline registration
   * response. Stores the list of successfully registered pipeline plugins.
   * @throws `ValidationError` if the payload is invalid.
   */
  @withValidation(RegisterPluginSchema)
  public async register(
    pipeline: UploadedFile,
  ): Promise<PipelineRegistrationResponse> {
    const form = new FormData();

    form.append(
      'zip_file',
      pipeline,
      pipeline.name ?? 'plugin.zip',
    );

    const response = await this.client('register-pipeline-plugin', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      body: form,
    });

    const body = await response.json();

    return body as PipelineRegistrationResponse;
  }

  /**
   * Unregister a pipeline from GLChat pipeline registry.
   *
   * @param {string[]} pluginIds List of plugin identifiers to be removed from
   * GLChat pipeline registry. The plugin identifier should be returned during the
   * registration process.
   * @returns {Promise<PipelineUnregistrationResponse>} Pipeline unregistration response.
   * Stores the list of deleted pipeline plugins.
   * @throws `ValidationError` if the payload is invalid.
   */
  @withValidation(UnregisterPluginSchema)
  public async unregister(pluginIds: string[]): Promise<PipelineUnregistrationResponse> {
    const response = await this.client('unregister-pipeline-plugin', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        // needed to avoid bad request errors.
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(pluginIds),
    });

    const body = await response.json();

    return body as PipelineUnregistrationResponse;
  };
}
