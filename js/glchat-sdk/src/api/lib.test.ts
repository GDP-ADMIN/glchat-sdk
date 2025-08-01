import { describe, expect, it } from 'vitest';
import { processGLChatChunk } from './lib';

describe('processGLChatChunk', () => {
  it('should throw error when the chunk is incorrect', () => {
    const chunk = 1234123412334;

    expect(() => processGLChatChunk(chunk)).toThrow('Chunk is corrupted!');
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
