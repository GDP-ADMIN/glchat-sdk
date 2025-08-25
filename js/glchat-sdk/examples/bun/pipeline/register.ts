import { GLChat } from '@/client';

const client = new GLChat();

void (async () => {
  const file = Bun.file('examples/fixtures/pipeline.zip');

  const result = await client.pipeline.register(file);
  console.log(JSON.stringify(result, null, 2));
})();
