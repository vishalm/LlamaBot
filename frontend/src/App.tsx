import React from 'react';
import { ConversationSidebar } from './components/ConversationSidebar';
import { ChatWindow } from './components/ChatWindow';
import './index.css';

function App() {
  return (
    <div className="h-screen bg-dark-bg text-dark-text flex">
      <ConversationSidebar />
      <ChatWindow />
    </div>
  );
}

export default App; 