/*
 * types.ts
 *
 * Collection of types related with message API (payload).
 *
 * Authors:
 *   Cristopher (cristopher@gdplabs.id)
 * Created at: June 18th 2025
 *
 * ---
 * Copyright (c) GDP LABS. All rights reserved.
 */

import { z } from 'zod/v4';

/**
 * Custom file type of files for message-related functionality.
 *
 * Mainly made to maintain runtime-compatibility with Bun, since Bun
 * doesn't support `File` natively.
 */
export interface UploadedFile extends Blob {
  readonly name?: string | undefined;
}

/**
 * Common chat mode of a message, where the data
 * is passed directly to LLM with as minimal processing
 * as possible.
 */
type ChatbotMode = 'normal';
/**
 * Chat mode of a message where it performs a web
 * search using search engine to gather additional
 * contexts before passing through to LLM.
 */
type WebSearchMode = 'web';
/**
 * Available chat mode for a message.
 */
type SearchType = ChatbotMode | WebSearchMode;

/**
 * Step is currently in progress.
 */
type Running = 'running';
/**
 * Step has been completed successfully.
 */
type Finished = 'finished';
/**
 * Step was stopped either prematurely or by user demand.
 */
type Stopped = 'stopped';
/**
 * Available statuses for a step indicator. Each status corresponds
 * to a specific visual state in the UI.
 * */
export type StepIndicatorStatus = Running | Finished | Stopped;

/**
 * A chunk where the value contains actual data stored
 * inside `data_value`.
 */
type Data = 'data';
/**
 * A chunk where the value contains response from LLM
 * stored as a string inside `data_value`.
 */
type Response = 'response';
/**
 * A dummy chunk that indicates the DPO is still processing
 * user documents.
 */
type ProcessingDocument = 'processing_document';
/**
 * Available variants for chunks from API. Each type should
 * be handled separately.
 */
export type GLChatMessageStatus = Data | Response | ProcessingDocument;

/**
 * Payload for creating a new message in GLChat
 */
export interface CreateMessagePayload {
  /**
   * The chatbot identifier where this message is created.
   */
  chatbot_id: string;
  /**
   * Actual message contents
   */
  message: string;

  /**
   * The parent identifier of the newly created message.
   *
   * Normally, this should be the ID of the previous message
   * except for the following cases:
   *  1. If this is the first message of a conversation,
   *     this value should be the conversation ID
   *  2. If this message is a new message based on regenerate or edit,
   *     this value should be the source message ID.
   */
  parent_id?: string;
  /**
   * The intended source of the resulting assistant message.
   *
   * Should be filled with the currently used LLM or in agent flow,
   * the agent identifier.
   */
  source?: string;
  /**
   * User identifier.
   *
   * Should be `undefined` in incognito mode
   */
  user_id?: string;
  /**
   * The conversation identifier where this message is created.
   *
   * Should be `undefined` in incognito mode as incognito
   * doesn't have the capability to initiate a new conversation.
   */
  conversation_id?: string;
  /**
   * TODO: write documentation for this
   */
  user_message_id?: string;
  /**
   * TODO: write documentation for this
   */
  assistant_message_id?: string;
  /**
   * TODO: write documentation for this
   */
  chat_history?: [];
  /**
   * List of uploaded files that should be included in message.
   *
   * This field uses a custom type `UploadedFile` to
   * maintain runtime-compability.
   *
   * It extends the base `Blob` class with additional field `name`,
   * which should be fulfilled by `File` and `BunFile` objects respectively.
   */
  files?: UploadedFile[];
  /**
   * Stream identifier
   *
   * Useful for stop generation. If not provided, this value will be
   * automatically generated and returned later.
   */
  stream_id?: string;
  /**
   * Model name that will be used to respond to this messsage.
   */
  model_name?: `${string}/${string}`;
  /**
   * Determines whether the message should be anonymized before
   * the message is forwarded to the embedding model.
   */
  anonymize_em?: boolean;
  /**
   * Determines whether the message should be anonymized before
   * the message is forwarded to the language model.
   */
  anonymize_lm?: boolean;
  /**
   * Determines whether this message should use cache.
   *
   * Using cache might speed up the response time of
   * this message if similar query
   * has been asked before.
   */
  use_cache?: boolean;
  /**
   * Search mode of this message that determines the base source
   * of the reasoning.
   */
  search_type?: SearchType;
  /**
   * A collection of miscellaneous data that doesn't fit
   * with existing keys but don't warrant for additional keys
   * due to how niche they are.
   */
  metadata?: MessageMetadata;
  /**
   * Additional form data key-value pairs that can be included in the request.
   *
   * This field is used for custom deployments only.
   *
   * The key should not conflict with other preserved keys.
   */
  additional_data?: Record<string, string | Blob | null | undefined>;
};

/**
 * A collection of miscellaneous data that doesn't fit
 * with existing keys but don't warrant for additional keys
 * due to how niche they are.
 */
interface MessageMetadata {
  /**
   * Quoted part of assistant message.
   *
   * Useful if you want to narrow down the context to specific phrases.
   */
  quote?: string;
}

const UploadedFileSchema = z.instanceof(Blob).refine(
  (file): file is UploadedFile => !('name' in file) || typeof (file as UploadedFile).name === 'string',
);

const MessageMetadataSchema = z.object({
  quote: z.string().optional(),
});

