import { GLChat } from '@/client';
import { readFileSync } from 'node:fs';

const client = new GLChat();

void (async () => {
  const buffer = readFileSync('examples/fixtures/pipeline.zip');
  const file = new File([buffer], 'pipeline.zip', { type: 'application/zip' });

  const result = await client.pipeline.register(file);
  console.log(JSON.stringify(result, null, 2));
})();
