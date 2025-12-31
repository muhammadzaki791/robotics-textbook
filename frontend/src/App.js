import React from 'react';
import ChatbotWidget from './components/ChatbotWidget';
import './styles/main.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Physical AI & Humanoid Robotics Textbook Assistant</h1>
        <p>Ask questions about the textbook content using AI-powered search</p>
      </header>
      <main className="app-main">
        <ChatbotWidget />
      </main>
    </div>
  );
}

export default App;