export const CreateMessagePayloadSchema = z.object({
  chatbot_id: z.string({ error: 'Chatbot ID is required' }),
  message: z.string({ error: 'Message is required' }),
  parent_id: z.string().optional(),
  source: z.string().optional(),
  user_id: z.string().optional(),
  conversation_id: z.string().optional(),
  user_message_id: z.string().optional(),
  assistant_message_id: z.string().optional(),
  chat_history: z.array(z.any()).optional(),
  files: z.array(UploadedFileSchema).optional(),
  stream_id: z.string().optional(),
  model_name: z.string().regex(/^.+\/.+$/).optional(),
  anonymize_em: z.boolean().optional(),
  anonymize_lm: z.boolean().optional(),
  use_cache: z.boolean().optional(),
  search_type: z.enum(['normal', 'web']).optional(),
  metadata: MessageMetadataSchema.optional(),
  additional_data: z.record(
    z.string(),
    z.union([
      z.string(),
      z.instanceof(Blob),
      z.null(),
      z.undefined(),
    ]),
  ).optional(),
});

/**
 * Data wrapper for deanonymized_message chunk.
 *
 * Stores both user and assistant plus their actual content mapped
 * in key-value objects.
 */
interface DeanomymizedData {
  /**
   * Deanonymization data for user message that triggers the request
   */
  user_message: DeanonymizedMessage;
  /**
   * Deanonymization data for assistant message
   */
  ai_message: DeanonymizedMessage;
  /**
   * Key-value mapping of anonymization for both user and assistant message
   */
  deanonymized_mapping: Record<string, string>;
}

/**
 * Actual message content of the deanonymized_message chunk.
 */
interface DeanonymizedMessage {
  /**
   * Message contentthat has been anonymized.
   */
  content: string;
  /**
   * Raw message content without anonymization. If the message
   * isn't going through anonymization step, this value will be `undefined`.
   */
  deanonymized_content?: string;
}

/**
 * Progress report of current message stream
 */
interface GLChatProcess {
  /**
   * Unique identifier of the process
   */
  id: string;

  /**
   * Human-readable message to be associated with the process
   */
  message?: string;
  /**
   * Status of the current progress
   */
  status: StepIndicatorStatus;
  /**
   * Unix timestamp that denotes when this process is created
   */
  time?: number;
}

/**
 * Attached binary data in form of File inside a message.
 */
interface GLChatAttachment {
  /**
   * Identifier of the attachment.
   *
   * Mainly used to interact with the attachment during edit / refresh flow.
   */
  id: string;
  /**
   * MIME type of the attachment.
   */
  type: string;
  /**
   * Name of the attachment.
   */
  name: string;
  /**
   * A public URL of the attachment.
   */
  url: string;
}

/**
 * Streamed data sent from GLChat API during message manipulation process.
 */
export type GLChatMessageChunk = GLChatMessageDataChunk
  | GLChatMessageResponseChunk
  | GLChatMessageBaseChunk<ProcessingDocument>;

interface GLChatMessageBaseChunk<T = GLChatMessageStatus> {
  /**
   * Conversation identifier where the message belongs to.
   */
  conversation_id: string | null;
  /**
   * Identifier of the user message.
   *
   * If the current message is an assistant message, this value
   * will be the ID of the user message that triggers the response.
   */
  user_message_id: string | null;
  /**
   * Identifier of the assitant message.
   *
   * If the current message is a user message, this value
   * will be the ID of the assistant message that complements the request.
   */
  assistant_message_id: string | null;
  /**
   * Unix timestamp when the chunk is created.
   */
  created_date: number;
  /**
   * An enum that denotes the type of the chunk.
   */
  status: T;

  message: unknown;
}

/**
 * A chunk that represents data related to the message manipulation process
 * that isn't the response itself.
 */
interface GLChatMessageDataChunk extends GLChatMessageBaseChunk<Data> {
  /**
   * Actual data content of the chunk.
   */
  message: GLChatReferenceChunk
    | GLChatAttachmentChunk
    | GLChatRelatedQuestionChunk
    | GLChatDeanonymizationChunk
    | GLChatMediaChunk
    | GLChatProcessChunk;
}

/**
 * Chunk that represents actual LLM or agent response.
 */
interface GLChatMessageResponseChunk extends GLChatMessageBaseChunk<Response> {
  /**
   * Response of LLM or agent.
   */
  message: string;
}

/**
 * Chunk that represents references that may exist in the actual response string.
 */
export interface GLChatReferenceChunk {
  data_type: 'reference';
  /**
   * List of references mentioned in the response string.
   */
  data_value: string[];
}

/**
 * Chunk that represents attachment binary of the message.
 */
export interface GLChatAttachmentChunk {
  data_type: 'attachments';
  /**
   * List of attachments of the message.
   */
  data_value: GLChatAttachment[];
}

/**
 * Chunk that represents questions related with the query
 * that triggers the chunk.
 */
export interface GLChatRelatedQuestionChunk {
  data_type: 'related';
  /**
   * List of related questions.
   */
  data_value: string[];
}

/**
 * Chunk that represents anonymization data of the message.
 */
export interface GLChatDeanonymizationChunk {
  data_type: 'deanonymized_data';
  /**
   * Anonymization result of the message.
   */
  data_value: DeanomymizedData;
}

/**
 * Chunk that represents key-value of media inside actual contents
 * represented by `[<media_type>_<id>]` string.
 */
export interface GLChatMediaChunk {
  data_type: 'media_mapping';
  /**
   * Key-value mapping of media that may exist inside actual contents
   * of the message.
   */
  data_value: Record<string, string>;
}

/**
 * Chunk that represents process of the message-manipulation request.
 */
export interface GLChatProcessChunk {
  data_type: 'process';
  /**
   * Current process of the request.
   */
  data_value: GLChatProcess;
}
