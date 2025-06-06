import React from 'react';
import { ConversationSidebar } from './components/ConversationSidebar';
import { ChatWindow } from './components/ChatWindow';
import { useChatStore } from './stores/chatStore';
import './index.css';

function App() {
  const { isSidebarVisible } = useChatStore();

  return (
    <div className="h-screen bg-dark-bg text-dark-text flex">
      <ConversationSidebar />
      <ChatWindow />
    </div>
  );
}

export default App; 