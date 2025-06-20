<p align="center">
  <a href="https://docs.glair.ai" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://glair-chart.s3.ap-southeast-1.amazonaws.com/images/glair-horizontal-logo-blue.png">
      <source media="(prefers-color-scheme: light)" srcset="https://glair-chart.s3.ap-southeast-1.amazonaws.com/images/glair-horizontal-logo-color.png">
      <img alt="GLAIR" src="https://glair-chart.s3.ap-southeast-1.amazonaws.com/images/glair-horizontal-logo-color.png" width="180" height="60" style="max-width: 100%;">
    </picture>
  </a>
</p>

<p align="center">
  GLChat JavaScript SDK
<p>

<p align="center">
    <a href="https://github.com/glair-ai/glchat-sdk/releases"><img src="https://img.shields.io/npm/v/glchat-sdk" alt="Latest Release"></a>
    <a href="https://github.com/glair-ai/glchat-sdk/blob/main/LICENSE"><img src="https://img.shields.io/npm/l/glchat-sdk" alt="License"></a>
</p>

This SDK provides convenient access to the GLChat REST API for JavaScript or TypeScript.

This SDK is runtime-agnostic and can be used in NodeJS, Deno, Bun, and Cloudflare Workers (untested).

## Installation

You can install this SDK with your package manager from npm registry

```bash
# Using npm
npm install glchat-sdk

# Using yarn
yarn add glchat-sdk

# Using pnpm
pnpm add glchat-sdk

# Using bun
bun add glchat-sdk
```

This SDK is also available in JSR

```bash
npx jsr add glchat-sdk
```

After installation, you can verify your installation by trying to import the package from your workspace directory:

```js
import { GLChat } from 'glchat-sdk';
```

## Quick Start

The SDK can primarily be interacted through the main `GLChat` client:

```js
import { GLChat } from 'glchat-sdk';

const client = new GLChat('<YOUR_API_KEY>');
```

After the client has been initialized, you can start interacting with GLChat API. The primary API to interact with GLChat API is the Message API. You can generate a response with the code below:

```js
import { GLChat } from 'glchat-sdk';

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
```

Sample codes in various JavaScript runtimes are available inside the [examples folder](./examples)

## API Reference

### GLChat

The main client class for interacting with the GLChat API.

#### Initialization

```ts
import { GLChat } from 'glchat-sdk';

const client = new GLChat('<YOUR_API_KEY>');
```

#### Constructor Parameters

| Name       | Type                        | Required? | Description                                 |
|------------|-----------------------------|----------|---------------------------------------------|
| `apiKey`     | `string`                    | Yes      | GLChat API key for authentication      |
| `config`     | `Partial<GLChatConfiguration>` | No       | Optional client configuration.               |

#### `config` Fields

| Name        | Type          | Required? | Description                              |
|-------------|---------------|----------|------------------------------------------|
| `baseUrl`     | `string`      | No       | Custom base URL for the GLChat API. Defaults to `https://chat.gdplabs.id/api/proxy`       |
| `__version`   | `APIVersion`  | No       | Optional API version to use. Currently unused.              |

> [!WARN]
> If your `baseUrl` contains a path, ensure that it ends with a trailing slash! Otherwise, the path will be dropped
> during request and may cause unexpected errors.

### Methods

#### `.setBaseUrl(url: string): void`

Sets the base URL to be used for future API calls.

| Name | Type     | Required | Description         |
|------|----------|----------|---------------------|
| url  | `string` | Yes      | A valid base API URL |

**Throws:** Error if the URL is invalid.

#### `.setAPIVersion(version: APIVersion): void`

Sets the API version to be used for future requests.

| Name    | Type         | Required | Description                 |
|---------|--------------|----------|-----------------------------|
| version | `APIVersion` | Yes      | One of the supported versions |

**Throws:** Error if the version is invalid or unsupported.

### Message API

#### `message.create(payload: CreateMessagePayload): Promise<AsyncIterable<GLChatMessageChunk>>`

