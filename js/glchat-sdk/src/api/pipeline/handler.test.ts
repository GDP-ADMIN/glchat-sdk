import { createGLChatFetchClient } from '@/api/fetch';
import type { UploadedFile } from '@/api/types';
import { ValidationError } from '@/error';
import { describe, expect, it } from 'vitest';
import { PipelineAPI } from './handler';

describe('PipelineAPI', () => {
  const client = createGLChatFetchClient({
    apiKey: 'API-KEY',
    timeout: 0,
    baseUrl: 'https://test.glchat.id',
    __version: 'v1',
  });

  describe('register', () => {
    it('should throw ValidationError if the payload is not a file', async () => {
      const handler = new PipelineAPI(client);

      await expect(() => handler.register(1 as unknown as UploadedFile)).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError if the payload is not a zip file', async () => {
      // I don't even know who Rocky Balboa is.
      const payload = new Blob(['Rocky Balboa'], { type: 'text/plain' });
      const handler = new PipelineAPI(client);

      await expect(() => handler.register(payload)).rejects.toThrow(ValidationError);
    });

    it('should return a success response when request is successful', async () => {
      const payload = new Blob(['Rocky Balboa'], { type: 'application/zip' });
      const handler = new PipelineAPI(client);

      const result = await handler.register(payload);

      expect(result.status).toBe('success');
      expect(Array.isArray(result.registered_pipelines)).toBe(true);
    });
  });

  describe('unregister', () => {
    it('should throw ValidationError if the payload is not an array of string', async () => {
      const handler = new PipelineAPI(client);

      await expect(() => handler.unregister([1] as unknown as string[])).rejects.toThrow(ValidationError);
    });

    it('should throw ValidationError if the payload is an empty array', async () => {
      const handler = new PipelineAPI(client);

      await expect(() => handler.unregister([])).rejects.toThrow(ValidationError);
    });

    it('should return a success response when the request is successful', async () => {
      const handler = new PipelineAPI(client);

      const result = await handler.unregister(['Rocky Balboa']);

      expect(result.status).toBe('success');
      expect(Array.isArray(result.unregistered_pipelines)).toBe(true);
    });
  });
});
