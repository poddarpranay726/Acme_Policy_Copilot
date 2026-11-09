
function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelect,
  userName,
}) {
  const displayName = userName || "User";

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">✦</div>
        <div>
          <h2>ACME</h2>
          <span>POLICY COPILOT</span>
        </div>
      </div>

      <button className="new-chat-button" onClick={onNewChat}>
        + New conversation
      </button>

      <div className="sidebar-section-title">
        RECENT CONVERSATIONS
      </div>

      <div className="conversation-list">
        {conversations.map((conversation) => (
          <button
            key={conversation.conversation_id}
            className={`conversation-item ${
              activeId === conversation.conversation_id ? "active" : ""
            }`}
            onClick={() => onSelect(conversation.conversation_id)}
            title={conversation.title || "New conversation"}
          >
            <span>◷</span>
            <span className="conversation-title">
              {conversation.title || "New conversation"}
            </span>
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="avatar">
          {displayName.charAt(0).toUpperCase()}
        </div>

        <div>
          <strong>{displayName}</strong>
          <span>Acme Employee</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
