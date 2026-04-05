"use client";
import { motion } from "framer-motion";

interface Props {
  onSelect: (mode: "talk" | "chat") => void;
  onBack: () => void;
}

export default function ModeSelector({ onSelect, onBack }: Props) {
  return (
    <div className="flex flex-col items-center justify-center flex-1 px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-lg"
      >
        <h2 className="text-center text-2xl mb-1 tracking-widest"
          style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
          How do you wish to connect?
        </h2>
        <p className="text-center text-xs mb-8 tracking-wider" style={{ color: "#8b6914" }}>
          Choose your experience
        </p>

        <div className="grid grid-cols-2 gap-5">
          {/* Talk */}
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onSelect("talk")}
            className="flex flex-col items-center justify-center gap-4 p-8 rounded-2xl text-center"
            style={{ background: "#1a0e00", border: "1px solid #8b6914" }}
          >
            <span className="text-5xl">🎙️</span>
            <div>
              <p className="text-base tracking-widest mb-1" style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
                Talk
              </p>
              <p className="text-xs leading-relaxed" style={{ color: "#8b6914" }}>
                Speak face to face. A full-screen conversation, voice only.
              </p>
            </div>
          </motion.button>

          {/* Chat */}
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onSelect("chat")}
            className="flex flex-col items-center justify-center gap-4 p-8 rounded-2xl text-center"
            style={{ background: "#1a0e00", border: "1px solid #3d2400" }}
          >
            <span className="text-5xl">💬</span>
            <div>
              <p className="text-base tracking-widest mb-1" style={{ fontFamily: "var(--font-cinzel)", color: "#c8a96e" }}>
                Chat
              </p>
              <p className="text-xs leading-relaxed" style={{ color: "#8b6914" }}>
                Type your questions. Read the responses at your own pace.
              </p>
            </div>
          </motion.button>
        </div>

        <button
          onClick={onBack}
          className="mt-8 mx-auto flex items-center gap-2 text-xs tracking-wider transition-colors"
          style={{ color: "#6b4f20" }}
          onMouseEnter={(e) => (e.currentTarget.style.color = "#8b6914")}
          onMouseLeave={(e) => (e.currentTarget.style.color = "#6b4f20")}
        >
          ← Back to scripture selection
        </button>
      </motion.div>
    </div>
  );
}
