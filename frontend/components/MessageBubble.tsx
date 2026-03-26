"use client";
import { motion } from "framer-motion";

interface Props {
  role: "user" | "assistant";
  content: string;
  isTyping?: boolean;
}

export default function MessageBubble({ role, content, isTyping }: Props) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex flex-col gap-1 max-w-[85%] ${isUser ? "self-end items-end" : "self-start items-start"}`}
    >
      <span className="text-[0.65rem] tracking-widest uppercase"
        style={{ color: "var(--text-muted)" }}>
        {isUser ? "You" : "Vandana"}
      </span>
      <div
        className="px-4 py-3 rounded-2xl text-[0.9rem] leading-relaxed whitespace-pre-wrap"
        style={{
          background: isUser ? "#3d2400" : "#1e1200",
          border: `1px solid ${isUser ? "#8b6914" : "#3d2400"}`,
          borderBottomRightRadius: isUser ? "4px" : undefined,
          borderBottomLeftRadius: !isUser ? "4px" : undefined,
          color: "var(--text-primary)",
        }}
      >
        {isTyping ? (
          <span className="flex gap-1 items-center h-5">
            {[0, 1, 2].map((i) => (
              <motion.span
                key={i}
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: "#8b6914" }}
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </span>
        ) : content}
      </div>
    </motion.div>
  );
}
