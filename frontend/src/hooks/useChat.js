import { useState, useCallback } from 'react';
import ApiService from '../services/api';

const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addMessage = useCallback((message) => {
    setMessages(prev => [...prev, message]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const sendMessage = useCallback(async (messageData) => {
    // Handle both string (for backward compatibility) and object formats
    let question, selectedText;

    if (typeof messageData === 'string') {
      question = messageData;
      selectedText = null;
    } else if (typeof messageData === 'object' && messageData.question) {
      question = messageData.question;
      selectedText = messageData.selectedText || null;
    } else {
      return; // Invalid input
    }

    if (!question.trim() || isLoading) return;

    try {
      setIsLoading(true);
      setError(null);

      // Add user message
      const userMessage = {
        id: Date.now(),
        text: question,
        sender: 'user',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);

      // Prepare the request payload
      const requestPayload = { question };
      if (selectedText) {
        requestPayload.selected_text = selectedText;
      }

      // Get response from API
      const response = await ApiService.askQuestion(requestPayload);

      const botMessage = {
        id: Date.now() + 1,
        text: response.answer,
        sender: 'bot',
        sources: response.sources || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        id: Date.now() + 1,
        text: "Sorry, I'm having trouble connecting to the server. Please try again later.",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    addMessage,
    clearMessages
  };
};

export default useChat;