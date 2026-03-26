"use client";
import { useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/lib/store";
import { fetchConversations, fetchConversation, deleteConversation } from "@/lib/api";

interface Props {
  open: boolean;
  onClose: () => void;
}

function timeAgo(iso: string) {
  const d = new Date(iso), now = new Date();
  const diff = now.getTime() - d.getTime();
  if (diff < 86400000) return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  if (diff < 604800000) return d.toLocaleDateString([], { weekday: "short" });
  return d.toLocaleDateString([], { month: "short", day: "numeric" });
}

export default function HistorySidebar({ open, onClose }: Props) {
  const { token, isLoggedIn, history, setHistory, setConversationId, setMessages, conversationId, newConversation } = useStore();

  useEffect(() => {
    if (open && isLoggedIn() && token) {
      fetchConversations(token).then(setHistory);
    }
  }, [open, token, isLoggedIn, setHistory]);

  async function handleSelect(id: string) {
    if (!token) return;
    const data = await fetchConversation(id, token);
    setConversationId(data.id);
    setMessages(data.messages.map((m) => ({ id: m.id, role: m.role, content: m.content })));
    onClose();
  }

  async function handleDelete(e: React.MouseEvent, id: string) {
    e.stopPropagation();
    if (!token) return;
    await deleteConversation(id, token);
    if (conversationId === id) newConversation();
    setHistory(history.filter((c) => c.id !== id));
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-40"
            style={{ background: "rgba(0,0,0,0.5)" }}
            onClick={onClose}
          />
          <motion.div
            initial={{ x: "-100%" }} animate={{ x: 0 }} exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed top-0 left-0 h-full w-72 z-50 flex flex-col"
            style={{ background: "#130a00", borderRight: "1px solid #3d2400" }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-4 border-b" style={{ borderColor: "#3d2400" }}>
              <span className="text-sm font-semibold tracking-widest uppercase" style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
                Conversations
              </span>
              <button onClick={onClose} className="text-lg" style={{ color: "#8b6914" }}>✕</button>
            </div>

            {/* New Chat */}
            <button
              onClick={() => { newConversation(); onClose(); }}
              className="mx-3 my-3 flex items-center gap-2 px-4 py-3 rounded-xl text-sm transition-colors"
              style={{ background: "#2a1800", border: "1px solid #8b6914", color: "#f0c060" }}
            >
              <span className="text-base">✦</span> New conversation
            </button>

            {/* List */}
            <div className="flex-1 overflow-y-auto px-2 pb-4">
              {!isLoggedIn() ? (
                <p className="text-center text-xs py-8" style={{ color: "#6b4f20" }}>Sign in to see history</p>
              ) : history.length === 0 ? (
                <p className="text-center text-xs py-8" style={{ color: "#6b4f20" }}>No conversations yet</p>
              ) : history.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => handleSelect(conv.id)}
                  className="group flex items-center justify-between px-3 py-3 rounded-xl cursor-pointer transition-colors"
                  style={{
                    background: conv.id === conversationId ? "#2a1800" : "transparent",
                    marginBottom: "2px",
                  }}
                  onMouseEnter={(e) => { if (conv.id !== conversationId) e.currentTarget.style.background = "#1e1200"; }}
                  onMouseLeave={(e) => { if (conv.id !== conversationId) e.currentTarget.style.background = "transparent"; }}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate" style={{ color: "#f5e6c8" }}>{conv.title}</p>
                    <p className="text-xs mt-0.5" style={{ color: "#6b4f20" }}>{timeAgo(conv.updated_at)}</p>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, conv.id)}
                    className="opacity-0 group-hover:opacity-100 ml-2 text-sm transition-opacity hover:text-red-400"
                    style={{ color: "#6b4f20" }}
                  >
                    🗑
                  </button>
                </div>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
