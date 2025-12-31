/**
 * API service for the RAG Chatbot
 */

// Handle environment variables properly for browser
const API_BASE_URL = (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_BASE_URL)
  ? process.env.REACT_APP_API_BASE_URL
  : 'http://localhost:8000';

class ApiService {
  /**
   * Ask a question to the textbook assistant
   * @param {string|Object} questionData - Either a string question or an object with question and selected_text
   * @returns {Promise<Object>} The response from the chatbot
   */
  static async askQuestion(questionData) {
    let payload;

    if (typeof questionData === 'string') {
      payload = { question: questionData };
    } else if (typeof questionData === 'object') {
      // Handle object format with question and optional selected_text
      payload = {
        question: questionData.question || questionData.text || '',
        selected_text: questionData.selected_text || questionData.selectedText || null
      };
    } else {
      throw new Error('Invalid question data format');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/chat/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  }

  /**
   * Get chat health status
   * @returns {Promise<Object>} Health check response
   */
  static async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/health`);
      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  /**
   * Get document information
   * @returns {Promise<Object>} Document information
   */
  static async getDocuments() {
    try {
      const response = await fetch(`${API_BASE_URL}/documents`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  }
}

export default ApiService;