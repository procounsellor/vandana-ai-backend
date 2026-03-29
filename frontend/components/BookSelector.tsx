"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { fetchScriptures, suggestScripture } from "@/lib/api";

const BOOK_META: Record<string, { icon: string; tagline: string }> = {
  gita: { icon: "🕉️", tagline: "Dharma, duty & the path to liberation" },
  yoga_sutras: { icon: "🧘", tagline: "The eight-limbed path of Raja Yoga" },
  chanakya_neeti: { icon: "♟️", tagline: "Practical wisdom on ethics & life" },
  arthashastra: { icon: "⚖️", tagline: "Statecraft, economics & strategy" },
  kama_sutra: { icon: "🌸", tagline: "The art of living & loving well" },
  upanishads: { icon: "🔥", tagline: "Nature of Brahman, Atman & moksha" },
};

interface Scripture {
  short_name: string;
  name: string;
  available: boolean;
}

interface Props {
  onSelect: (shortName: string) => void;
}

export default function BookSelector({ onSelect }: Props) {
  const [scriptures, setScriptures] = useState<Scripture[]>([]);
  const [hovered, setHovered] = useState<string | null>(null);
  const [suggesting, setSuggesting] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    fetchScriptures().then((list) => setScriptures(list as Scripture[]));
  }, []);

  async function handleSuggest() {
    if (!query.trim()) return;
    setSuggesting(true);
    try {
      const result = await suggestScripture(query);
      if (result) onSelect(result.scripture_short_name);
    } finally {
      setSuggesting(false);
    }
  }

  return (
    <div className="flex flex-col items-center justify-center flex-1 px-4 py-8 overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <h2 className="text-center text-2xl mb-1 tracking-widest"
          style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
          Choose Your Scripture
        </h2>
        <p className="text-center text-xs mb-6 tracking-wider" style={{ color: "#8b6914" }}>
          Select a text to receive wisdom from, or describe your question below
        </p>

        {/* Book grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
          {scriptures.map((s, i) => {
            const meta = BOOK_META[s.short_name] ?? { icon: "📖", tagline: "" };
            const isHovered = hovered === s.short_name;
            return (
              <motion.button
                key={s.short_name}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                onHoverStart={() => setHovered(s.short_name)}
                onHoverEnd={() => setHovered(null)}
                onClick={() => s.available && onSelect(s.short_name)}
                disabled={!s.available}
                className="relative flex flex-col items-center text-center p-4 rounded-xl transition-all"
                style={{
                  background: isHovered && s.available ? "#2a1800" : "#1a0e00",
                  border: `1px solid ${isHovered && s.available ? "#f0c060" : "#3d2400"}`,
                  cursor: s.available ? "pointer" : "not-allowed",
                  opacity: s.available ? 1 : 0.45,
                }}
              >
                <span className="text-3xl mb-2">{meta.icon}</span>
                <span className="text-sm font-medium mb-1"
                  style={{ fontFamily: "var(--font-cinzel)", color: isHovered && s.available ? "#f0c060" : "#c8a96e" }}>
                  {s.name}
                </span>
                <span className="text-[0.65rem] leading-snug" style={{ color: "#6b4f20" }}>
                  {meta.tagline}
                </span>
                {!s.available && (
                  <span className="absolute top-2 right-2 text-[0.55rem] tracking-widest uppercase px-1.5 py-0.5 rounded"
                    style={{ background: "#3d2400", color: "#6b4f20" }}>
                    soon
                  </span>
                )}
              </motion.button>
            );
          })}
        </div>

        {/* Suggest by question */}
        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSuggest()}
            placeholder="Or describe what's on your mind…"
            className="flex-1 text-sm px-3 py-2 rounded-lg outline-none"
            style={{
              background: "#1a0e00",
              border: "1px solid #3d2400",
              color: "#c8a96e",
            }}
          />
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleSuggest}
            disabled={suggesting || !query.trim()}
            className="px-4 py-2 rounded-lg text-sm tracking-wider transition-all"
            style={{
              background: suggesting || !query.trim() ? "#2a1800" : "#8b6914",
              color: "#f0c060",
              border: "1px solid #8b6914",
              cursor: suggesting || !query.trim() ? "not-allowed" : "pointer",
            }}
          >
            {suggesting ? "…" : "Suggest"}
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
