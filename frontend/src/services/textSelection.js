/**
 * Text Selection Detection Utility
 * Provides functionality to detect and retrieve selected text on a webpage
 */

class TextSelectionService {
  /**
   * Get the currently selected text in the document
   * @returns {string} The selected text, or empty string if no text is selected
   */
  static getSelectedText() {
    return window.getSelection ? window.getSelection().toString().trim() : '';
  }

  /**
   * Get detailed information about the current text selection
   * @returns {Object|null} Selection info including text, start/end positions, or null if no selection
   */
  static getSelectionInfo() {
    const selection = window.getSelection ? window.getSelection() : null;

    if (!selection || selection.toString().trim() === '') {
      return null;
    }

    const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

    if (!range) {
      return {
        text: selection.toString().trim(),
        startContainer: null,
        endContainer: null,
        startOffset: null,
        endOffset: null
      };
    }

    return {
      text: selection.toString().trim(),
      startContainer: range.startContainer,
      endContainer: range.endContainer,
      startOffset: range.startOffset,
      endOffset: range.endOffset,
      rect: range.getBoundingClientRect()
    };
  }

  /**
   * Check if there is currently selected text
   * @returns {boolean} True if text is selected, false otherwise
   */
  static hasSelection() {
    return this.getSelectedText().length > 0;
  }

  /**
   * Add an event listener for text selection changes
   * @param {Function} callback - Function to call when selection changes
   * @returns {Function} Function to remove the event listener
   */
  static addSelectionListener(callback) {
    const handler = () => {
      const selectionInfo = this.getSelectionInfo();
      callback(selectionInfo);
    };

    document.addEventListener('selectionchange', handler);

    // Return a function to remove the event listener
    return () => {
      document.removeEventListener('selectionchange', handler);
    };
  }

  /**
   * Highlight selected text with a custom style
   * @param {string} highlightClass - CSS class name to apply to highlighted text
   */
  static highlightSelection(highlightClass = 'textbot-highlight') {
    if (!this.hasSelection()) return;

    const selection = window.getSelection();
    if (selection.rangeCount === 0) return;

    const range = selection.getRangeAt(0);
    const preSelectionRange = range.cloneRange();

    // Create a new span element with the highlight class
    const highlightElement = document.createElement('span');
    highlightElement.className = highlightClass;

    // Surround the selected content with the highlight element
    preSelectionRange.selectNodeContents(range.startContainer);
    preSelectionRange.setEnd(range.endContainer, range.endOffset);

    const content = preSelectionRange.extractContents();
    highlightElement.appendChild(content);
    range.insertNode(highlightElement);
  }

  /**
   * Remove all highlights created by highlightSelection
   * @param {string} highlightClass - CSS class name of highlights to remove
   */
  static removeHighlights(highlightClass = 'textbot-highlight') {
    const highlightedElements = document.querySelectorAll(`.${highlightClass}`);
    highlightedElements.forEach(element => {
      // Extract the content from the highlight element
      const content = element.innerHTML;
      const textNode = document.createTextNode(content);

      // Replace the highlight element with its content
      element.parentNode.replaceChild(textNode, element);
    });
  }

  /**
   * Get the context around the selected text (surrounding text)
   * @param {number} contextLength - Number of characters before and after selection
   * @returns {Object} Object with selected text and surrounding context
   */
  static getSelectionWithContext(contextLength = 100) {
    const selectionInfo = this.getSelectionInfo();
    if (!selectionInfo) return null;

    const selectedText = selectionInfo.text;

    // Get the surrounding text context
    let contextBefore = '';
    let contextAfter = '';

    // This is a simplified approach - in a real implementation you might want to
    // get the actual surrounding text from the DOM
    if (selectionInfo.startContainer && selectionInfo.startContainer.textContent) {
      const fullText = selectionInfo.startContainer.textContent;
      const startIndex = fullText.indexOf(selectedText);

      if (startIndex !== -1) {
        const start = Math.max(0, startIndex - contextLength);
        const end = Math.min(fullText.length, startIndex + selectedText.length + contextLength);

        contextBefore = fullText.substring(start, startIndex);
        contextAfter = fullText.substring(startIndex + selectedText.length, end);
      }
    }

    return {
      selectedText,
      contextBefore,
      contextAfter
    };
  }
}

export default TextSelectionService;