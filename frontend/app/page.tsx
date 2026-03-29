"use client";
import { motion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";

const SAFFRON = "#f0c060";
const GOLD = "#8b6914";
const DEEP = "#0f0800";
const WARM = "#c8a96e";
const PANEL = "#1a0f00";
const BORDER = "#3d2400";

function Divider() {
  return (
    <div className="flex items-center gap-4 my-2">
      <div className="flex-1 h-px" style={{ background: `linear-gradient(90deg, transparent, ${BORDER})` }} />
      <span style={{ color: GOLD, fontSize: "1rem" }}>✦</span>
      <div className="flex-1 h-px" style={{ background: `linear-gradient(90deg, ${BORDER}, transparent)` }} />
    </div>
  );
}

function NavBar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-4"
      style={{ background: "rgba(15,8,0,0.80)", backdropFilter: "blur(12px)", borderBottom: `1px solid ${BORDER}` }}>
      <span className="text-base tracking-[4px]" style={{ fontFamily: "var(--font-cinzel)", color: SAFFRON }}>
        🪔 VANDANA AI
      </span>
      <div className="hidden md:flex items-center gap-8">
        {[["About", "#about"], ["Features", "#features"], ["How It Works", "#how-it-works"]].map(([label, href]) => (
          <a key={label} href={href}
            className="text-xs tracking-widest transition-colors duration-200"
            style={{ color: GOLD }}
            onMouseEnter={(e) => (e.currentTarget.style.color = SAFFRON)}
            onMouseLeave={(e) => (e.currentTarget.style.color = GOLD)}>
            {label}
          </a>
        ))}
      </div>
      <Link href="/chat"
        className="px-5 py-2 rounded-full text-xs tracking-widest transition-all duration-300"
        style={{ border: `1px solid ${GOLD}`, color: SAFFRON }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = GOLD; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}>
        Begin
      </Link>
    </nav>
  );
}

