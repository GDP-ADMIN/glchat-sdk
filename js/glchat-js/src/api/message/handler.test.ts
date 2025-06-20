import { describe, expect, it } from 'vitest';
import { ZodError } from 'zod/v4';
import { createGLChatFetchClient } from '../fetch';
import { MessageAPI } from './handler';
import type { CreateMessagePayload } from './types';

describe('MessageAPI', () => {
  const client = createGLChatFetchClient({
    apiKey: 'API-KEY',
    timeout: 0,
    baseUrl: 'https://test.glchat.id',
    __version: 'v1',
  });

  describe('create', () => {
    it('should throw a ZodError if the payload is invalid', async () => {
      const payload = {
        chatbot_id: 123,
        message: 'AAAAAAAAA',
      };

      const handler = new MessageAPI(client);

      await expect(() => handler.create(payload as unknown as CreateMessagePayload)).rejects.toThrow(ZodError);
    });

    it('should stream basic message correctly', async () => {
      const payload: CreateMessagePayload = {
        chatbot_id: 'general-purpose',
        message: 'hello world',
      };

      const handler = new MessageAPI(client);
      const stream = await handler.create(payload);

      let result = '';
      for await (const chunk of stream) {
        if (chunk.status === 'response') {
          result += chunk.message;
        }
      }

      expect(result).toBe('hello world!');
    });

    it('should handle files in the payload', async () => {
      const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
      const payload: CreateMessagePayload = {
        chatbot_id: 'general-purpose',
        message: 'hello world',
        files: [file],
      };

      const handler = new MessageAPI(client);
      const stream = await handler.create(payload);

      let result = '';
      for await (const chunk of stream) {
        if (chunk.status === 'response') {
          result += chunk.message;
        }
      }

      expect(result).toBe('hello world!has_files');
    });

    it('should handle additional data in the payload', async () => {
      const payload: CreateMessagePayload = {
        chatbot_id: 'general-purpose',
        message: 'hello world',
        additional_data: {
          custom_field: 'value',
        },
      };

      const handler = new MessageAPI(client);
      const stream = await handler.create(payload);

      let result = '';
      for await (const chunk of stream) {
        if (chunk.status === 'response') {
          result += chunk.message;
        }
      }

      expect(result).toBe('hello world!has_additional_data');
    });
  });
});
