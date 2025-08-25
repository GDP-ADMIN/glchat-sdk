<p align="center">
  <a href="https://docs.glair.ai" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://assets.analytics.glair.ai/generative/img/glchat-beta-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://assets.analytics.glair.ai/generative/img/glchat-beta-light.svg">
      <img alt="GLAIR" src="https://assets.analytics.glair.ai/generative/img/glchat-beta-light.svg" width="180" height="60" style="max-width: 100%;">
    </picture>
  </a>
</p>

<p align="center">
  GLChat JavaScript SDK
<p>

<p align="center">
    <a href="https://www.npmjs.com/package/glchat-sdk"><img src="https://img.shields.io/npm/v/glchat-sdk" alt="Latest Release"></a>
    <a href="https://github.com/GDP-ADMIN/glchat-sdk/blob/main/js/glchat-sdk/LICENSE"><img src="https://img.shields.io/npm/l/glchat-sdk" alt="License"></a>
</p>

## 📋 Overview

This SDK provides convenient access to the GLChat REST API for JavaScript or TypeScript.

This SDK is runtime-agnostic and can be used in [NodeJS](https://nodejs.org/en), [Deno](https://deno.com/), [Bun](https://bun.sh/), and [Cloudflare Workers](https://workers.cloudflare.com/) (untested).

## Requirements

Requirements may vary depending on the runtime. The following table denotes minimum version for various JavaScript runtimes:

| Runtime | Minimum Version |
| ------- | --------------- |
| NodeJS  | 18.x            |
| Bun     | 1.x             |

## 📦 Installation

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
import { GLChat } from "glchat-sdk";
```

## 🚀 Quick Start

The SDK can primarily be interacted through the main `GLChat` client:

```js
import { GLChat } from "glchat-sdk";

const client = new GLChat("<YOUR_API_KEY>");
```

After the client has been initialized, you can start interacting with GLChat API. The primary API to interact with GLChat API is the Message API. You can generate a response with the code below:

```js
import { GLChat } from "glchat-sdk";

const client = new GLChat("<YOUR_API_KEY>");

void (async () => {
  const result = await client.message.create({
    chatbot_id: "general-purpose",
    message: "hello!",
  });

  for await (const chunk of result) {
    console.log(chunk);
  }
})();
```

Sample codes in various JavaScript runtimes are available inside the [examples folder](./examples)

## 📚 API Reference

### GLChat

The main client class for interacting with the GLChat API.

#### Initialization

```ts
import { GLChat } from "glchat-sdk";

const client = new GLChat();
```

#### Constructor Parameters

| Name     | Type                           | Required? | Description                    |
| -------- | ------------------------------ | --------- | ------------------------------ |
| `config` | `Partial<GLChatConfiguration>` | No        | Optional client configuration. |

#### `config` Fields

| Name        | Type         | Required? | Description                                                                                                                                                                         |
| ----------- | ------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apiKey`    | `string`     | No        | GLChat API key for authentication. Reads from `process.env.GLCHAT_API_KEY` if not provided. The constructor will throw error if the API key is not available after resolution.      |
| `baseUrl`   | `string`     | No        | Custom base URL for the GLChat API. Reads from `process.env.GLCHAT_BASE_URL` if not provided. Defaults to `https://chat.gdplabs.id/api/proxy`                                       |
| `timeout`   | `number`     | No        | Global timeout when calling GLChat API in milliseconds. Must be a non-negative interger. Reads from `process.env.GLCHAT_TIMEOUT` if not provided. Defaults to `60_000` (60 seconds) |
| `__version` | `APIVersion` | No        | Optional API version to use. Reads from `process.env.GLCHAT_API_VERSION` if not provided. Currently unused.                                                                         |

> [!WARN]
> If your `baseUrl` contains a path, ensure that it ends with a trailing slash! Otherwise, the path will be dropped
> during request and may cause unexpected errors.

#### Methods

#### `.setBaseUrl(url: string): void`

Sets the base URL to be used for future API calls.

| Name | Type     | Required | Description          |
| ---- | -------- | -------- | -------------------- |
| url  | `string` | Yes      | A valid base API URL |

**Throws:** Error if the URL is invalid.

#### `.setAPIVersion(version: APIVersion): void`

Sets the API version to be used for future requests. Currently doesn't do anything.

| Name    | Type         | Required | Description                   |
| ------- | ------------ | -------- | ----------------------------- |
| version | `APIVersion` | Yes      | One of the supported versions |

#### `.setAPIVersion(version: APIVersion): void`

Sets the global API timeout to be used for future requests.

| Name    | Type     | Required | Description                                                                              |
| ------- | -------- | -------- | ---------------------------------------------------------------------------------------- |
| timeout | `number` | Yes      | Global timeout when calling GLChat API in milliseconds. Must be a non-negative interger. |

**Throws:** `ZodError` if the timeout is not an integer or negative.

### Message API

#### `message.create(payload: CreateMessagePayload)`

Creates a streaming response from the GLChat API for a chatbot message.

#### Payload Parameters

| Name                   | Type                                                  | Required | Description                                                   |
| ---------------------- | ----------------------------------------------------- | -------- | ------------------------------------------------------------- |
| `chatbot_id`           | `string`                                              | Yes      | The chatbot identifier where this message is created          |
| `message`              | `string`                                              | Yes      | The actual user message                                       |
| `parent_id`            | `string`                                              | No       | ID of the parent message or source message                    |
| `source`               | `string`                                              | No       | LLM name or agent ID                                          |
| `user_id`              | `string`                                              | No       | User identifier (optional in incognito)                       |
| `conversation_id`      | `string`                                              | No       | ID of the conversation (not available in incognito)           |
| `user_message_id`      | `string`                                              | No       | Custom ID for tracking the user message                       |
| `assistant_message_id` | `string`                                              | No       | Custom ID for tracking the assistant message                  |
| `chat_history`         | `[]`                                                  | No       | Placeholder for past message history (currently undocumented) |
| `files`                | `UploadedFile[]`                                      | No       | A list of files (Blob-compatible with optional `name` field)  |
| `stream_id`            | `string`                                              | No       | Custom stream ID for controlling the response stream          |
| `model_name`           | `${string}/${string}`                                 | No       | Model version override, e.g., `"openai/gpt-4"`                |
| `anonymize_em`         | `boolean`                                             | No       | Whether to anonymize before embedding                         |
| `anonymize_lm`         | `boolean`                                             | No       | Whether to anonymize before LLM processing                    |
| `use_cache`            | `boolean`                                             | No       | Use cached result if available                                |
| `search_type`          | `'normal' \| 'web'`                                   | No       | Selects whether to perform a web-enhanced query               |
| `metadata`             | `MessageMetadata`                                     | No       | Quoted phrase info and other niche metadata                   |
| `additional_data`      | `Record<string, string \| Blob \| null \| undefined>` | No       | Optional key-value pairs for advanced custom deployment use   |

#### `MessageMetadata` Fields

| Name  | Type     | Description                                          |
| ----- | -------- | ---------------------------------------------------- |
| `quote` | `string` | Quoted section of an assistant message (for context) |

#### `GLChatMessageChunk` Fields

| Name  | Type     | Description                                          |
| ----- | -------- | ---------------------------------------------------- |
| `quote` | `string` | Quoted section of an assistant message (for context) |

#### Returns

`Promise<AsyncIterable<GLChatMessageChunk>>`, an asynchronous iterable yielding [streamed message chunks](#message-chunks).

#### Example Usage

```ts
for await (const chunk of await client.message.create({
  chatbot_id: "bot-id",
  message: "Tell me a joke!",
})) {
  console.log(chunk);
}
```

### Pipeline API

#### `pipeline.register(pipeline: UploadedFile)`

Register a new pipeline to GLChat pipeline registry.

#### Payload Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `pipeline` | `UploadedFile` | Pipeline plugin file. Only accepts a `.zip` file. |

#### Returns

`Promise<PipelineRegistrationResponse>`, a Promise that resolves into `PipelineRegistrationResponse` with the following properties:

| Name | Type | Description |
| ---- | ---- | ----------- |
| `status` | `string` | Status of the response. The value for the property is always `success` |
| `registered_plugins` | `string[]` | List of plugin IDs that have been successfully registered. Will be used later for [unregistration API](#pipelineunregisterpluginids-string) |

#### Example Usage

```ts
const file = new File([<ZIP_FILE_CHUNK>], 'pipeline.zip', { type: 'application/zip' });

const result = await client.pipeline.register(file);
```

#### `pipeline.unregister(pluginIds: string[])`

Removes a pipeline plugin from GLChat pipeline registry.

#### Payload Parameters

| Name | Type | Description |
| ---- | ---- | ----------- |
| `pluginIds` | `string[]` | List of plugin IDs that should be removed from GLChat pipeline registry. The ID is returned from plugin registration. |

#### Returns

`Promise<PipelineUnregistrationResponse>`, a Promise that resolves into `PipelineUnregistrationResponse` with the following properties:

| Name | Type | Description |
| ---- | ---- | ----------- |
| `status` | `string` | Status of the response. The value for the property is always `success` |
| `unregistered_plugins` | `string[]` | List of plugin IDs that have been successfully unregistered. |

#### Example Usage

```ts
const result = await client.pipeline.unregister(['glchat-sample-pipeline']);
```

## Message Chunks

GLChat Message API streams the response in form of a structured chunk.

This type is a **discriminated union** and can be one of:

- `GLChatMessageResponseChunk`: The actual assistant or LLM response.
- `GLChatMessageDataChunk`: Intermediate information, references, metadata, etc.

### Shared Base Fields

All chunk types share these base fields from `GLChatMessageBaseChunk`:

| Field                | Type                                            | Description                                                                               |
| -------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| conversation_id      | `string \| null`                                | The conversation this chunk belongs to                                                    |
| user_message_id      | `string \| null`                                | The ID of the user message that triggered the chunk                                       |
| assistant_message_id | `string \| null`                                | The assistant message responding to the user message                                      |
| created_date         | `number`                                        | Unix timestamp when the chunk was created                                                 |
| status               | `"data" \| "response" \| "processing_document"` | Type of chunk content                                                                     |
| message              | `unknown`                                       | Actual chunk content. Chunk status must be asserted to have correct typing of this field. |

### `GLChatMessageResponseChunk`

Represents the actual streamed response text from the assistant or LLM.

| Field   | Type         | Description                               |
| ------- | ------------ | ----------------------------------------- |
| status  | `"response"` | Indicates this is a response chunk        |
| message | `string`     | A partial or full message response string |

### `GLChatMessageDataChunk`

Encapsulates non-textual information like references, attachments, media, etc.

| Field   | Type                                                                                                                                                                             | Description                                  |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| status  | `"data"`                                                                                                                                                                         | Indicates this is a metadata / info chunk    |
| message | One of:<br/>`GLChatReferenceChunk`<br/>`GLChatAttachmentChunk`<br/>`GLChatRelatedQuestionChunk`<br/>`GLChatDeanonymizationChunk`<br/>`GLChatMediaChunk`<br/>`GLChatProcessChunk` | Actual data content depending on `data_type` |

### `message.data_type` Variants in `GLChatMessageDataChunk`

#### `GLChatReferenceChunk`

| Field      | Type          | Description                                 |
| ---------- | ------------- | ------------------------------------------- |
| data_type  | `"reference"` | Type discriminator                          |
| data_value | `string[]`    | List of inline references from the response |

#### `GLChatAttachmentChunk`

| Field      | Type                 | Description                        |
| ---------- | -------------------- | ---------------------------------- |
| data_type  | `"attachments"`      | Type discriminator                 |
| data_value | `GLChatAttachment[]` | List of attachments in the message |

Each `GLChatAttachment` includes:

| Field | Type   | Description                   |
| ----- | ------ | ----------------------------- |
| id    | string | Unique identifier             |
| type  | string | MIME type of the file         |
| name  | string | File name                     |
| url   | string | Public URL to access the file |

#### `GLChatRelatedQuestionChunk`

| Field      | Type        | Description                         |
| ---------- | ----------- | ----------------------------------- |
| data_type  | `"related"` | Type discriminator                  |
| data_value | `string[]`  | Related questions to the user query |

#### `GLChatDeanonymizationChunk`

| Field      | Type                  | Description                                     |
| ---------- | --------------------- | ----------------------------------------------- |
| data_type  | `"deanonymized_data"` | Type discriminator                              |
| data_value | `DeanomymizedData`    | Contains mapping and raw user/assistant content |

**DeanomymizedData** includes:

| Field                | Type                     | Description                                |
| -------------------- | ------------------------ | ------------------------------------------ |
| user_message         | `DeanonymizedMessage`    | Original and deanonymized user input       |
| ai_message           | `DeanonymizedMessage`    | Original and deanonymized assistant output |
| deanonymized_mapping | `Record<string, string>` | Mapping of placeholders to originals       |

**DeanonymizedMessage** includes:

| Field                | Type                    | Description                   |
| -------------------- | ----------------------- | ----------------------------- |
| content              | `string`                | Anonymized version            |
| deanonymized_content | `string` \| `undefined` | Original version if available |

#### `GLChatMediaChunk`

| Field      | Type                     | Description                                  |
| ---------- | ------------------------ | -------------------------------------------- |
| data_type  | `"media_mapping"`        | Type discriminator                           |
| data_value | `Record<string, string>` | Mapping of media placeholders to public URLs |

#### `GLChatProcessChunk`

| Field      | Type            | Description                          |
| ---------- | --------------- | ------------------------------------ |
| data_type  | `"process"`     | Type discriminator                   |
| data_value | `GLChatProcess` | Status of backend message processing |

**GLChatProcess** includes:

| Field   | Type                                   | Description               |
| ------- | -------------------------------------- | ------------------------- |
| id      | `string`                               | Unique process ID         |
| message | `string` \| `undefined`                | Optional status message   |
| status  | `"running" \| "finished" \| "stopped"` | Progress state            |
| time    | `number` \| `undefined`                | Unix timestamp (optional) |

---

## 👮 Error Handling

GLChat JavaScript SDK provides several helpful errors in case when incorrect parameters are supplied, the API returned non-200 HTTP status code, or network failures. All errors are wrapped inside `GLChatError` class to distinguish them from other errors that don't came from GLChat JavaScript SDK.

```ts
import { GLChat, APIError } from 'glchat-sdk';

const client = new GLChat();

void (async () => {
  try {
    const result = await client.message.create({
      chatbot_id: 'general-purpose',
      message: 'hello!',
    });

    for await (const chunk of result) {
      // Process the chunk
    }
  } catch (err) {
    if (err instanceof APIError) {
      console.log(err.status);
      console.log(err.headers);
    }
  }
})();

```

Below are the list of possible error that can be thrown by the SDK

| Class | Cause |
| ----- | ----- |
| ValidationError | Thrown when incorrect parameters are supplied. This error has an extra field `issues` that stores detailed information which field(s) are invalid. This field is a [Standard Schema](https://github.com/standard-schema/standard-schema) issues field. |
| APIError | Thrown when API returned a non-OK HTTP response. Contains additional field `status` that stores the HTTP status and `headers` that stores the response headers. |
| TimeoutError | Thrown when request to API has timed out. Can only be thrown when `timeout` is supplied. |
| ChunkError | Thrown when API returned an invalid stream chunk format. Unlikely to be thrown. |
| NetworkError | Thrown when API request fails due to network error. This error has an extra field `originalError` that stores the original network error. |

## 👨‍💻 Contributing

Please refer to the [Contributor Guidelines](./CONTRIBUTING.md)

## 🔑 License

This project is licensed under the [MIT License](./LICENSE)