function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden"
      style={{ background: DEEP }}>

      {/* Full-bleed background */}
      <div className="absolute inset-0">
        <Image src="/home/mainbackground.avif" alt="" fill
          className="object-cover opacity-30" priority sizes="100vw" />
        <div className="absolute inset-0"
          style={{ background: "linear-gradient(180deg, rgba(15,8,0,0.6) 0%, rgba(15,8,0,0.2) 40%, rgba(15,8,0,0.7) 100%)" }} />
      </div>

      {/* Top panoramic banner */}
      <div className="absolute top-0 left-0 right-0 h-28 overflow-hidden">
        <Image src="/home/topherosection.avif" alt="" fill
          className="object-cover object-top opacity-60" sizes="100vw" />
        <div className="absolute inset-0"
          style={{ background: "linear-gradient(180deg, rgba(15,8,0,0.4) 0%, rgba(15,8,0,1) 100%)" }} />
      </div>

      {/* Thin left border strip */}
      <div className="absolute left-0 top-0 bottom-0 w-3 md:w-5 overflow-hidden">
        <Image src="/home/leftborder.avif" alt="" fill className="object-cover" sizes="20px" />
      </div>

      {/* Thin right border strip */}
      <div className="absolute right-0 top-0 bottom-0 w-3 md:w-5 overflow-hidden">
        <Image src="/home/rightborder.avif" alt="" fill className="object-cover" sizes="20px" />
      </div>

      {/* Left tree decoration */}
      <div className="absolute left-4 md:left-8 bottom-0 w-36 md:w-56 h-[70%] pointer-events-none hidden sm:block">
        <Image src="/home/leftbordertree.avif" alt="" fill
          className="object-contain object-bottom opacity-70" sizes="224px" />
      </div>

      {/* Right tree decoration (mirrored) */}
      <div className="absolute right-4 md:right-8 bottom-0 w-36 md:w-56 h-[70%] pointer-events-none hidden sm:block"
        style={{ transform: "scaleX(-1)" }}>
        <Image src="/home/leftbordertree.avif" alt="" fill
          className="object-contain object-bottom opacity-70" sizes="224px" />
      </div>

      {/* Top-left corner widget */}
      <div className="absolute top-16 left-6 md:left-12 w-20 md:w-32 h-20 md:h-32 pointer-events-none">
        <motion.div animate={{ rotate: [0, 3, 0, -3, 0] }} transition={{ duration: 8, repeat: Infinity }}>
          <Image src="/home/herosectiontopleftwidget.avif" alt="" width={128} height={128}
            className="w-full h-full object-contain opacity-80" />
        </motion.div>
      </div>

      {/* Top-right corner widget */}
      <div className="absolute top-16 right-6 md:right-12 w-20 md:w-32 h-20 md:h-32 pointer-events-none">
        <motion.div animate={{ rotate: [0, -3, 0, 3, 0] }} transition={{ duration: 8, repeat: Infinity, delay: 1 }}>
          <Image src="/home/herosectiontoprightwidget.avif" alt="" width={128} height={128}
            className="w-full h-full object-contain opacity-80" />
        </motion.div>
      </div>

      {/* Secondary widgets below first ones */}
      <div className="absolute top-40 left-4 md:left-10 w-16 md:w-24 h-16 md:h-24 pointer-events-none hidden md:block">
        <motion.div animate={{ y: [0, -6, 0] }} transition={{ duration: 5, repeat: Infinity, delay: 0.5 }}>
          <Image src="/home/herosectiontopleftwidget2.avif" alt="" width={96} height={96}
            className="w-full h-full object-contain opacity-60" />
        </motion.div>
      </div>
      <div className="absolute top-40 right-4 md:right-10 w-16 md:w-24 h-16 md:h-24 pointer-events-none hidden md:block">
        <motion.div animate={{ y: [0, -6, 0] }} transition={{ duration: 5, repeat: Infinity, delay: 1.5 }}>
          <Image src="/home/herosectiontoprightwidget2.avif" alt="" width={96} height={96}
            className="w-full h-full object-contain opacity-60" />
        </motion.div>
      </div>

      {/* Moon widget */}
      <div className="absolute top-20 md:top-28 left-1/2 -translate-x-1/2 w-48 md:w-72 h-48 md:h-72 pointer-events-none opacity-25">
        <Image src="/home/moonwidget.avif" alt="" fill className="object-contain" sizes="288px" />
      </div>

      {/* Central Ganesh */}
      <div className="relative z-10 flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className="w-28 md:w-40 mb-4"
        >
          <motion.div
            animate={{ filter: ["drop-shadow(0 0 12px #f0c06044)", "drop-shadow(0 0 28px #f0c06088)", "drop-shadow(0 0 12px #f0c06044)"] }}
            transition={{ duration: 3, repeat: Infinity }}>
            <Image src="/home/ganesh2.avif" alt="Ganesha" width={200} height={300}
              className="w-full h-auto object-contain" />
          </motion.div>
        </motion.div>

        {/* Flanking Ganeshas on desktop */}
        <div className="absolute -left-24 md:-left-36 bottom-0 w-16 md:w-24 pointer-events-none hidden md:block opacity-50">
          <Image src="/home/ganesh2reversedlateral.avif" alt="" width={96} height={144}
            className="w-full h-auto object-contain" />
        </div>
        <div className="absolute -right-24 md:-right-36 bottom-0 w-16 md:w-24 pointer-events-none hidden md:block opacity-50"
          style={{ transform: "scaleX(-1)" }}>
          <Image src="/home/ganesh2reversedlateral.avif" alt="" width={96} height={144}
            className="w-full h-auto object-contain" />
        </div>
      </div>

      {/* Hero text */}
      <div className="relative z-10 text-center px-6 max-w-2xl">
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-xs tracking-[6px] mb-3 uppercase"
          style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>
          Ancient Wisdom · Modern Life
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.9 }}
          className="text-4xl md:text-6xl mb-5 leading-tight"
          style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
          Seek guidance from<br />
          <span style={{ color: SAFFRON, fontStyle: "italic" }}>ancient Indian wisdom</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-base leading-relaxed mb-10"
          style={{ color: WARM, fontFamily: "var(--font-cormorant)", fontSize: "1.15rem" }}>
          Vandana is your personal spiritual companion — voice-driven, multilingual,<br className="hidden md:block" />
          and rooted in the timeless wisdom of the Bhagavad Gita, Yoga Sutras, Upanishads, and more.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1 }}
          className="flex flex-col sm:flex-row gap-4 items-center justify-center">
          <Link href="/chat"
            className="px-8 py-4 rounded-full text-sm tracking-[3px] uppercase font-medium transition-all duration-300"
            style={{ background: SAFFRON, color: DEEP, fontFamily: "var(--font-cinzel)" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#f5d070"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = SAFFRON; }}>
            Talk to Vandana
          </Link>
          <Link href="/store"
            className="px-8 py-4 rounded-full text-sm tracking-[3px] uppercase transition-all duration-300"
            style={{ border: `1px solid ${GOLD}`, color: SAFFRON, fontFamily: "var(--font-cinzel)" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(139,105,20,0.2)"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}>
            Sacred Store
          </Link>
        </motion.div>
      </div>

      {/* Scroll hint */}
      <motion.div
        className="absolute bottom-8 flex flex-col items-center gap-2 z-10"
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 2, repeat: Infinity }}>
        <span className="text-[0.6rem] tracking-[4px]" style={{ color: GOLD }}>SCROLL</span>
        <div className="w-px h-8" style={{ background: `linear-gradient(${GOLD}, transparent)` }} />
      </motion.div>
    </section>
  );
}

