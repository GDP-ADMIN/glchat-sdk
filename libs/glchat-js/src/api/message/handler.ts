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
import { processGLChatChunk } from '../lib';
import type { CreateMessagePayload, GLChatMessageChunk } from './types';

export class MessageAPI {
  public constructor(private readonly configuration: GLChatConfiguration) {}

  /**
   * Create a new message in an existing chatbot.
   *
   * @param {CreateMessagePayload} payload Message payload
   * @returns {Promise<AsyncIterable<GLChatMessageChunk>>} A promise that resolves
   * into a generator that produces message chunks.
   */
  public async create(
    payload: CreateMessagePayload,
  ): Promise<AsyncIterable<GLChatMessageChunk>> {
    const form = new FormData();
    const {
      files = [],
      additional_data = {},
      ...rest
    } = payload;

    // Populate form with additional data and other payload fields
    const combinedEntries = [
      ...Object.entries(additional_data),
      ...Object.entries(rest),
    ];
    for (const [key, value] of combinedEntries) {
      form.set(key, value);
    }

    for (const [index, file] of files.entries()) {
      form.append(
        'files',
        file,
        file.name ?? `file_message_${(index + 1).toString()}.bin`,
      );
    }

    const response = await glchatFetch('/message', this.configuration, {
      method: 'POST',
      headers: {
        Accept: 'text/event-stream',
      },
      body: form,
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    return {
      async* [Symbol.asyncIterator]() {
        if (!reader) throw new Error('No response body');

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const rawChunk = decoder.decode(value as ArrayBuffer, { stream: true });
            yield processGLChatChunk(rawChunk);
          }
        } finally {
          reader.releaseLock();
        }
      },
    };
  }
}
