import React from 'react';
import { Send, User, Loader2, Menu, ChevronDown } from 'lucide-react';
import { useChatStore } from '@/stores/chatStore';
import type { UIMessage } from '@/types/chat';

interface MessageProps {
  message: UIMessage;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const isUser = message.type === 'user';
  
  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-dark-accent flex items-center justify-center flex-shrink-0">
          <img 
            src="https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7" 
            alt="LlamaBot" 
            className="w-8 h-8 rounded-full"
          />
        </div>
      )}
      
      <div className={`
        max-w-[70%] p-3 rounded-lg
        ${isUser 
          ? 'bg-dark-input text-dark-text rounded-br-sm' 
          : 'bg-dark-chat text-dark-text rounded-bl-sm border border-dark-border'
        }
      `}>
        <div className="whitespace-pre-wrap break-words">
          {message.content}
        </div>
        {message.timestamp && (
          <div className="text-xs text-dark-text/40 mt-2">
            {message.timestamp.toLocaleTimeString()}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-dark-input flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-dark-text" />
        </div>
      )}
    </div>
  );
};

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  isStreaming?: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({ 
  onSendMessage, 
  disabled = false,
  isStreaming = false 
}) => {
  const [input, setInput] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedInput = input.trim();
    if (trimmedInput && !disabled) {
      onSendMessage(trimmedInput);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="p-4 bg-dark-chat border-t border-dark-border">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={disabled}
          className="w-full p-3 border border-dark-border rounded-lg bg-dark-input text-dark-text 
                   placeholder-dark-text/50 focus:outline-none focus:border-dark-accent 
                   resize-none min-h-[2.5rem] max-h-48"
          rows={1}
          style={{
            height: 'auto',
            minHeight: '2.5rem',
          }}
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!input.trim() || disabled}
            className="flex items-center gap-2 px-4 py-2 bg-dark-accent text-white font-medium 
                     rounded-lg hover:bg-dark-accent/80 disabled:opacity-50 disabled:cursor-not-allowed 
                     transition-colors"
          >
            {isStreaming ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

// Helper function to format agent names for display
const formatAgentName = (agentName: string): string => {
  return agentName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export const ChatWindow: React.FC = () => {
  const { 
    currentMessages, 
    currentConversationId,
    isStreaming,
    error,
    isSidebarVisible,
    selectedAgent,
    availableAgents,
    isLoadingAgents,
    sendMessage,
    clearError,
    toggleSidebar,
    setSelectedAgent,
    loadAvailableAgents
  } = useChatStore();

  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const dropdownRef = React.useRef<HTMLDivElement>(null);
  const [isAgentDropdownOpen, setIsAgentDropdownOpen] = React.useState(false);

  // Auto-scroll to bottom when new messages arrive
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages]);

  // Load available agents on component mount
  React.useEffect(() => {
    loadAvailableAgents();
  }, [loadAvailableAgents]);

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsAgentDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSendMessage = (message: string) => {
    if (error) clearError();
    sendMessage(message);
  };

  const handleAgentSelect = (agent: string) => {
    setSelectedAgent(agent);
    setIsAgentDropdownOpen(false);
  };

  if (!currentConversationId) {
    return (
      <div className="flex-1 h-full flex flex-col bg-dark-chat">
        {/* Header - always show even when no conversation */}
        <div className="h-15 px-4 py-3 bg-dark-chat border-b border-dark-border flex items-center gap-3">
          {!isSidebarVisible && (
            <button
              onClick={toggleSidebar}
              className="p-2 text-dark-text hover:bg-dark-border/30 rounded transition-colors"
              title="Show sidebar"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}
          
          <img 
            src="https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7" 
            alt="LlamaBot" 
            className="w-8 h-8 rounded-full"
          />
          <h1 className="text-xl font-semibold text-dark-text">LlamaBot</h1>
          
          <div className="ml-auto flex items-center gap-4">
            {/* Agent Selector */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsAgentDropdownOpen(!isAgentDropdownOpen)}
                className="flex items-center gap-2 px-3 py-2 bg-dark-input border border-dark-border rounded-md text-dark-text hover:border-dark-accent transition-colors"
                disabled={isLoadingAgents}
              >
                <span className="text-sm">
                  {isLoadingAgents ? 'Loading...' : (selectedAgent ? formatAgentName(selectedAgent) : 'Select Agent')}
                </span>
                <ChevronDown className="w-4 h-4" />
              </button>
              
              {isAgentDropdownOpen && !isLoadingAgents && (
                <div className="absolute right-0 top-full mt-1 w-64 bg-dark-input border border-dark-border rounded-md shadow-lg z-50">
                  {availableAgents.length === 0 ? (
                    <div className="px-3 py-2 text-sm text-dark-text/60">
                      No agents available
                    </div>
                  ) : (
                    availableAgents.map((agent) => (
                      <button
                        key={agent}
                        onClick={() => handleAgentSelect(agent)}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-dark-border/30 transition-colors first:rounded-t-md last:rounded-b-md ${
                          selectedAgent === agent ? 'bg-dark-accent text-white' : 'text-dark-text'
                        }`}
                      >
                        {formatAgentName(agent)}
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex-1 flex items-center justify-center text-center text-dark-text/60">
          <div>
            <img 
              src="https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7" 
              alt="LlamaBot" 
              className="w-16 h-16 mx-auto mb-4 rounded-full opacity-30"
            />
            <h3 className="text-xl font-semibold mb-2">Welcome to LlamaBot</h3>
            <p>Select a conversation or start a new one to get started!</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 h-full flex flex-col bg-dark-chat">
      {/* Header */}
      <div className="h-15 px-4 py-3 bg-dark-chat border-b border-dark-border flex items-center gap-3">
        {!isSidebarVisible && (
          <button
            onClick={toggleSidebar}
            className="p-2 text-dark-text hover:bg-dark-border/30 rounded transition-colors"
            title="Show sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        
        <img 
          src="https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7" 
          alt="LlamaBot" 
          className="w-8 h-8 rounded-full"
        />
        <h1 className="text-xl font-semibold text-dark-text">LlamaBot</h1>
        {selectedAgent && (
          <span className="text-sm text-dark-text/60 px-2 py-1 bg-dark-input rounded-md">
            {formatAgentName(selectedAgent)}
          </span>
        )}
        {isStreaming && (
          <div className="text-sm text-dark-accent flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Thinking...
          </div>
        )}
        
        <div className="ml-auto flex items-center gap-4">
          {/* Agent Selector */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsAgentDropdownOpen(!isAgentDropdownOpen)}
              className="flex items-center gap-2 px-3 py-2 bg-dark-input border border-dark-border rounded-md text-dark-text hover:border-dark-accent transition-colors"
              disabled={isLoadingAgents}
            >
              <span className="text-sm">
                {isLoadingAgents ? 'Loading...' : (selectedAgent ? formatAgentName(selectedAgent) : 'Select Agent')}
              </span>
              <ChevronDown className="w-4 h-4" />
            </button>
            
            {isAgentDropdownOpen && !isLoadingAgents && (
              <div className="absolute right-0 top-full mt-1 w-64 bg-dark-input border border-dark-border rounded-md shadow-lg z-50">
                {availableAgents.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-dark-text/60">
                    No agents available
                  </div>
                ) : (
                  availableAgents.map((agent) => (
                    <button
                      key={agent}
                      onClick={() => handleAgentSelect(agent)}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-dark-border/30 transition-colors first:rounded-t-md last:rounded-b-md ${
                        selectedAgent === agent ? 'bg-dark-accent text-white' : 'text-dark-text'
                      }`}
                    >
                      {formatAgentName(agent)}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {currentMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-dark-text/60">
            <div className="text-center">
              <img 
                src="https://service-jobs-images.s3.us-east-2.amazonaws.com/7rl98t1weu387r43il97h6ipk1l7" 
                alt="LlamaBot" 
                className="w-12 h-12 mx-auto mb-3 rounded-full"
              />
              <p>Start a conversation by sending a message below!</p>
            </div>
          </div>
        ) : (
          currentMessages.map((message) => (
            <Message key={message.id} message={message} />
          ))
        )}
        
        {/* Error display */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg mb-4">
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
            <button 
              onClick={clearError}
              className="text-xs underline mt-1 hover:no-underline"
            >
              Dismiss
            </button>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput 
        onSendMessage={handleSendMessage}
        disabled={isStreaming}
        isStreaming={isStreaming}
      />
    </div>
  );
}; 