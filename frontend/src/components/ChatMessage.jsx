
function ChatMessage({ message, isLoading }) {
  const isUser = message.role === "user";

  return (
    <div className={`message-row ${isUser ? "user-row" : "assistant-row"}`}>
      {!isUser && <div className="message-avatar">✦</div>}

      <div className={`message-bubble ${isUser ? "user-bubble" : ""}`}>
        {isLoading ? (
          <span className="typing-indicator">Thinking...</span>
        ) : (
          <div className="message-content">{message.content}</div>
        )}
      </div>

      {isUser && <div className="user-avatar">R</div>}
    </div>
  );
}

export default ChatMessage;