Creates a streaming response from the GLChat API for a chatbot message.

```ts
const stream = await client.message.create({
  chatbot_id: 'bot-123',
  message: 'Hello!',
  conversation_id: 'conv-456',
  files: [new File(['hello'], 'greeting.txt')],
});
```

#### Payload Parameters

| Name                  | Type                         | Required | Description                                                                 |
|-----------------------|------------------------------|----------|-----------------------------------------------------------------------------|
| `chatbot_id`            | `string`                     | Yes      | The chatbot identifier where this message is created                        |
| `message`               | `string`                     | Yes      | The actual user message                                                     |
| `parent_id`             | `string`                     | No       | ID of the parent message or source message                                  |
| `source`                | `string`                     | No       | LLM name or agent ID                                                        |
| `user_id`               | `string`                     | No       | User identifier (optional in incognito)                                     |
| `conversation_id`       | `string`                     | No       | ID of the conversation (not available in incognito)                         |
| `user_message_id`       | `string`                     | No       | Custom ID for tracking the user message                                     |
| `assistant_message_id`  | `string`                     | No       | Custom ID for tracking the assistant message                                |
| `chat_history`          | `[]`                         | No       | Placeholder for past message history (currently undocumented)               |
| `files`                 | `UploadedFile[]`             | No       | A list of files (Blob-compatible with optional `name` field)                |
| `stream_id`             | `string`                     | No       | Custom stream ID for controlling the response stream                        |
| `model_name`            | ``${string}/${string}``      | No       | Model version override, e.g., `"openai/gpt-4"`                              |
| `anonymize_em`          | `boolean`                    | No       | Whether to anonymize before embedding                                       |
| `anonymize_lm`          | `boolean`                    | No       | Whether to anonymize before LLM processing                                  |
| `use_cache`             | `boolean`                    | No       | Use cached result if available                                              |
| `search_type`           | `'normal' \| 'web'`          | No       | Selects whether to perform a web-enhanced query                             |
| `metadata`              | `MessageMetadata`            | No       | Quoted phrase info and other niche metadata                                 |
| `additional_data`       | `Record<string, string \| Blob \| null \| undefined>` | No | Optional key-value pairs for advanced custom deployment use                 |

#### `MessageMetadata` Fields

| Name   | Type     | Description                                           |
|--------|----------|-------------------------------------------------------|
| quote  | `string` | Quoted section of an assistant message (for context)  |

#### `GLChatMessageChunk` Fields

| Name   | Type     | Description                                           |
|--------|----------|-------------------------------------------------------|
| quote  | `string` | Quoted section of an assistant message (for context)  |

#### Returns

- `Promise<AsyncIterable<GLChatMessageChunk>>`: An asynchronous iterable yielding streamed message chunks.

### Example Usage

```ts
for await (const chunk of await client.message.create({
  chatbot_id: 'bot-id',
  message: 'Tell me a joke!',
})) {
  console.log(chunk);
}
```

## Message Chunks

GLChat Message API streams the response in form of a structured chunk.

This type is a **discriminated union** and can be one of:

- `GLChatMessageResponseChunk`: The actual assistant or LLM response.
- `GLChatMessageDataChunk`: Intermediate information, references, metadata, etc.

### Shared Base Fields

All chunk types share these base fields from `GLChatMessageBaseChunk`:

| Field               | Type               | Description                                                                 |
|--------------------|--------------------|-----------------------------------------------------------------------------|
| conversation_id     | `string \| null`   | The conversation this chunk belongs to                                      |
| user_message_id     | `string \| null`   | The ID of the user message that triggered the chunk                         |
| assistant_message_id| `string \| null`   | The assistant message responding to the user message                        |
| created_date        | `number`           | Unix timestamp when the chunk was created                                   |
| status              | `"data" \| "response" \| "processing_document"` | Type of chunk content |

### `GLChatMessageResponseChunk`

