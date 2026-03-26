"use client";
import { useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { useStore } from "@/lib/store";
import MessageBubble from "./MessageBubble";

interface Props {
  isTyping: boolean;
  status: string;
  onSendText: (text: string) => void;
}

export default function ChatPanel({ isTyping, status, onSendText }: Props) {
  const { messages } = useStore();
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const val = inputRef.current?.value.trim();
      if (val) { onSendText(val); inputRef.current!.value = ""; }
    }
  }

  function handleSend() {
    const val = inputRef.current?.value.trim();
    if (val) { onSendText(val); inputRef.current!.value = ""; }
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-5 flex flex-col gap-4">
        {messages.length === 0 && !isTyping ? (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="flex-1 flex flex-col items-center justify-center gap-4 text-center py-16"
          >
            <div className="text-5xl" style={{ color: "#8b6914", textShadow: "0 0 30px #f0c06044" }}>ॐ</div>
            <p className="text-sm leading-relaxed max-w-xs" style={{ color: "#6b4f20" }}>
              Share what is weighing on your heart.<br />
              Vandana will offer guidance from the Bhagavad Gita.
            </p>
          </motion.div>
        ) : (
          <>
            {messages.map((m) => <MessageBubble key={m.id} role={m.role} content={m.content} />)}
            {isTyping && <MessageBubble role="assistant" content="" isTyping />}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Status */}
      {status && (
        <div className="px-4 py-1 text-xs text-center" style={{ color: "#6b4f20" }}>{status}</div>
      )}

      {/* Input */}
      <div className="px-4 py-3 flex gap-2 items-end" style={{ borderTop: "1px solid #3d2400" }}>
        <textarea
          ref={inputRef}
          rows={1}
          placeholder="Ask Vandana anything..."
          onKeyDown={handleKeyDown}
          className="flex-1 resize-none rounded-xl px-4 py-3 text-sm outline-none transition-colors"
          style={{
            background: "#2a1800",
            border: "1px solid #3d2400",
            color: "#f5e6c8",
            maxHeight: "120px",
          }}
          onInput={(e) => {
            const t = e.currentTarget;
            t.style.height = "auto";
            t.style.height = Math.min(t.scrollHeight, 120) + "px";
          }}
          onFocus={(e) => e.currentTarget.style.borderColor = "#8b6914"}
          onBlur={(e) => e.currentTarget.style.borderColor = "#3d2400"}
        />
        <button
          onClick={handleSend}
          className="w-10 h-10 rounded-xl flex items-center justify-center text-lg transition-colors"
          style={{ background: "#8b6914", color: "#0f0800" }}
          onMouseEnter={(e) => e.currentTarget.style.background = "#f0c060"}
          onMouseLeave={(e) => e.currentTarget.style.background = "#8b6914"}
        >
          ➤
        </button>
      </div>
    </div>
  );
}
