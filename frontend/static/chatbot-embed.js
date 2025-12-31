/**
 * Chatbot Embed Script for Docusaurus Integration
 * This script allows the chatbot to be embedded in Docusaurus sites
 */

(function() {
  // Configuration
  const CONFIG = {
    apiBaseUrl: window.CHATBOT_CONFIG?.apiBaseUrl || '/api',
    containerId: 'chatbot-container',
    widgetTitle: 'Textbook Assistant',
    position: 'bottom-right', // bottom-left, bottom-right, top-left, top-right
    zIndex: 1000
  };

  // Create the chatbot container element
  function createChatbotContainer() {
    const container = document.createElement('div');
    container.id = CONFIG.containerId;
    container.className = 'chatbot-embed-container';
    container.style.cssText = `
      position: fixed;
      ${CONFIG.position.includes('bottom') ? 'bottom' : 'top'}: 20px;
      ${CONFIG.position.includes('right') ? 'right' : 'left'}: 20px;
      width: 380px;
      height: 500px;
      z-index: ${CONFIG.zIndex};
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      border-radius: 12px;
      overflow: hidden;
      display: none;
      background: white;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    `;
    return container;
  }

  // Create the toggle button
  function createToggleButton() {
    const button = document.createElement('button');
    button.className = 'chatbot-toggle-button';
    button.innerHTML = '💬';
    button.style.cssText = `
      position: fixed;
      ${CONFIG.position.includes('bottom') ? 'bottom' : 'top'}: 20px;
      ${CONFIG.position.includes('right') ? 'right' : 'left'}: 20px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      border: none;
      background: #4a6cf7;
      color: white;
      font-size: 24px;
      cursor: pointer;
      z-index: ${CONFIG.zIndex + 1};
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
    `;

    button.addEventListener('click', toggleChatbot);
    return button;
  }

  // Toggle chatbot visibility
  function toggleChatbot() {
    const container = document.getElementById(CONFIG.containerId);
    const button = document.querySelector('.chatbot-toggle-button');

    if (container.style.display === 'none') {
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      button.innerHTML = '✕';
      button.style.background = '#e53e3e';
    } else {
      container.style.display = 'none';
      button.innerHTML = '💬';
      button.style.background = '#4a6cf7';
    }
  }

  // Create the chatbot UI
  function createChatbotUI() {
    const chatDiv = document.createElement('div');
    chatDiv.innerHTML = `
      <div id="chat-header" style="
        background: #4a6cf7;
        color: white;
        padding: 16px;
        text-align: center;
        font-weight: bold;
      ">
        ${CONFIG.widgetTitle}
      </div>
      <div id="chat-messages" style="
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-height: 400px;
      ">
        <div style="
          text-align: center;
          color: #666;
          font-style: italic;
          padding: 20px 0;
        ">
          <p>Hello! I'm your Physical AI & Humanoid Robotics textbook assistant.</p>
          <p>Ask me any questions about the content, and I'll find the answers for you.</p>
        </div>
      </div>
      <div id="chat-input-container" style="
        padding: 16px;
        border-top: 1px solid #e0e0e0;
        background: white;
      ">
        <div style="display: flex; gap: 8px;">
          <textarea
            id="chat-input"
            placeholder="Ask a question about the textbook..."
            style="
              flex: 1;
              padding: 12px;
              border: 1px solid #ddd;
              border-radius: 24px;
              resize: none;
              min-height: 40px;
              font-family: inherit;
            "
          ></textarea>
          <button
            id="send-button"
            style="
              padding: 12px 20px;
              background: #4a6cf7;
              color: white;
              border: none;
              border-radius: 24px;
              cursor: pointer;
              font-weight: bold;
            "
          >
            Send
          </button>
        </div>
      </div>
    `;

    // Add event listeners
    const input = chatDiv.querySelector('#chat-input');
    const sendButton = chatDiv.querySelector('#send-button');

    sendButton.addEventListener('click', sendMessage);

    input.addEventListener('keypress', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    return chatDiv;
  }

  // Send message to API
  async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    const messagesContainer = document.getElementById('chat-messages');

    // Add user message
    const userMessage = document.createElement('div');
    userMessage.className = 'user-message';
    userMessage.style.cssText = `
      align-self: flex-end;
      background: #e3f2fd;
      border-radius: 18px 18px 4px 18px;
      padding: 12px 16px;
      max-width: 80%;
      text-align: right;
      margin-bottom: 12px;
    `;
    userMessage.textContent = message;
    messagesContainer.appendChild(userMessage);

    // Clear input
    input.value = '';

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      // Show typing indicator
      const typingIndicator = document.createElement('div');
      typingIndicator.id = 'typing-indicator';
      typingIndicator.innerHTML = `
        <div style="
          display: flex;
          align-items: center;
          justify-content: flex-start;
          margin-bottom: 12px;
        ">
          <div style="
            background: #f5f5f5;
            border-radius: 18px 18px 18px 4px;
            padding: 12px 16px;
            max-width: 80%;
          ">
            <div style="display: flex; align-items: center;">
              <div style="
                height: 8px;
                width: 8px;
                background: #9e9e9e;
                border-radius: 50%;
                display: inline-block;
                margin: 0 2px;
                animation: typing 1.4s infinite ease-in-out both;
              "></div>
              <div style="
                height: 8px;
                width: 8px;
                background: #9e9e9e;
                border-radius: 50%;
                display: inline-block;
                margin: 0 2px;
                animation: typing 1.4s infinite ease-in-out both;
                animation-delay: -0.32s;
              "></div>
              <div style="
                height: 8px;
                width: 8px;
                background: #9e9e9e;
                border-radius: 50%;
                display: inline-block;
                margin: 0 2px;
                animation: typing 1.4s infinite ease-in-out both;
                animation-delay: -0.16s;
              "></div>
            </div>
          </div>
        </div>
      `;

      // Add CSS for typing animation
      if (!document.querySelector('#typing-animation')) {
        const style = document.createElement('style');
        style.id = 'typing-animation';
        style.textContent = `
          @keyframes typing {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
          }
        `;
        document.head.appendChild(style);
      }

      messagesContainer.appendChild(typingIndicator);
      messagesContainer.scrollTop = messagesContainer.scrollHeight;

      // Call API
      const response = await fetch(`${CONFIG.apiBaseUrl}/chat/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: message }),
      });

      // Remove typing indicator
      const typingEl = document.getElementById('typing-indicator');
      if (typingEl) typingEl.remove();

      if (response.ok) {
        const data = await response.json();

        // Add bot message
        const botMessage = document.createElement('div');
        botMessage.className = 'bot-message';
        botMessage.style.cssText = `
          align-self: flex-start;
          background: #f5f5f5;
          border-radius: 18px 18px 18px 4px;
          padding: 12px 16px;
          max-width: 80%;
          margin-bottom: 12px;
        `;
        botMessage.innerHTML = `<div>${data.answer.replace(/\n/g, '<br>')}</div>`;

        messagesContainer.appendChild(botMessage);
      } else {
        // Add error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'bot-message';
        errorMessage.style.cssText = `
          align-self: flex-start;
          background: #f5f5f5;
          border-radius: 18px 18px 18px 4px;
          padding: 12px 16px;
          max-width: 80%;
          margin-bottom: 12px;
        `;
        errorMessage.textContent = "Sorry, I'm having trouble connecting to the server. Please try again later.";

        messagesContainer.appendChild(errorMessage);
      }
    } catch (error) {
      // Remove typing indicator
      const typingEl = document.getElementById('typing-indicator');
      if (typingEl) typingEl.remove();

      // Add error message
      const errorMessage = document.createElement('div');
      errorMessage.className = 'bot-message';
      errorMessage.style.cssText = `
        align-self: flex-start;
        background: #f5f5f5;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        max-width: 80%;
        margin-bottom: 12px;
      `;
      errorMessage.textContent = "Sorry, I'm having trouble connecting to the server. Please try again later.";

      messagesContainer.appendChild(errorMessage);
    }

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Initialize the chatbot
  function initChatbot() {
    // Check if chatbot is already initialized
    if (document.getElementById(CONFIG.containerId)) return;

    // Create and add elements to the page
    const container = createChatbotContainer();
    const toggleButton = createToggleButton();
    const chatUI = createChatbotUI();

    container.appendChild(chatUI);

    document.body.appendChild(toggleButton);
    document.body.appendChild(container);
  }

  // Initialize when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initChatbot);
  } else {
    initChatbot();
  }
})();