Represents the actual streamed response text from the assistant or LLM.

| Field   | Type     | Description                              |
|---------|----------|------------------------------------------|
| status  | `"response"` | Indicates this is a response chunk     |
| message | `string` | A partial or full message response string |

### `GLChatMessageDataChunk`

Encapsulates non-textual information like references, attachments, media, etc.

| Field   | Type                                                                 | Description                                   |
|---------|----------------------------------------------------------------------|-----------------------------------------------|
| status  | `"data"`                                                             | Indicates this is a metadata / info chunk       |
| message | One of:<br/>`GLChatReferenceChunk`<br/>`GLChatAttachmentChunk`<br/>`GLChatRelatedQuestionChunk`<br/>`GLChatDeanonymizationChunk`<br/>`GLChatMediaChunk`<br/>`GLChatProcessChunk` | Actual data content depending on `data_type`  |

### `message.data_type` Variants in `GLChatMessageDataChunk`

#### `GLChatReferenceChunk`

| Field      | Type       | Description                                 |
|------------|------------|---------------------------------------------|
| data_type  | `"reference"` | Type discriminator                         |
| data_value | `string[]` | List of inline references from the response |

#### `GLChatAttachmentChunk`

| Field      | Type               | Description                            |
|------------|--------------------|----------------------------------------|
| data_type  | `"attachments"`    | Type discriminator                     |
| data_value | `GLChatAttachment[]` | List of attachments in the message     |

Each `GLChatAttachment` includes:

| Field | Type   | Description                     |
|-------|--------|---------------------------------|
| id    | string | Unique identifier               |
| type  | string | MIME type of the file           |
| name  | string | File name                       |
| url   | string | Public URL to access the file   |

#### `GLChatRelatedQuestionChunk`

| Field      | Type       | Description                          |
|------------|------------|--------------------------------------|
| data_type  | `"related"`| Type discriminator                   |
| data_value | `string[]` | Related questions to the user query  |

#### `GLChatDeanonymizationChunk`

| Field      | Type               | Description                                 |
|------------|--------------------|---------------------------------------------|
| data_type  | `"deanonymized_data"` | Type discriminator                         |
| data_value | `DeanomymizedData` | Contains mapping and raw user/assistant content |

**DeanomymizedData** includes:

| Field               | Type                             | Description                          |
|--------------------|----------------------------------|--------------------------------------|
| user_message        | `DeanonymizedMessage`            | Original and deanonymized user input |
| ai_message          | `DeanonymizedMessage`            | Original and deanonymized assistant output |
| deanonymized_mapping| `Record<string, string>`         | Mapping of placeholders to originals |

**DeanonymizedMessage** includes:

| Field               | Type      | Description                                |
|--------------------|-----------|--------------------------------------------|
| content             | `string` | Anonymized version                         |
| deanonymized_content| `string` \| `undefined` | Original version if available     |

#### `GLChatMediaChunk`

| Field      | Type                    | Description                                     |
|------------|-------------------------|-------------------------------------------------|
| data_type  | `"media_mapping"`       | Type discriminator                              |
| data_value | `Record<string, string>`| Mapping of media placeholders to public URLs    |

#### `GLChatProcessChunk`

| Field      | Type             | Description                                |
|------------|------------------|--------------------------------------------|
| data_type  | `"process"`      | Type discriminator                         |
| data_value | `GLChatProcess`  | Status of backend message processing       |

**GLChatProcess** includes:

| Field   | Type     | Description                               |
|---------|----------|-------------------------------------------|
| id      | `string` | Unique process ID                         |
| message | `string` \| `undefined` | Optional status message         |
| status  | `"running" \| "finished" \| "stopped"` | Progress state |
| time    | `number` \| `undefined` | Unix timestamp (optional)       |

---

## Contributing

Please refer to the [Contributor Guidelines](./CONTRIBUTING.md)

## License

This project is licensed under the [MIT License](./LICENSE)
