import { GLChat } from './../../src/client';

const client = new GLChat();

void (async () => {
  // Deno uses custom filesystem API inside the Deno namespace
  const rawFile = await Deno.readFile('examples/fixtures/sample.txt');
  const file = new Blob([rawFile], { type: 'text/plain' });

  const result = await client.message.create({
    chatbot_id: 'general-purpose',
    message: 'Tell me the filename from the .txt file that I have attached and its contents!',
    files: [file],
    search_type: 'normal',
    anonymize_lm: false,
  });

  for await (const chunk of result) {
    console.log(chunk);
  }
})();
