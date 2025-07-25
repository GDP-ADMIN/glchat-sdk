import { GLChat } from '@/client';

const client = new GLChat();

void (async () => {
  const result = await client.message.create({
    chatbot_id: 'general-purpose',
    message: 'hello!',
  });

  for await (const chunk of result) {
    if (chunk.status === 'response') {
      console.log(chunk.message);
    } else if (chunk.status === 'data') {
      console.log(`Got data chunk of ${chunk.message.data_type}`);
    }
  }
})();
