import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { GLChatConfiguration } from '../config';
import { createGLChatFetchClient } from './fetch';

const mockApiKey = 'test-api-key';
const mockConfig: GLChatConfiguration = {
  baseUrl: 'https://test.glchat.id/',
  __version: 'v1',
};

describe('createGLChatFetchClient with MSW', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should make successful request with correct headers', async () => {
    const client = createGLChatFetchClient(mockApiKey, mockConfig);
    const response = await client('/fetch/success', {
      headers: {
        Accept: 'text/html',
      },
    });

    expect(response.status).toBe(200);
    const body = await response.json();

    expect(body).toEqual({
      data: {
        headers: {
          'Accept': 'text/html',
          'Authorization': `Bearer ${mockApiKey}`,
          'User-Agent': 'glchat-js-sdk@dev',
        },
      },
    });
  });

  it('should make successful request with array headers', async () => {
    const client = createGLChatFetchClient(mockApiKey, mockConfig);
    const response = await client('/fetch/success', {
      headers: new Headers([['Accept', 'text/html']]),
    });

    expect(response.status).toBe(200);
    const body = await response.json();

    expect(body).toEqual({
      data: {
        headers: {
          'Accept': 'text/html',
          'Authorization': `Bearer ${mockApiKey}`,
          'User-Agent': 'glchat-js-sdk@dev',
        },
      },
    });
  });

  it('should throw error when the request fails', async () => {
    const client = createGLChatFetchClient(mockApiKey, mockConfig);

    await expect(client('/fetch/fail')).rejects.toThrowError('Failed to fetch');
  });
});
