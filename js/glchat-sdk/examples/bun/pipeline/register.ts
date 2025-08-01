import { GLChat } from '@/client';

const client = new GLChat();

void (async () => {
  const file = Bun.file('examples/fixtures/pipeline.zip');

  /**
   * If you are using a Node version that doesn't support File API yet, you can try:
   *
   * const uploadedFile: UploadedFile = Object.assign(
   *   new Blob([buffer], { type: 'text/plain' }),
   *   { name: 'file.txt' },
   * );
   */

  const result = await client.pipeline.register(file);
  console.log(JSON.stringify(result, null, 2));
})();
