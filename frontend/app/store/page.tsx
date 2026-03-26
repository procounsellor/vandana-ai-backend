"use client";
import { motion } from "framer-motion";
import Link from "next/link";

export default function StorePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-6"
      style={{ background: "var(--bg-deep)" }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-lg"
      >
        <div className="text-6xl mb-6" style={{ color: "#f0c060" }}>🕉️</div>
        <h1 className="text-3xl mb-4 tracking-widest" style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
          Sacred Store
        </h1>
        <p className="text-base leading-relaxed mb-8" style={{ fontFamily: "var(--font-cormorant)", color: "#c8a96e", fontSize: "1.1rem" }}>
          Curated spiritual artifacts, sacred texts, and devotional items — coming soon.
        </p>
        <Link href="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm tracking-widest transition-all duration-300"
          style={{ border: "1px solid #8b6914", color: "#f0c060", background: "transparent" }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#8b6914"; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}
        >
          ← Return Home
        </Link>
      </motion.div>
    </div>
  );
}
