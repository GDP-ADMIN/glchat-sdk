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

import { processGLChatChunk, withValidation } from '@/api/lib';
import { CreateMessagePayloadSchema, type CreateMessagePayload, type GLChatMessageChunk } from './types';

/**
 * An API that serves as an interface to GLChat message-related API.
 *
 * Not to be used outside the main GLChat interface.
 */
export class MessageAPI {
  /**
   * An API that serves as an interface to GLChat message-related API.
   *
   * @params {typeof fetch} client Fetch API client, augmented with authentication data.
   */
  public constructor(
    private readonly client: typeof fetch,
  ) {}

  /**
   * Create a new message in an existing chatbot.
   *
   * @param {CreateMessagePayload} payload Message payload
   * @returns {Promise<AsyncIterable<GLChatMessageChunk>>} A promise that resolves
   * into a generator that produces message chunks.
   * @throws `ValidationError` if the payload is invalid.
   */
  @withValidation(CreateMessagePayloadSchema)
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

    const response = await this.client('message', {
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
