import { useState, useEffect, useCallback } from 'react';
import TextSelectionService from '../services/textSelection';

const useTextSelection = () => {
  const [selection, setSelection] = useState({
    text: '',
    rect: null,
    hasSelection: false,
    context: null
  });

  const updateSelection = useCallback(() => {
    const selectionInfo = TextSelectionService.getSelectionInfo();

    if (selectionInfo && selectionInfo.text) {
      setSelection({
        text: selectionInfo.text,
        rect: selectionInfo.rect || null,
        hasSelection: true,
        context: TextSelectionService.getSelectionWithContext(100)
      });
    } else {
      setSelection({
        text: '',
        rect: null,
        hasSelection: false,
        context: null
      });
    }
  }, []);

  useEffect(() => {
    // Add event listener for selection changes
    const removeListener = TextSelectionService.addSelectionListener(() => {
      updateSelection();
    });

    // Also update on mouseup and keyup events for better UX
    const handleSelectionChange = () => {
      // Small delay to ensure selection is complete
      setTimeout(updateSelection, 0);
    };

    document.addEventListener('mouseup', handleSelectionChange);
    document.addEventListener('keyup', handleSelectionChange);

    // Initial update
    updateSelection();

    // Cleanup function
    return () => {
      removeListener();
      document.removeEventListener('mouseup', handleSelectionChange);
      document.removeEventListener('keyup', handleSelectionChange);
    };
  }, [updateSelection]);

  const clearSelection = useCallback(() => {
    window.getSelection?.().removeAllRanges();
    setSelection({
      text: '',
      rect: null,
      hasSelection: false,
      context: null
    });
  }, []);

  const getSelectedText = useCallback(() => {
    return selection.text;
  }, [selection.text]);

  return {
    selection: selection.text,
    selectionRect: selection.rect,
    hasSelection: selection.hasSelection,
    selectionContext: selection.context,
    getSelectedText,
    clearSelection,
    updateSelection
  };
};

export default useTextSelection;