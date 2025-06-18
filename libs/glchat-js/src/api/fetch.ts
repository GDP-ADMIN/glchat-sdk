import type { GLChatConfiguration } from '../config';

function normalizeHeaders(headers?: Headers): Record<string, string> {
  if (!headers) {
    return {};
  }

  if (headers instanceof Headers) {
    const result: Record<string, string> = {};
    headers.forEach((value, key) => {
      result[key] = value;
    });

    return result;
  }

  if (Array.isArray(headers)) {
    return Object.fromEntries(headers);
  }

  return headers;
}

export async function glchatFetch(
  resource: string,
  config: GLChatConfiguration,
  options?: RequestInit,
) {
  try {
    const url = new URL(resource, config.baseUrl);

    const response = await fetch(url, {
      ...options,
      headers: {
        ...normalizeHeaders(options?.headers as Headers),
        'User-Agent': 'glchat-js-sdk@__packageVersion',
      },
    });

    return response;
  } catch {
    throw new Error('Failed to fetch');
  }
}
