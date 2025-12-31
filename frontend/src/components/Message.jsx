import React from 'react';

const Message = ({ text, sender, sources, contextReferences }) => {
  const isUser = sender === 'user';

  return (
    <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
      <div className="message-content">
        <div className="message-text">
          {text}
        </div>
        {(sources && sources.length > 0) || (contextReferences && contextReferences.length > 0) && (
          <div className="message-references">
            {sources && sources.length > 0 && (
              <details className="sources-details">
                <summary>Sources cited:</summary>
                <ul className="sources-list">
                  {sources.map((source, index) => (
                    <li key={index} className="source-item">
                      <strong>{source.source}</strong>
                      {source.section && <span>, Section: {source.section}</span>}
                      {source.page && <span>, Page: {source.page}</span>}
                    </li>
                  ))}
                </ul>
              </details>
            )}
            {contextReferences && contextReferences.length > 0 && (
              <details className="context-details">
                <summary>Related concepts:</summary>
                <ul className="context-list">
                  {contextReferences.map((reference, index) => (
                    <li key={index} className="context-item">
                      <strong>{reference.concept}</strong>
                      {reference.chapter && <span>, Chapter: {reference.chapter}</span>}
                      {reference.similarity_score && (
                        <span> (Relevance: {(reference.similarity_score * 100).toFixed(1)}%)</span>
                      )}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;