import axios from 'axios';
import type { 
  Conversation, 
  ChatMessageRequest, 
  StreamResponse,
  ConversationSummary,
  UIMessage,
  Message 
} from '@/types/chat';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

class ApiService {
  // Fetch all conversations/threads
  async getConversations(): Promise<Conversation[]> {
    const response = await api.get<Conversation[]>('/threads');
    return response.data;
  }

  // Fetch specific conversation history
  async getConversationHistory(threadId: string): Promise<Conversation> {
    const response = await api.get<Conversation>(`/chat-history/${threadId}`);
    return response.data;
  }

  // Send message with streaming response
  async sendMessage(
    request: ChatMessageRequest,
    onUpdate: (response: StreamResponse) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body reader available');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue;

          try {
            const data: StreamResponse = JSON.parse(line);
            onUpdate(data);
          } catch (parseError) {
            console.error('Error parsing stream data:', parseError, line);
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error : new Error('Unknown error occurred'));
    }
  }

  // Utility function to convert API messages to UI messages
  convertToUIMessages(messages: Message[]): UIMessage[] {
    return messages.map((msg) => ({
      id: msg.id,
      type: msg.type === 'human' ? 'user' : 'ai',
      content: msg.content,
      timestamp: new Date(), // You might want to extract timestamp from the message if available
    }));
  }

  // Generate conversation summary from messages
  generateConversationSummary(conversation: Conversation): ConversationSummary {
    const messages = conversation.state[0]?.messages || [];
    const firstUserMessage = messages.find(msg => msg.type === 'human');
    const lastMessage = messages[messages.length - 1];
    
    let title = 'New Conversation';
    if (firstUserMessage?.content) {
      title = firstUserMessage.content.substring(0, 50);
      if (firstUserMessage.content.length > 50) {
        title += '...';
      }
    }

    let preview = 'No messages yet...';
    if (lastMessage?.content) {
      preview = lastMessage.content.substring(0, 100);
      if (lastMessage.content.length > 100) {
        preview += '...';
      }
    }

    return {
      id: conversation.thread_id,
      title,
      preview,
      lastMessage: lastMessage?.content,
      timestamp: new Date(), // You might want to extract actual timestamp
      messageCount: messages.length,
    };
  }

  // Generate unique thread ID
  generateThreadId(): string {
    const timestamp = Date.now();
    const randomComponent = Math.random().toString(36).substring(2, 8);
    return `thread_${timestamp}_${randomComponent}`;
  }

  // Fetch available agents
  async getAvailableAgents(): Promise<string[]> {
    const response = await api.get<{ agents: string[] }>('/available-agents');
    return response.data.agents;
  }
}

export const apiService = new ApiService();
export default apiService; 