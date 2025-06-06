import React from 'react';
import { Plus, MessageCircle, ChevronLeft } from 'lucide-react';
import { useChatStore } from '@/stores/chatStore';
import type { ConversationSummary } from '@/types/chat';

interface ConversationItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onClick: () => void;
}

const ConversationItem: React.FC<ConversationItemProps> = ({ 
  conversation, 
  isActive, 
  onClick 
}) => {
  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return timestamp.toLocaleDateString();
  };

  return (
    <div
      className={`
        p-4 cursor-pointer transition-colors border-b border-dark-border/20
        hover:bg-dark-border/30
        ${isActive ? 'bg-dark-input border-l-4 border-l-dark-accent' : ''}
      `}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <MessageCircle className="w-4 h-4 mt-1 text-dark-accent flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-dark-text text-sm truncate mb-1">
            {conversation.title}
          </h3>
          <p className="text-xs text-dark-text/60 line-clamp-2 mb-2">
            {conversation.preview}
          </p>
          <div className="flex items-center justify-between text-xs text-dark-text/40">
            <span>{formatTime(conversation.timestamp)}</span>
            <span>{conversation.messageCount} messages</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const ConversationSidebar: React.FC = () => {
  const { 
    conversations, 
    currentConversationId, 
    isLoading,
    isSidebarVisible,
    selectConversation,
    createNewConversation,
    loadConversations,
    toggleSidebar,
    error
  } = useChatStore();

  React.useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleNewChat = () => {
    createNewConversation();
  };

  const handleSelectConversation = (conversationId: string) => {
    selectConversation(conversationId);
  };

  if (!isSidebarVisible) {
    return null;
  }

  return (
    <div className="w-1/4 h-full flex flex-col bg-dark-sidebar border-r border-dark-border">
      {/* Header */}
      <div className="h-15 px-4 py-3 bg-dark-chat border-b border-dark-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-dark-text">Conversations</h2>
          <button
            onClick={toggleSidebar}
            className="p-1 text-dark-text/60 hover:text-dark-text hover:bg-dark-border/30 rounded transition-colors"
            title="Collapse sidebar"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
        <button
          onClick={handleNewChat}
          className="flex items-center gap-2 px-3 py-2 bg-dark-accent text-white text-sm font-medium rounded-md hover:bg-dark-accent/80 transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading && conversations.length === 0 ? (
          <div className="p-4 text-center text-dark-text/60">
            <div className="animate-spin w-6 h-6 border-2 border-dark-accent border-t-transparent rounded-full mx-auto mb-2"></div>
            Loading conversations...
          </div>
        ) : error ? (
          <div className="p-4 text-center">
            <p className="text-red-400 mb-2">Error loading conversations</p>
            <button 
              onClick={loadConversations}
              className="px-3 py-2 bg-dark-accent text-white text-sm rounded-md hover:bg-dark-accent/80"
            >
              Retry
            </button>
          </div>
        ) : conversations.length === 0 ? (
          <div className="p-4 text-center text-dark-text/60">
            <MessageCircle className="w-12 h-12 mx-auto mb-3 text-dark-text/30" />
            <p className="text-sm mb-2">No conversations yet</p>
            <p className="text-xs">Start a new conversation to get started!</p>
          </div>
        ) : (
          conversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isActive={conversation.id === currentConversationId}
              onClick={() => handleSelectConversation(conversation.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}; 