import { GLChat } from './../../src/client';

const client = new GLChat('<YOUR_API_KEY>');

void (async () => {
  const result = await client.message.create({
    chatbot_id: 'general-purpose',
    message: 'hello!',
  });

  for await (const chunk of result) {
    console.log(chunk);
  }
})();
