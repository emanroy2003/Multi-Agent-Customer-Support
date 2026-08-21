import { useEffect, useState } from "react";
import ChatWindow from "../components/ChatWindow.jsx";
import Sidebar from "../components/Sidebar.jsx";
import * as chatApi from "../services/chat.js";

export default function Dashboard() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");

  async function refreshConversations() {
    try {
      const data = await chatApi.listConversations();
      setConversations(data);
    } catch {
      setError("Could not load conversation history.");
    }
  }

  useEffect(() => {
    refreshConversations();
  }, []);

  async function handleSelect(conversationId) {
    setActiveId(conversationId);
    setError("");
    try {
      const detail = await chatApi.getConversation(conversationId);
      setMessages(detail.messages);
    } catch {
      setError("Could not load this conversation.");
    }
  }

  function handleNewConversation() {
    setActiveId(null);
    setMessages([]);
    setError("");
  }

  async function handleDelete(conversationId) {
    try {
      await chatApi.deleteConversation(conversationId);
      if (conversationId === activeId) {
        handleNewConversation();
      }
      refreshConversations();
    } catch {
      setError("Could not delete this conversation.");
    }
  }

  async function handleSendMessage(text) {
    setError("");
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: text,
      agents_used: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      const response = await chatApi.sendMessage(text, activeId);
      const assistantMessage = {
        id: `temp-assistant-${Date.now()}`,
        role: "assistant",
        content: response.reply,
        agents_used: response.agents_used,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setActiveId(response.conversation_id);
      refreshConversations();
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong sending your message.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={handleSelect}
        onNewConversation={handleNewConversation}
        onDelete={handleDelete}
      />
      <ChatWindow
        messages={messages}
        onSendMessage={handleSendMessage}
        isSending={isSending}
        error={error}
      />
    </div>
  );
}
