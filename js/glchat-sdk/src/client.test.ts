import { beforeEach, describe, expect, it, vi } from 'vitest';
import { GLChat } from './client';
import type { GLChatConfiguration } from './config';

import * as config from './config';

describe('GLChat', () => {
  const mockConfig: GLChatConfiguration = {
    baseUrl: 'https://api.example.com',
    __version: 'v1',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    vi.spyOn(config, 'normalizeConfig').mockImplementation(partialConfig => ({
      ...mockConfig,
      ...partialConfig,
    }));

    vi.spyOn(config, 'validateConfiguration').mockImplementation(() => {
      // ...do nothing
    });
  });

  describe('constructor', () => {
    it('should initialize with default configuration when no config provided', () => {
      new GLChat('');
      expect(config.normalizeConfig).toHaveBeenCalledWith({});
      expect(config.validateConfiguration).toHaveBeenCalled();
    });

    it('should initialize with provided configuration', () => {
      const customConfig = { baseUrl: 'https://custom.example.com' };
      new GLChat('', customConfig);
      expect(config.normalizeConfig).toHaveBeenCalledWith(customConfig);
    });

    it('should throw if configuration validation fails', () => {
      vi.spyOn(config, 'validateConfiguration').mockImplementation(() => {
        throw new Error('Invalid config');
      });

      expect(() => new GLChat('', {})).toThrow('Invalid config');
    });
  });

  describe('setBaseUrl', () => {
    it('should update the base URL when valid', () => {
      const client = new GLChat('', mockConfig);
      const newUrl = 'https://new.example.com';

      client.setBaseUrl(newUrl);

      expect(config.validateConfiguration).toHaveBeenCalledWith({
        ...mockConfig,
        baseUrl: newUrl,
      });
    });
  });

  describe('setAPIVersion', () => {
    it('should update the API version when valid', () => {
      const client = new GLChat('', mockConfig);
      const newVersion = 'v1';

      client.setAPIVersion(newVersion);

      expect(config.validateConfiguration).toHaveBeenCalledWith({
        ...mockConfig,
        __version: newVersion,
      });
    });
  });
});
