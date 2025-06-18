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

/**
 * Custom file type of files for message-related functionality.
 *
 * Mainly made to maintain runtime-compatibility with Bun, since Bun
 * doesn't support `File` natively.
 */
interface UploadedFile extends Blob {
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

interface DeanomymizedData {
  user_message: DeanonymizedMessage;
  ai_message: DeanonymizedMessage;
  deanonymized_mapping: Record<string, string>;
}

interface DeanonymizedMessage {
  content: string;
  deanonymized_content?: string;
}

interface GLChatProcess {
  id: string;

  message?: string;
  status: StepIndicatorStatus;
  time?: number;
}

interface GLChatAttachment {
  id: string;
  type: string;
  name: string;
  size: number;

  url?: string;
}

export type GLChatMessageChunk = GLChatMessageDataChunk
  | GLChatMessageResponseChunk
  | GLChatMessageBaseChunk<ProcessingDocument>;

interface GLChatMessageBaseChunk<T = GLChatMessageStatus> {
  conversation_id: string | null;
  user_message_id: string | null;
  assistant_message_id: string | null;
  created_date: number;
  status: T;
}

interface GLChatMessageDataChunk extends GLChatMessageBaseChunk<Data> {
  message: GLChatReferenceChunk
    | GLChatAttachmentChunk
    | GLChatRelatedQuestionChunk
    | GLChatDeanonymizationChunk
    | GLChatMediaChunk
    | GLChatProcessChunk;
}

interface GLChatMessageResponseChunk extends GLChatMessageBaseChunk<Response> {
  message: string;
}

export interface GLChatReferenceChunk {
  data_type: 'reference';
  data_value: string[];
}

export interface GLChatAttachmentChunk {
  data_type: 'attachments';
  data_value: GLChatAttachment[];
}

export interface GLChatRelatedQuestionChunk {
  data_type: 'related';
  data_value: string[];
}

export interface GLChatDeanonymizationChunk {
  data_type: 'deanonymized_data';
  data_value: DeanomymizedData;
}

export interface GLChatMediaChunk {
  data_type: 'media_mapping';
  data_value: Record<string, string>;
}

export interface GLChatProcessChunk {
  data_type: 'process';
  data_value: GLChatProcess;
}
