// Message types based on the API structure
export interface BaseMessage {
  content: string;
  additional_kwargs: Record<string, unknown>;
  response_metadata: Record<string, unknown>;
  type: 'human' | 'ai';
  name: string | null;
  id: string;
  example: boolean;
}

export interface AIMessage extends BaseMessage {
  type: 'ai';
  tool_calls: unknown[];
  invalid_tool_calls: unknown[];
  usage_metadata: unknown | null;
}

export interface HumanMessage extends BaseMessage {
  type: 'human';
}

export type Message = AIMessage | HumanMessage;

// Conversation/Thread types
export interface ConversationState {
  messages: Message[];
}

export interface Conversation {
  thread_id: string;
  state: ConversationState;
}

// UI-specific message type for easier handling
export interface UIMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp?: Date;
}

// API request/response types
export interface ChatMessageRequest {
  message: string;
  thread_id?: string;
  agent?: string;
}

export interface StreamResponse {
  type: 'start' | 'update' | 'final' | 'error';
  request_id?: string;
  node?: string;
  value?: string;
  error?: string;
  messages?: Message[];
}

// UI State types
export interface ConversationSummary {
  id: string;
  title: string;
  preview: string;
  lastMessage?: string;
  timestamp: Date;
  messageCount: number;
} 