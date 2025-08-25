import { GLChat } from '@/client';

const client = new GLChat();

void (async () => {
  const result = await client.pipeline.unregister(['claudia-gpt']);
  console.log(JSON.stringify(result, null, 2));
})();
