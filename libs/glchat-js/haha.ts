import { GLChat } from './src';

const client = new GLChat();

void (async () => {
  const result = await client.message.create({
    chatbotId: 'general-purpose',
    message: 'hello!',
  });

  console.log(result);
})();
