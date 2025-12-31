import React, { useRef } from 'react';
import useChat from '../hooks/useChat';
import ChatInput from './ChatInput';
import Message from './Message';
import '../styles/chatbot.css';

const ChatbotWidget = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="chatbot-widget">
      <div className="chat-header">
        <h3>Textbook Assistant</h3>
      </div>
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Hello! I'm your Physical AI & Humanoid Robotics textbook assistant.</p>
            <p>Ask me any questions about the content, and I'll find the answers for you.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <Message
              key={msg.id}
              text={msg.text}
              sender={msg.sender}
              sources={msg.sources}
            />
          ))
        )}
        {isLoading && (
          <div className="message bot-message">
            <div className="message-text">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={sendMessage} disabled={isLoading} />
    </div>
  );
};

export default ChatbotWidget;