function About() {
  return (
    <section id="about" className="relative py-28 px-6 overflow-hidden" style={{ background: PANEL }}>
      {/* Background texture */}
      <div className="absolute inset-0 opacity-10">
        <Image src="/home/background2.avif" alt="" fill className="object-cover" sizes="100vw" />
      </div>

      <div className="relative max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.9 }}
          className="text-center mb-16">
          <p className="text-xs tracking-[5px] uppercase mb-4" style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>About Vandana</p>
          <h2 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
            Where scripture meets technology
          </h2>
          <Divider />
        </motion.div>

        <div className="grid md:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}>
            <p className="leading-relaxed mb-6" style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1.15rem" }}>
              Vandana — meaning <em style={{ color: SAFFRON }}>prayer</em> or <em style={{ color: SAFFRON }}>reverence</em> — is an AI spiritual guide that channels the wisdom of India's greatest scriptures to help you navigate life's deepest questions.
            </p>
            <p className="leading-relaxed" style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1.15rem" }}>
              Whether you seek dharma from the Bhagavad Gita, clarity from the Upanishads, discipline from the Yoga Sutras, or strategy from Chanakya — Vandana listens in your language and responds with timeless guidance.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="relative">
            {/* Ganesh portrait */}
            <div className="relative h-80 rounded-2xl overflow-hidden"
              style={{ border: `1px solid ${BORDER}` }}>
              <Image src="/home/ganesh.avif" alt="Lord Ganesha" fill
                className="object-contain" sizes="500px"
                style={{ background: "radial-gradient(ellipse at center, #2a1400 0%, #0f0800 100%)" }} />
              <div className="absolute inset-0"
                style={{ background: "linear-gradient(180deg, transparent 60%, rgba(26,15,0,0.8) 100%)" }} />
            </div>

            {/* Stat cards */}
            <div className="grid grid-cols-3 gap-3 mt-4">
              {[
                { num: "6", label: "Scriptures" },
                { num: "1200+", label: "Verses" },
                { num: "∞", label: "Wisdom" },
              ].map(({ num, label }) => (
                <div key={label} className="flex flex-col items-center justify-center py-5 rounded-xl"
                  style={{ background: DEEP, border: `1px solid ${BORDER}` }}>
                  <div className="text-2xl mb-1" style={{ color: SAFFRON, fontFamily: "var(--font-cinzel)" }}>{num}</div>
                  <div className="text-[0.65rem] tracking-widest" style={{ color: GOLD }}>{label}</div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

const SCRIPTURES = [
  { icon: "🕉️", name: "Bhagavad Gita", tagline: "Dharma, duty & liberation", short: "gita" },
  { icon: "🧘", name: "Yoga Sutras", tagline: "The eight-limbed path", short: "yoga_sutras" },
  { icon: "🔥", name: "Upanishads", tagline: "Brahman, Atman & moksha", short: "upanishads" },
  { icon: "♟️", name: "Chanakya Neeti", tagline: "Ethics & practical wisdom", short: "chanakya_neeti" },
  { icon: "⚖️", name: "Arthashastra", tagline: "Statecraft & strategy", short: "arthashastra" },
  { icon: "🌸", name: "Kama Sutra", tagline: "The art of living well", short: "kama_sutra" },
];

function ScriptureShowcase() {
  return (
    <section className="relative py-20 px-6 overflow-hidden" style={{ background: PANEL }}>
      <div className="relative max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12">
          <p className="text-xs tracking-[5px] uppercase mb-4" style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>Scriptures</p>
          <h2 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
            Six paths of ancient wisdom
          </h2>
          <Divider />
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {SCRIPTURES.map((s, i) => (
            <motion.div
              key={s.short}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.07 }}
              className="flex flex-col items-center text-center p-6 rounded-2xl"
              style={{ background: DEEP, border: `1px solid ${BORDER}` }}>
              <span className="text-4xl mb-3">{s.icon}</span>
              <h3 className="text-sm tracking-wider mb-1" style={{ fontFamily: "var(--font-cinzel)", color: SAFFRON }}>{s.name}</h3>
              <p className="text-xs leading-snug" style={{ color: GOLD }}>{s.tagline}</p>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mt-10">
          <Link href="/chat"
            className="inline-flex items-center justify-center px-8 py-3 rounded-full text-xs tracking-widest uppercase transition-all duration-300"
            style={{ background: SAFFRON, color: DEEP, fontFamily: "var(--font-cinzel)" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#f5d070"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = SAFFRON; }}>
            Choose Your Scripture
          </Link>
        </motion.div>
      </div>
    </section>
  );
}

function TwoPaths() {
  return (
    <section className="relative py-28 px-6 overflow-hidden" style={{ background: DEEP }}>
      {/* Subtle background */}
      <div className="absolute inset-0 opacity-8">
        <Image src="/home/background1.avif" alt="" fill className="object-cover opacity-10" sizes="100vw" />
        <div className="absolute inset-0" style={{ background: "rgba(15,8,0,0.85)" }} />
      </div>

      <div className="relative max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16">
          <p className="text-xs tracking-[5px] uppercase mb-4" style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>Choose Your Path</p>
          <h2 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
            Two ways to connect
          </h2>
          <Divider />
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* AI Guide */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="group relative rounded-3xl overflow-hidden flex flex-col"
            style={{ border: `1px solid ${BORDER}`, background: PANEL }}
            whileHover={{ scale: 1.01 }}>
            {/* Card image */}
            <div className="relative h-56 overflow-hidden">
              <Image src="/home/mediumherosection.avif" alt="AI Guide" fill
                className="object-cover opacity-60 group-hover:opacity-80 transition-opacity duration-500 group-hover:scale-105"
                sizes="600px"
                style={{ transition: "transform 0.5s ease" }} />
              <div className="absolute inset-0"
                style={{ background: "linear-gradient(180deg, transparent 30%, rgba(26,15,0,1) 100%)" }} />
              <div className="absolute bottom-4 left-6">
                <span className="text-4xl">🕉️</span>
              </div>
            </div>

            <div className="p-8 flex flex-col flex-1 gap-5">
              <div>
                <h3 className="text-xl mb-3 tracking-widest" style={{ fontFamily: "var(--font-cinzel)", color: SAFFRON }}>
                  AI Spiritual Guide
                </h3>
                <p style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1.05rem", lineHeight: "1.7" }}>
                  Speak or type your deepest questions. Vandana listens with the patience of a sage and responds with guidance from India's greatest scriptures — in your language, in a voice that carries the essence of the divine.
                </p>
              </div>
              <ul className="space-y-2">
                {["Voice & text conversation", "Multilingual (EN, HI)", "6 ancient scriptures", "Temple-resonant voice"].map((f) => (
                  <li key={f} className="flex items-center gap-3 text-sm" style={{ color: WARM }}>
                    <span style={{ color: SAFFRON }}>✦</span> {f}
                  </li>
                ))}
              </ul>
              <Link href="/chat"
                className="mt-auto inline-flex items-center justify-center px-6 py-3 rounded-full text-xs tracking-widest uppercase transition-all duration-300"
                style={{ background: SAFFRON, color: DEEP, fontFamily: "var(--font-cinzel)" }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#f5d070"; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = SAFFRON; }}>
                Begin Conversation
              </Link>
            </div>
          </motion.div>

          {/* Store */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="group relative rounded-3xl overflow-hidden flex flex-col"
            style={{ border: `1px solid ${BORDER}`, background: PANEL }}
            whileHover={{ scale: 1.01 }}>
            {/* Card image */}
            <div className="relative h-56 overflow-hidden">
              <Image src="/home/background2.avif" alt="Sacred Store" fill
                className="object-cover opacity-60 group-hover:opacity-80 transition-opacity duration-500"
                sizes="600px" />
              <div className="absolute inset-0"
                style={{ background: "linear-gradient(180deg, transparent 30%, rgba(26,15,0,1) 100%)" }} />
              <div className="absolute bottom-4 left-6">
                <span className="text-4xl">🪔</span>
              </div>
            </div>

            <div className="p-8 flex flex-col flex-1 gap-5">
              <div>
                <h3 className="text-xl mb-3 tracking-widest" style={{ fontFamily: "var(--font-cinzel)", color: SAFFRON }}>
                  Sacred Store
                </h3>
                <p style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1.05rem", lineHeight: "1.7" }}>
                  Discover curated spiritual artifacts, sacred texts, and devotional items handpicked to deepen your practice. Each piece is chosen with the intention of bringing you closer to the divine.
                </p>
              </div>
              <ul className="space-y-2">
                {["Sacred idols & artifacts", "Devotional books", "Incense & ritual items", "Handcrafted spiritual gifts"].map((f) => (
                  <li key={f} className="flex items-center gap-3 text-sm" style={{ color: WARM }}>
                    <span style={{ color: SAFFRON }}>✦</span> {f}
                  </li>
                ))}
              </ul>
              <Link href="/store"
                className="mt-auto inline-flex items-center justify-center px-6 py-3 rounded-full text-xs tracking-widest uppercase transition-all duration-300"
                style={{ border: `1px solid ${GOLD}`, color: SAFFRON, fontFamily: "var(--font-cinzel)" }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(139,105,20,0.2)"; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}>
                Explore Store
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

function Features() {
  const features = [
    { icon: "🎙️", title: "Voice-First", desc: "Speak naturally and receive spoken guidance. Vandana's voice carries a temple-like resonance — reverb, warmth, and presence." },
    { icon: "📖", title: "6 Sacred Scriptures", desc: "Choose from the Bhagavad Gita, Yoga Sutras, Upanishads, Chanakya Neeti, Arthashastra, or Kama Sutra — each with its own wisdom and persona." },
    { icon: "🌐", title: "Multilingual", desc: "Converse in English or Hindi. Vandana understands your language and responds in kind." },
    { icon: "💬", title: "Contextual", desc: "Vandana remembers your conversation, building a continuous dialogue rather than isolated responses." },
    { icon: "🔒", title: "Private & Secure", desc: "Sign in with Google to save your conversations. Guest access allows 3 free queries — no account required to begin." },
    { icon: "⚡", title: "Real-Time", desc: "Responses stream progressively — you start hearing wisdom within seconds, not after a long wait." },
  ];

  return (
    <section id="features" className="relative py-28 px-6 overflow-hidden" style={{ background: PANEL }}>
      <div className="absolute inset-0 opacity-10">
        <Image src="/home/background2.avif" alt="" fill className="object-cover" sizes="100vw" />
        <div className="absolute inset-0" style={{ background: "rgba(26,15,0,0.85)" }} />
      </div>

      <div className="relative max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16">
          <p className="text-xs tracking-[5px] uppercase mb-4" style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>Features</p>
          <h2 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
            Crafted with devotion
          </h2>
          <Divider />
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div key={f.title}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="rounded-2xl p-7 flex flex-col gap-4"
              style={{ background: DEEP, border: `1px solid ${BORDER}` }}>
              <div className="text-3xl">{f.icon}</div>
              <h3 className="text-sm tracking-widest" style={{ fontFamily: "var(--font-cinzel)", color: SAFFRON }}>{f.title}</h3>
              <p className="leading-relaxed" style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1rem" }}>{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    { num: "01", title: "Open Vandana", desc: "Visit the AI Guide and speak or type your question — in English or Hindi." },
    { num: "02", title: "Vandana Listens", desc: "Your voice is transcribed and matched against your chosen scripture using semantic vector search." },
    { num: "03", title: "Wisdom Arrives", desc: "A thoughtful response streams back to you — spoken in a temple-resonant voice." },
    { num: "04", title: "Continue the Journey", desc: "Build a lasting conversation. Sign in with Google to save your history and return whenever you need guidance." },
  ];

  return (
    <section id="how-it-works" className="relative py-28 px-6 overflow-hidden" style={{ background: DEEP }}>
      <div className="relative max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16">
          <p className="text-xs tracking-[5px] uppercase mb-4" style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>How It Works</p>
          <h2 className="text-4xl md:text-5xl mb-4" style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
            Your path to guidance
          </h2>
          <Divider />
        </motion.div>

        <div className="relative">
          <div className="absolute left-8 top-0 bottom-0 w-px hidden md:block"
            style={{ background: `linear-gradient(${BORDER}, ${BORDER} 80%, transparent)` }} />

          <div className="space-y-12">
            {steps.map((s, i) => (
              <motion.div key={s.num}
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.12 }}
                className="flex gap-8 items-start">
                <div className="hidden md:flex w-16 h-16 shrink-0 rounded-full items-center justify-center text-sm relative"
                  style={{ background: PANEL, border: `1px solid ${GOLD}`, fontFamily: "var(--font-cinzel)", color: SAFFRON }}>
                  {s.num}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="md:hidden text-xs" style={{ color: GOLD, fontFamily: "var(--font-cinzel)" }}>{s.num}</span>
                    <h3 className="text-xl" style={{ fontFamily: "var(--font-cinzel)", color: SAFFRON }}>{s.title}</h3>
                  </div>
                  <p style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1.05rem", lineHeight: "1.7" }}>{s.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function CallToAction() {
  return (
    <section className="relative py-32 px-6 text-center overflow-hidden" style={{ background: PANEL }}>
      {/* Background */}
      <div className="absolute inset-0">
        <Image src="/home/mainbackground.avif" alt="" fill
          className="object-cover opacity-20" sizes="100vw" />
        <div className="absolute inset-0"
          style={{ background: "radial-gradient(ellipse 80% 60% at 50% 50%, rgba(42,20,0,0.7) 0%, rgba(26,15,0,0.95) 70%)" }} />
      </div>

      {/* Flanking Ganeshas */}
      <div className="absolute bottom-0 left-4 md:left-16 w-28 md:w-44 pointer-events-none hidden sm:block">
        <Image src="/home/ganesh2.avif" alt="" width={176} height={264}
          className="w-full h-auto object-contain opacity-30" />
      </div>
      <div className="absolute bottom-0 right-4 md:right-16 w-28 md:w-44 pointer-events-none hidden sm:block"
        style={{ transform: "scaleX(-1)" }}>
        <Image src="/home/ganesh2.avif" alt="" width={176} height={264}
          className="w-full h-auto object-contain opacity-30" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="relative max-w-2xl mx-auto">
        <motion.div
          animate={{ textShadow: ["0 0 30px #f0c06033", "0 0 60px #f0c06055", "0 0 30px #f0c06033"] }}
          transition={{ duration: 3, repeat: Infinity }}
          className="text-5xl mb-6" style={{ color: SAFFRON }}>ॐ
        </motion.div>
        <h2 className="text-4xl md:text-5xl mb-6"
          style={{ fontFamily: "var(--font-cormorant)", color: "#fff8ee", fontWeight: 300 }}>
          Begin your journey today
        </h2>
        <p className="mb-10 leading-relaxed"
          style={{ fontFamily: "var(--font-cormorant)", color: WARM, fontSize: "1.1rem" }}>
          Three free conversations await you — no sign-in required. Let Vandana light the way.
        </p>
        <Link href="/chat"
          className="inline-flex items-center gap-3 px-10 py-4 rounded-full text-sm tracking-[3px] uppercase font-medium transition-all duration-300"
          style={{ background: SAFFRON, color: DEEP, fontFamily: "var(--font-cinzel)" }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#f5d070"; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = SAFFRON; }}>
          Talk to Vandana ➤
        </Link>
      </motion.div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="relative py-12 px-6 text-center overflow-hidden"
      style={{ background: "#080500", borderTop: `1px solid ${BORDER}` }}>
      <div className="max-w-4xl mx-auto">
        <p className="text-base mb-2" style={{ fontFamily: "var(--font-cinzel)", color: GOLD, letterSpacing: "4px" }}>VANDANA AI</p>
        <p className="text-xs mb-8" style={{ color: "#4a3010" }}>Ancient wisdom for modern life</p>
        <div className="flex justify-center gap-8 mb-8">
          {[["AI Guide", "/chat"], ["Sacred Store", "/store"]].map(([label, href]) => (
            <Link key={label} href={href}
              className="text-xs tracking-widest transition-colors"
              style={{ color: GOLD }}
              onMouseEnter={(e) => (e.currentTarget.style.color = SAFFRON)}
              onMouseLeave={(e) => (e.currentTarget.style.color = GOLD)}>
              {label}
            </Link>
          ))}
        </div>
        <Divider />
        <p className="text-xs mt-6" style={{ color: "#4a3010" }}>
          © {new Date().getFullYear()} Vandana AI · Rooted in ancient Indian wisdom
        </p>
      </div>
    </footer>
  );
}

export default function HomePage() {
  return (
    <div style={{ background: DEEP, color: "#fff8ee" }}>
      <NavBar />
      <Hero />
      <About />
      <ScriptureShowcase />
      <TwoPaths />
      <Features />
      <HowItWorks />
      <CallToAction />
      <Footer />
    </div>
  );
}
