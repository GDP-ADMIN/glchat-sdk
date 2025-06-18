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

type SearchType = 'normal' | 'web';

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

export interface GLChatMessageGenerationChunk {
  conversation_id: string | null;
  user_message_id: string | null;
  assistant_message_id: string | null;
  created_date: number;
  status: 'data' | 'response';
  messsage: GLChatMessageChunk;
}

export interface GLChatMessageChunk {
  data_type: string;
  data_value: string;
}

export interface GLChatReferenceChunk {

}

export interface GLChatAttachmentChunk {

}
