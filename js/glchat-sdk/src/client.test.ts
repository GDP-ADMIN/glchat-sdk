import { afterEach, describe, expect, it, vi } from 'vitest';
import { GLChat } from './client';

import type { APIVersion } from './config';
import { ValidationError } from './error';

describe('GLChat', () => {
  afterEach(() => vi.clearAllMocks());

  describe('constructor', () => {
    it('should initialize with default configuration when no config provided', () => {
      expect(() => new GLChat()).not.toThrowError();
    });

    it('should initialize with custom configuration', () => {
      expect(() => new GLChat({
        baseUrl: 'https://www.google.com',
        timeout: 234589432,
        __version: 'v1',
      })).not.toThrowError();
    });

    it('should throw if configuration validation fails', () => {
      expect(() => new GLChat({
        baseUrl: 'haha',
      })).toThrow(ValidationError);
    });
  });

  describe('setBaseUrl', () => {
    it('should update the base URL when valid', () => {
      const client = new GLChat();
      const newUrl = 'https://new.example.com';

      expect(() => client.setBaseUrl(newUrl)).not.toThrow();
    });

    it('should throw error when the URL is invalid', () => {
      const client = new GLChat();
      const newUrl = 'AKU CINTA GLCHAT ♡';

      expect(() => client.setBaseUrl(newUrl)).toThrow(ValidationError);
    });
  });

  describe('setAPIVersion', () => {
    it('should update the API version when valid', () => {
      const client = new GLChat();
      const newVersion = 'v1';

      expect(() => client.setAPIVersion(newVersion)).not.toThrow();
    });

    it('should throw error the API version is invalid', () => {
      const client = new GLChat();
      const newVersion = 'versi-3';

      expect(() => client.setAPIVersion(newVersion as unknown as APIVersion)).toThrow(ValidationError);
    });
  });

  describe('setTimeout', () => {
    it('should update the timeout when valid', () => {
      const client = new GLChat();
      const newTimeout = 123124;

      expect(() => client.setTimeout(newTimeout)).not.toThrow();
    });

    it('should throw error the timeout is invalid', () => {
      const client = new GLChat();
      const newTimeout = -123;

      expect(() => client.setTimeout(newTimeout)).toThrow(ValidationError);
    });
  });
});
