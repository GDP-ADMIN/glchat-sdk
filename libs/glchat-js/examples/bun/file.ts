import { GLChat } from './../../src/client';

const client = new GLChat('<YOUR_API_KEY>');

void (async () => {
  // Bun supports faster filesystem using the Bun namespace
  const sampleText = Bun.file('examples/bun/sample.txt');

  const result = await client.message.create({
    chatbot_id: 'general-purpose',
    message: 'Tell me the filename from the .txt file that I have attached and its contents!',
    files: [sampleText],
    search_type: 'normal',
    anonymize_lm: false,
  });

  for await (const chunk of result) {
    console.log(chunk);
  }
})();
