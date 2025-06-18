import { describe, expect, it } from 'vitest';
import {
  DEFAULT_CONFIG,
  normalizeConfig,
  validateConfiguration,
  type GLChatConfiguration,
} from './config';

describe('normalizeConfig', () => {
  it('should return default config when empty object provided', () => {
    const result = normalizeConfig({});
    expect(result).toEqual(DEFAULT_CONFIG);
  });

  it('should merge provided config with defaults', () => {
    const customConfig: Partial<GLChatConfiguration> = {
      baseUrl: 'https://custom.example.com',
    };
    const result = normalizeConfig(customConfig);
    expect(result).toEqual({
      baseUrl: customConfig.baseUrl,
      __version: 'v1',
    });
  });

  it('should filter out null / undefined values', () => {
    const customConfig: Partial<GLChatConfiguration> = {
      baseUrl: undefined,
      __version: 'v1',
    };
    const result = normalizeConfig(customConfig);
    expect(result).toEqual({
      ...DEFAULT_CONFIG,
      __version: 'v1',
    });
  });
});

describe('validateConfiguration', () => {
  it('should not throw for valid configuration', () => {
    const validConfig: GLChatConfiguration = {
      baseUrl: 'https://valid.example.com',
      __version: 'v1',
    };
    expect(() => validateConfiguration(validConfig)).not.toThrow();
  });

  it('should throw for invalid URL', () => {
    const invalidConfig: GLChatConfiguration = {
      baseUrl: 'not-a-url',
      __version: 'v1',
    };

    expect(() => validateConfiguration(invalidConfig))
      .toThrowError('Invalid base URL. The base URL must be a valid URL');
  });

  it('should throw for invalid version', () => {
    const invalidConfig = {
      baseUrl: 'https://valid.example.com',
      __version: 'v2',
    };

    expect(() => validateConfiguration(invalidConfig as unknown as GLChatConfiguration))
      .toThrowError('Invalid API version. Available API versions are: v1');
  });
});
