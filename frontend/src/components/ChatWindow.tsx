import React from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
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
          <Bot className="w-4 h-4 text-white" />
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

export const ChatWindow: React.FC = () => {
  const { 
    currentMessages, 
    currentConversationId,
    isStreaming,
    error,
    sendMessage,
    clearError 
  } = useChatStore();

  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages]);

  const handleSendMessage = (message: string) => {
    if (error) clearError();
    sendMessage(message);
  };

  if (!currentConversationId) {
    return (
      <div className="flex-1 h-full flex flex-col bg-dark-chat">
        <div className="flex-1 flex items-center justify-center text-center text-dark-text/60">
          <div>
            <Bot className="w-16 h-16 mx-auto mb-4 text-dark-text/30" />
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
        <Bot className="w-8 h-8 text-dark-accent" />
        <h1 className="text-xl font-semibold text-dark-text">LlamaBot</h1>
        {isStreaming && (
          <div className="text-sm text-dark-accent flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Thinking...
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {currentMessages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-dark-text/60">
            <div className="text-center">
              <Bot className="w-12 h-12 mx-auto mb-3 text-dark-accent" />
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