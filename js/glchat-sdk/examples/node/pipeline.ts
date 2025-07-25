import { readFileSync } from 'node:fs';

import { GLChat } from './../../src/client';

const client = new GLChat();

void (async () => {
  const buffer = readFileSync('examples/fixtures/pipeline.zip');
  const file = new File([buffer], 'pipeline.zip', { type: 'application/zip' });

  /**
   * If you are using a Node version that doesn't support File API yet, you can try:
   *
   * const uploadedFile: UploadedFile = Object.assign(
   *   new Blob([buffer], { type: 'text/plain' }),
   *   { name: 'file.txt' },
   * );
   */

  const result = await client.pipeline.register(file);
  console.log(result);
})();
