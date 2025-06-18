/*
 * message.ts
 *
 * Collection of API related with message manipulation in GLChat.
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import type { GLChatConfiguration } from '../../config';
import { glchatFetch } from '../fetch';
import { camelToSnakeCase } from '../lib';
import type { CreateMessagePayload } from './types';

export class MessageAPI {
  public constructor(private readonly configuration: GLChatConfiguration) {}

  /**
   * Create a new message in an existing chatbot.
   *
   * @param {CreateMessagePayload} payload Message payload
   * @returns {Promise<>} A promise neverland
   */
  public async create(payload: CreateMessagePayload) {
    const form = new FormData();
    const { files = [], additionalData = {}, ...rest } = payload;

    for (const [key, value] of Object.entries(additionalData)) {
      form.set(key, value);
    }

    // Use `set` to prevent duplicate keys
    for (const [key, value] of Object.entries(rest)) {
      form.set(camelToSnakeCase(key), value);
    }

    for (const [index, file] of files.entries()) {
      form.append(
        'files',
        file,
        file.name ?? `file_message_${(index + 1).toString()}.bin`,
      );
    }

    return glchatFetch('/message', this.configuration, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
      },
      body: form,
    });
  }
}
