import { describe, expect, it } from 'vitest';
import { ZodError } from 'zod/v4';
import { createGLChatFetchClient } from '../fetch';
import type { UploadedFile } from '../types';
import { PipelineAPI } from './handler';

describe('PipelineAPI', () => {
  const client = createGLChatFetchClient({
    apiKey: 'API-KEY',
    timeout: 0,
    baseUrl: 'https://test.glchat.id',
    __version: 'v1',
  });

  describe('register', () => {
    it('should throw a ZodError if the payload is not a file', async () => {
      const handler = new PipelineAPI(client);

      await expect(() => handler.register(1 as unknown as UploadedFile)).rejects.toThrow(ZodError);
    });

    it('should throw a ZodError if the payload is not a zip file', async () => {
      // I don't even know who Rocky Balboa is.
      const payload = new Blob(['Rocky Balboa'], { type: 'text/plain' });
      const handler = new PipelineAPI(client);

      await expect(() => handler.register(payload)).rejects.toThrow(ZodError);
    });

    it('should return a success response when request is successful', async () => {
      const payload = new Blob(['Rocky Balboa'], { type: 'application/zip' });
      const handler = new PipelineAPI(client);

      const result = await handler.register(payload);

      expect(result.status).toBe('success');
      expect(Array.isArray(result.registered_pipelines)).toBe(true);
    });
  });
});
