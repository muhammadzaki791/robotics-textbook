import React, { useState, useEffect } from 'react';
import useTextSelection from '../hooks/useTextSelection';

const ChatInput = ({ onSendMessage, disabled }) => {
  const [inputValue, setInputValue] = useState('');
  const { selection, hasSelection } = useTextSelection();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      // Create the message object with selected text if available
      const messageObject = {
        question: inputValue,
        selectedText: hasSelection ? selection : null
      };

      onSendMessage(messageObject);
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-fill the input if there's selected text and the input is empty
  useEffect(() => {
    if (hasSelection && !inputValue) {
      setInputValue(`About this text: "${selection}" `);
    }
  }, [hasSelection, selection, inputValue]);

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <div className="input-container">
        <textarea
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={hasSelection
            ? `Ask about selected text: "${selection.substring(0, 30)}${selection.length > 30 ? '...' : ''}"`
            : "Ask a question about the textbook..."}
          disabled={disabled}
          rows="1"
        />
        <button
          type="submit"
          className="send-button"
          disabled={disabled || !inputValue.trim()}
        >
          Send
        </button>
      </div>
    </form>
  );
};

export default ChatInput;