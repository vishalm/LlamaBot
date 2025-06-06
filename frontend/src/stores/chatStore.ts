import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { ConversationSummary, UIMessage, StreamResponse } from '@/types/chat';
import apiService from '@/services/api';

interface ChatState {
  // Conversations
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  currentMessages: UIMessage[];
  
  // UI State
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  isSidebarVisible: boolean;
  selectedAgent: string;
  availableAgents: string[];
  isLoadingAgents: boolean;
  
  // Actions
  loadConversations: () => Promise<void>;
  selectConversation: (conversationId: string) => Promise<void>;
  createNewConversation: () => void;
  sendMessage: (message: string) => Promise<void>;
  setError: (error: string | null) => void;
  clearError: () => void;
  toggleSidebar: () => void;
  setSelectedAgent: (agent: string) => void;
  loadAvailableAgents: () => Promise<void>;
}

export const useChatStore = create<ChatState>()(
  devtools(
    (set, get) => ({
      // Initial state
      conversations: [],
      currentConversationId: null,
      currentMessages: [],
      isLoading: false,
      isStreaming: false,
      error: null,
      isSidebarVisible: true,
      selectedAgent: '',
      availableAgents: [],
      isLoadingAgents: false,

      // Load all conversations
      loadConversations: async () => {
        set({ isLoading: true, error: null });
        try {
          const conversations = await apiService.getConversations();
          const summaries = conversations.map(conv => 
            apiService.generateConversationSummary(conv)
          );
          
          set({ 
            conversations: summaries,
            isLoading: false 
          });

          // Auto-select first conversation if available
          if (summaries.length > 0 && !get().currentConversationId) {
            get().selectConversation(summaries[0].id);
          }
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load conversations',
            isLoading: false 
          });
        }
      },

      // Select and load a specific conversation
      selectConversation: async (conversationId: string) => {
        set({ isLoading: true, error: null });
        try {
          console.log('Loading conversation:', conversationId);
          const conversation = await apiService.getConversationHistory(conversationId);
          console.log('Conversation data:', conversation);
          
          // Since it's an array, let's check each element for messages
          let messages: any[] = [];
          
          if (Array.isArray(conversation)) {
            console.log('Searching for messages in array elements...');
            conversation.forEach((element, index) => {
              console.log(`Element ${index}:`, element);
              
              // Check if this element has messages
              if (element && typeof element === 'object') {
                if (element.messages && Array.isArray(element.messages)) {
                  console.log(`Found messages in element ${index}:`, element.messages);
                  messages = element.messages;
                } else if (element.state && element.state.messages) {
                  console.log(`Found messages in element ${index}.state:`, element.state.messages);
                  messages = element.state.messages;
                }
              }
            });
          } else {
            // Original logic for object structure
            messages = conversation.state?.messages || [];
          }
          
          console.log('Final messages:', messages);
          
          const uiMessages = apiService.convertToUIMessages(messages);
          console.log('UI messages:', uiMessages);
          
          set({
            currentConversationId: conversationId,
            currentMessages: uiMessages,
            isLoading: false
          });
        } catch (error) {
          console.error('Error loading conversation:', error);
          set({ 
            error: error instanceof Error ? error.message : 'Failed to load conversation',
            isLoading: false,
            currentMessages: []
          });
        }
      },

      // Create a new conversation
      createNewConversation: () => {
        const newId = apiService.generateThreadId();
        const newConversation: ConversationSummary = {
          id: newId,
          title: 'New Conversation',
          preview: 'Start a new conversation...',
          timestamp: new Date(),
          messageCount: 0,
        };

        set({
          currentConversationId: newId,
          currentMessages: [],
          conversations: [newConversation, ...get().conversations],
        });
      },

      // Send a message
      sendMessage: async (message: string) => {
        const { currentConversationId, currentMessages, selectedAgent } = get();
        
        if (!currentConversationId) {
          set({ error: 'No conversation selected' });
          return;
        }

        // Add user message immediately
        const userMessage: UIMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: message,
          timestamp: new Date(),
        };

        set({
          currentMessages: [...currentMessages, userMessage],
          isStreaming: true,
          error: null,
        });

        // Create placeholder for AI response
        const aiMessageId = (Date.now() + 1).toString();
        const aiMessage: UIMessage = {
          id: aiMessageId,
          type: 'ai',
          content: '',
          timestamp: new Date(),
        };

        set({
          currentMessages: [...get().currentMessages, aiMessage],
        });

        try {
          await apiService.sendMessage(
            {
              message,
              thread_id: currentConversationId,
              agent: selectedAgent,
            },
            (response: StreamResponse) => {
              const messages = get().currentMessages;
              const aiMessageIndex = messages.findIndex(m => m.id === aiMessageId);
              
              if (response.type === 'update' && response.value) {
                // Update AI message content
                const updatedMessages = [...messages];
                if (aiMessageIndex !== -1) {
                  updatedMessages[aiMessageIndex] = {
                    ...updatedMessages[aiMessageIndex],
                    content: updatedMessages[aiMessageIndex].content + response.value,
                  };
                  set({ currentMessages: updatedMessages });
                }
              } else if (response.type === 'final' && response.messages) {
                // Final response with complete message
                const lastMessage = response.messages[response.messages.length - 1];
                if (lastMessage && aiMessageIndex !== -1) {
                  const updatedMessages = [...messages];
                  updatedMessages[aiMessageIndex] = {
                    ...updatedMessages[aiMessageIndex],
                    content: lastMessage.content,
                  };
                  set({ currentMessages: updatedMessages });
                }
              } else if (response.type === 'error') {
                set({ error: response.error || 'Unknown error occurred' });
              }
            },
            (error: Error) => {
              set({ error: error.message });
            }
          );
        } catch (error) {
          set({ 
            error: error instanceof Error ? error.message : 'Failed to send message' 
          });
        } finally {
          set({ isStreaming: false });
        }
      },

      // Set error
      setError: (error: string | null) => {
        set({ error });
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },

      // Toggle sidebar visibility
      toggleSidebar: () => {
        set({ isSidebarVisible: !get().isSidebarVisible });
      },

      // Set selected agent
      setSelectedAgent: (agent: string) => {
        set({ selectedAgent: agent });
      },

      // Load available agents
      loadAvailableAgents: async () => {
        set({ isLoadingAgents: true });
        try {
          const agents = await apiService.getAvailableAgents();
          set({
            availableAgents: agents,
            isLoadingAgents: false,
            // Set first agent as default if none selected
            selectedAgent: get().selectedAgent || agents[0] || ''
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to load available agents',
            isLoadingAgents: false
          });
        }
      },
    }),
    {
      name: 'chat-store',
    }
  )
); 