import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const handlers = [
  http.get('https://test.glchat.id/fetch/success', (ctx) => {
    return HttpResponse.json({
      data: {
        headers: {
          'Accept': ctx.request.headers.get('Accept'),
          'Authorization': ctx.request.headers.get('Authorization'),
          'User-Agent': ctx.request.headers.get('User-Agent'),
        },
      },
    });
  }),

  http.get('https://test.glchat.id/fetch/fail/network', () => {
    return HttpResponse.error();
  }),

  http.get('https://test.glchat.id/fetch/fail/not-ok', () => {
    return HttpResponse.json({}, { status: 401 });
  }),

  http.post('https://test.glchat.id/message', async ({ request }) => {
    const formData = await request.formData();
    const hasFiles = formData.getAll('files').length > 0;
    const hasAdditionalData = Array.from(formData.entries())
      .some(([key]) => key !== 'files' && key !== 'chatbot_id' && key !== 'message');

    const stream = new ReadableStream({
      start(controller) {
        // First chunk with metadata about the request
        controller.enqueue(new TextEncoder().encode(
          JSON.stringify({
            conversation_id: null,
            user_message_id: null,
            assistant_message_id: null,
            created_date: 1234,
            status: 'metadata',
            has_files: hasFiles,
            has_additional_data: hasAdditionalData,
          }),
        ));

        // Second chunk with the actual response
        controller.enqueue(new TextEncoder().encode(
          JSON.stringify({
            conversation_id: null,
            user_message_id: null,
            assistant_message_id: null,
            created_date: 1234,
            status: 'response',
            message: 'hello',
          }),
        ));

        controller.enqueue(new TextEncoder().encode(
          JSON.stringify({
            conversation_id: null,
            user_message_id: null,
            assistant_message_id: null,
            created_date: 1234,
            status: 'response',
            message: ' world!',
          }),
        ));

        if (hasFiles) {
          controller.enqueue(new TextEncoder().encode(
            JSON.stringify({
              conversation_id: null,
              user_message_id: null,
              assistant_message_id: null,
              created_date: 1234,
              status: 'response',
              message: 'has_files',
            }),
          ));
        }

        if (hasAdditionalData) {
          controller.enqueue(new TextEncoder().encode(
            JSON.stringify({
              conversation_id: null,
              user_message_id: null,
              assistant_message_id: null,
              created_date: 1234,
              status: 'response',
              message: 'has_additional_data',
            }),
          ));
        }

        controller.close();
      },
    });

    return new HttpResponse(stream, {
      headers: {
        'content-type': 'text/event-stream',
      },
    });
  }),

  http.post('https://test.glchat.id/register-pipeline-plugin', async () => {
    return HttpResponse.json({
      status: 'success',
      registered_pipelines: ['Rocky Balboa'],
    });
  }),
];

export const server = setupServer(...handlers);
