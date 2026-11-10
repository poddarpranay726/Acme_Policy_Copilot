
import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  // Chat state
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState([]);

  // History state
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  // Authentication state
  const [token, setToken] = useState(
    () => sessionStorage.getItem("access_token")
  );

  const [authMode, setAuthMode] = useState("login");
  const [authName, setAuthName] = useState("");
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [currentUser, setCurrentUser] = useState(
    () => sessionStorage.getItem("user_name") || ""
  );
  const [authLoading, setAuthLoading] = useState(false);

  // Authenticated API helper
  async function authenticatedFetch(url, options = {}) {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    });

    // Handle expired or invalid tokens
    if (response.status === 401) {
      logout();
    }

    return response;
  }

  // Login / Register
  async function handleAuth(event) {
    event.preventDefault();

    if (authLoading) return;

    setAuthLoading(true);

    const isRegister = authMode === "register";

    const endpoint = isRegister
      ? "/auth/register"
      : "/auth/login";

    const body = isRegister
      ? {
          name: authName.trim(),
          email: authEmail.trim(),
          password: authPassword,
        }
      : {
          email: authEmail.trim(),
          password: authPassword,
        };

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed");
      }

      sessionStorage.setItem("access_token", data.access_token);
      sessionStorage.setItem("user_name", data.name);

      setToken(data.access_token);
      setCurrentUser(data.name);

      setAuthPassword("");
      setAuthName("");
      setAuthEmail("");

      setConversationId(null);
      setMessages([]);
      setConversations([]);
      setSources([]);
      setHistoryError("");

    } catch (error) {
      alert(
        typeof error.message === "string"
          ? error.message
          : "Authentication failed"
      );
    } finally {
      setAuthLoading(false);
    }
  }

  // Logout
  function logout() {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("user_name");

    setToken(null);
    setCurrentUser("");

    setConversationId(null);
    setMessages([]);
    setConversations([]);
    setSources([]);

    setInput("");
    setHistoryError("");
    setHistoryLoading(false);
  }

  // Load conversations
  async function loadConversations() {
    if (!token) return;

    try {
      const response = await authenticatedFetch(
        `${API_URL}/conversations`
      );

      if (!response.ok) {
        throw new Error("Could not load conversations");
      }

      const data = await response.json();
      setConversations(data);

    } catch (error) {
      console.error("Conversation loading error:", error);
    }
  }

  // Load conversations after login / token restoration
  useEffect(() => {
    if (token) {
      loadConversations();
    }
  }, [token]);

  // Create new conversation
  async function createConversation() {
    try {
      const response = await authenticatedFetch(
        `${API_URL}/conversations`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error("Could not create conversation");
      }

      const data = await response.json();

      setConversationId(data.conversation_id);
      setMessages([]);
      setSources([]);
      setHistoryError("");
      setHistoryLoading(false);

      await loadConversations();

    } catch (error) {
      console.error(error);
      alert("Could not create conversation. Please try again.");
    }
  }

  // Select existing conversation
  async function selectConversation(selectedConversationId) {
    setConversationId(selectedConversationId);
    setMessages([]);
    setSources([]);
    setHistoryError("");
    setHistoryLoading(true);

    try {
      const response = await authenticatedFetch(
        `${API_URL}/conversations/${selectedConversationId}/messages`
      );

      if (!response.ok) {
        throw new Error("Could not load conversation history");
      }

      const history = await response.json();

      const formattedMessages = history.map((message) => ({
        role: message.role,
        content: message.content,
        sources: [],
      }));

      setMessages(formattedMessages);

    } catch (error) {
      console.error("History loading error:", error);
      setHistoryError(
        "Unable to load conversation. Please try again."
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  // Send message with SSE streaming
  async function sendMessage(event) {
    event.preventDefault();

    const query = input.trim();

    if (!query || loading || historyLoading || !token) return;

    let activeConversationId = conversationId;

    // Automatically create conversation if none selected
    if (!activeConversationId) {
      try {
        const response = await authenticatedFetch(
          `${API_URL}/conversations`,
          {
            method: "POST",
          }
        );

        if (!response.ok) {
          throw new Error("Conversation creation failed");
        }

        const data = await response.json();

        activeConversationId = data.conversation_id;
        setConversationId(activeConversationId);

        await loadConversations();

      } catch (error) {
        console.error(error);
        alert("Could not create conversation.");
        return;
      }
    }

    setInput("");
    setLoading(true);
    setSources([]);

    setMessages((previous) => [
      ...previous,
      { role: "user", content: query },
      { role: "assistant", content: "" },
    ]);

    try {
      const response = await authenticatedFetch(
        `${API_URL}/chat/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query,
            conversation_id: activeConversationId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("Streaming response is not supported.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Normalize line endings for SSE parsing
        buffer = buffer.replace(/\r\n/g, "\n");

        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() || "";

        for (const block of blocks) {
          const lines = block.split("\n");

          let eventType = "";
          let eventData = "";

          for (const line of lines) {
            if (line.startsWith("event:")) {
              eventType = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              eventData += line.slice(5).trim();
            }
          }

          if (!eventType || !eventData) continue;

          const data = JSON.parse(eventData);

          if (eventType === "sources") {
            setSources(data);
          }

          if (eventType === "token") {
            setMessages((previous) => {
              const updated = [...previous];
              const lastMessage = updated[updated.length - 1];

              if (lastMessage?.role === "assistant") {
                updated[updated.length - 1] = {
                  ...lastMessage,
                  content: lastMessage.content + data,
                };
              }

              return updated;
            });
          }

          if (eventType === "error") {
            throw new Error(data);
          }

          if (eventType === "done") {
            console.log("Response generation completed");
          }
        }
      }

      await loadConversations();

    } catch (error) {
      console.error("Chat error:", error);

      setMessages((previous) => {
        const updated = [...previous];
        const lastMessage = updated[updated.length - 1];

        if (lastMessage?.role === "assistant") {
          updated[updated.length - 1] = {
            ...lastMessage,
            content:
              lastMessage.content ||
              "Sorry, something went wrong. Please try again.",
          };
        }

        return updated;
      });

    } finally {
      setLoading(false);
    }
  }

  // Login / Registration screen
  if (!token) {
    return (
      <div className="auth-container">
        <form className="auth-card" onSubmit={handleAuth}>
          <h1>Acme Policy Copilot</h1>
          <p>Your enterprise knowledge assistant</p>

          {authMode === "register" && (
            <input
              type="text"
              placeholder="Full name"
              value={authName}
              onChange={(e) => setAuthName(e.target.value)}
              maxLength={100}
              required
            />
          )}

          <input
            type="email"
            placeholder="Email address"
            value={authEmail}
            onChange={(e) => setAuthEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={authPassword}
            onChange={(e) => setAuthPassword(e.target.value)}
            minLength={8}
            maxLength={128}
            required
          />

          <button type="submit" disabled={authLoading}>
            {authLoading
              ? "Please wait..."
              : authMode === "register"
                ? "Register"
                : "Login"}
          </button>

          <p>
            {authMode === "login"
              ? "Don't have an account?"
              : "Already have an account?"}

            <button
              type="button"
              onClick={() =>
                setAuthMode(
                  authMode === "login" ? "register" : "login"
                )
              }
            >
              {authMode === "login" ? "Register" : "Login"}
            </button>
          </p>
        </form>
      </div>
    );
  }

  // Main chat UI
  return (
    <div className="app-container">

      <Sidebar
        conversations={conversations}
        activeId={conversationId}
        onNewChat={createConversation}
        onSelect={selectConversation}
        userName={currentUser}
      />

      <main className="chat-container">
        <header className="chat-header">
          <div>
            <h2>Acme Policy Copilot</h2>
            <p>Your enterprise knowledge assistant</p>
          </div>

          <div className="user-actions">
            <span>{currentUser}</span>
            <button onClick={logout}>Logout</button>
          </div>
        </header>

        <section className="messages-container">
          {historyLoading ? (
            <div className="welcome-screen">
              <h2>Loading conversation...</h2>
              <p>Please wait while we retrieve your messages.</p>
            </div>
          ) : historyError ? (
            <div className="welcome-screen">
              <h2>Something went wrong</h2>
              <p>{historyError}</p>

              <button
                onClick={() => selectConversation(conversationId)}
              >
                Try again
              </button>
            </div>
          ) : messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-icon">✦</div>
              <h1>How can I help you today?</h1>
              <p>
                Ask questions about company policies, benefits,
                procedures and documentation.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                isLoading={
                  loading &&
                  message.role === "assistant" &&
                  index === messages.length - 1 &&
                  !message.content
                }
              />
            ))
          )}
        </section>

        {sources.length > 0 && (
          <div className="sources-panel">
            <strong>Sources used</strong>

            {sources.map((source, index) => (
              <div
                className="source-item"
                key={source.chunk_id || index}
              >
                📄 {source.source} — Page {source.page}
              </div>
            ))}
          </div>
        )}

        <form className="chat-input-area" onSubmit={sendMessage}>
          <div className="input-wrapper">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask anything about company policies..."
              disabled={loading || historyLoading}
            />

            <button
              type="submit"
              disabled={
                loading || historyLoading || !input.trim()
              }
            >
              {loading ? "..." : "↑"}
            </button>
          </div>

          <p>AI-generated responses may require verification.</p>
        </form>
      </main>
    </div>
  );
}

export default App;
