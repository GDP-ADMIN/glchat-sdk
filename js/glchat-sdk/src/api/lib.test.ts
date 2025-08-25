import { ChunkError, ValidationError } from '@/error';
import { beforeEach, describe, expect, it } from 'vitest';
import { z } from 'zod/v4';
import { processGLChatChunk, withValidation } from './lib';

describe('processGLChatChunk', () => {
  it('should throw error when the chunk has incorrect type', () => {
    const chunk = 1234123412334;

    expect(() => processGLChatChunk(chunk)).toThrow(ChunkError);
  });

  it('should throw error when the chunk is an incorrect JSON', () => {
    const chunk = '{234j123oi52';

    expect(() => processGLChatChunk(chunk)).toThrow(ChunkError);
  });

  it('should process response chunk', () => {
    const expected = {
      conversation_id: null,
      user_message_id: null,
      assistant_message_id: null,
      created_date: 1234,
      status: 'response',
      message: 'foo',
    };

    const chunk = JSON.stringify(expected);

    const parsedChunk = processGLChatChunk(chunk);

    expect(parsedChunk).toEqual(expected);
  });

  it('should perform deep JSON.parse to data chunks', () => {
    const expected = {
      conversation_id: null,
      user_message_id: null,
      assistant_message_id: null,
      created_date: 1234,
      status: 'data',
      message: {
        data_type: 'reference',
        data_value: ['foo'],
      },
    };

    // perform copy
    const objectChunk = JSON.parse(JSON.stringify(expected));
    objectChunk.message = JSON.stringify(objectChunk.message);

    const chunk = JSON.stringify(objectChunk);

    const parsedChunk = processGLChatChunk(chunk);

    expect(parsedChunk).toEqual(expected);
  });
});

class TestService {
  @withValidation(z.string())
  async echo(input: string): Promise<string> {
    return `echo: ${input}`;
  }

  @withValidation(z.string())
  async throws(_input: string): Promise<string> {
    throw new Error('Something else failed');
  }
}

describe('withValidation decorator', () => {
  let service: TestService;

  beforeEach(() => {
    service = new TestService();
  });

  it('should run the method when input is valid', async () => {
    await expect(service.echo('hello')).resolves.toBe('echo: hello');
  });

  it('should throw ValidationError when input is invalid', async () => {
    await expect(service.echo(123 as unknown as string)).rejects.toBeInstanceOf(ValidationError);
  });

  it('should propagate non-validation errors', async () => {
    await expect(service.throws('hello')).rejects.toThrow('Something else failed');
  });
});
