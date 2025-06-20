import { readFileSync } from 'node:fs';

import { GLChat } from './../../src/client';

const client = new GLChat('<YOUR_API_KEY>');

void (async () => {
  const buffer = readFileSync('examples/fixtures/sample.txt');
  const file = new File([buffer], 'file.txt', { type: 'text/plain' });

  /**
   * If you are using a Node version that doesn't support File API yet, you can try:
   *
   * const uploadedFile: UploadedFile = Object.assign(
   *   new Blob([buffer], { type: 'text/plain' }),
   *   { name: 'file.txt' },
   * );
   */

  const result = await client.message.create({
    chatbot_id: 'general-purpose',
    message: 'Tell me the filename from the .txt file that I have attached and its contents!',
    files: [file],
  });

  for await (const chunk of result) {
    console.log(chunk);
  }
})();
