"use client";
import { useState, useRef, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import { useStore } from "@/lib/store";
import { voiceStream, fetchConversations } from "@/lib/api";
import BookSelector from "@/components/BookSelector";
import ModeSelector from "@/components/ModeSelector";
import ChatPanel from "@/components/ChatPanel";
import HistorySidebar from "@/components/HistorySidebar";
import LoginModal from "@/components/LoginModal";
import Link from "next/link";

export default function ChatPage() {
  const store = useStore();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [status, setStatus] = useState("");
  const [historyOpen, setHistoryOpen] = useState(false);

  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioQueueRef = useRef<string[]>([]);

  const avatarVideo = store.scriptureShortName === "gita"
    ? "/home/krishna-talking.mp4"
    : store.scriptureShortName === "chanakya_neeti" || store.scriptureShortName === "arthashastra" || store.scriptureShortName === "kama_sutra"
    ? "/home/chanakya-talking.mp4"
    : "/home/ganesha-talking.mp4";

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (isSpeaking) {
      video.play().catch(() => {});
    } else {
      video.pause();
      video.currentTime = 0;
    }
  }, [isSpeaking]);
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingChunksRef = useRef<Blob[]>([]);

  // Google is initialized in GoogleInit component (layout.tsx)

  // ── Audio playback ─────────────────────────────────────
  function getAudioCtx() {
    if (!audioCtxRef.current) audioCtxRef.current = new AudioContext();
    if (audioCtxRef.current.state === "suspended") audioCtxRef.current.resume();
    return audioCtxRef.current;
  }

  function playNextChunk() {
    if (audioQueueRef.current.length === 0) {
      setIsSpeaking(false);
      setStatus("");
      if (store.isLoggedIn()) fetchConversations(store.token!).then(store.setHistory);
      currentAudioRef.current = null;
      return;
    }
    const b64 = audioQueueRef.current.shift()!;
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const blob = new Blob([bytes], { type: "audio/wav" });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    const ac = getAudioCtx();
    if (!analyserRef.current) {
      analyserRef.current = ac.createAnalyser();
      analyserRef.current.fftSize = 128;
      analyserRef.current.connect(ac.destination);
    }
    const src = ac.createMediaElementSource(audio);
    src.connect(analyserRef.current);

    currentAudioRef.current = audio;
    setIsSpeaking(true);
    audio.play().catch(console.error);
    audio.onended = () => { URL.revokeObjectURL(url); playNextChunk(); };
  }

  function queueAudio(chunk: string) {
    audioQueueRef.current.push(chunk);
    if (!currentAudioRef.current) playNextChunk();
  }

  // ── Voice recording ────────────────────────────────────
  async function toggleRecording() {
    if (isRecording) {
      const mr = mediaRecorderRef.current;
      if (!mr) return;
      mr.stop();
      mr.stream.getTracks().forEach((t) => t.stop());
      setIsRecording(false);
      mr.onstop = () => processVoice();
    } else {
      if (store.isGuestLimitReached()) { store.setShowLoginModal(true); return; }
      recordingChunksRef.current = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      mr.ondataavailable = (e) => recordingChunksRef.current.push(e.data);
      mr.start();
      mediaRecorderRef.current = mr;
      setIsRecording(true);
      setStatus("Listening...");
    }
  }

  async function processVoice() {
    setStatus("Transcribing...");
    setIsTyping(true);
    const blob = new Blob(recordingChunksRef.current, { type: "audio/webm" });
    console.log("[processVoice] blob size:", blob.size, "type:", blob.type);
    const fd = new FormData();
    fd.append("audio", blob, "voice.webm");
    if (store.conversationId) fd.append("conversation_id", store.conversationId);
    fd.append("language_code", store.language);
    if (store.scriptureShortName) fd.append("scripture_short_name", store.scriptureShortName);
    console.log("[processVoice] sending — conversationId:", store.conversationId, "language:", store.language, "scripture:", store.scriptureShortName);

    const tempId = Date.now().toString();
    try {
      await voiceStream(
        fd, store.token,
        (transcript, convId) => {
          console.log("[processVoice] meta received — transcript:", transcript, "convId:", convId);
          store.addMessage({ id: tempId, role: "user", content: transcript });
          store.addMessage({ id: tempId + "_a", role: "assistant", content: "…" });
          store.setConversationId(convId);
          if (!store.isLoggedIn()) store.incrementGuest();
          setIsTyping(false);
          setStatus("Speaking...");
        },
        (chunk) => queueAudio(chunk),
        (message) => {
          console.log("[processVoice] done — message length:", message.length);
          store.updateLastAssistant(message);
        },
      );
    } catch (e) {
      console.error("[processVoice] error:", e);
      setStatus("Something went wrong");
      setIsTyping(false);
    }
  }

  // ── Text send ──────────────────────────────────────────
  const handleSendText = useCallback(async (text: string) => {
    if (store.isGuestLimitReached()) { store.setShowLoginModal(true); return; }
    const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    store.addMessage({ id: Date.now().toString(), role: "user", content: text });
    store.addMessage({ id: Date.now().toString() + "_a", role: "assistant", content: "…" });
    setIsTyping(true);
    setStatus("Thinking...");
    try {
      const res = await fetch(`${API}/avatar/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(store.token ? { Authorization: `Bearer ${store.token}` } : {}),
        },
        body: JSON.stringify({
          message: text,
          conversation_id: store.conversationId,
          language_code: store.language,
          scripture_short_name: store.scriptureShortName,
        }),
      });
      const data = await res.json();
      store.setConversationId(data.conversation_id);
      store.updateLastAssistant(data.message.content);
      if (!store.isLoggedIn()) store.incrementGuest();
      setIsTyping(false);
      setStatus("Speaking...");
      for (const chunk of (data.audio_chunks ?? [])) queueAudio(chunk);
    } catch (e) {
      console.error(e);
      setIsTyping(false);
      setStatus("Something went wrong");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [store]);

  return (
    <div className="h-screen flex flex-col" style={{ background: "var(--bg-deep)" }}>
      {/* Header */}
      <header className="relative flex items-center justify-center px-4 py-3 shrink-0"
        style={{ background: "linear-gradient(180deg,#1e1200 0%,transparent 100%)", borderBottom: "1px solid #3d2400" }}>
        <div className="absolute left-4 flex items-center gap-3">
          <Link href="/"
            className="text-sm transition-colors"
            style={{ color: "#8b6914" }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "#f0c060")}
            onMouseLeave={(e) => (e.currentTarget.style.color = "#8b6914")}>
            Home
          </Link>
          <button onClick={() => setHistoryOpen(true)}
            className="text-xl transition-colors"
            style={{ color: "#8b6914" }}
            onMouseEnter={(e) => e.currentTarget.style.color = "#f0c060"}
            onMouseLeave={(e) => e.currentTarget.style.color = "#8b6914"}>
            ☰
          </button>
          {store.scriptureShortName && (
            <button
              onClick={() => store.newConversation()}
              className="text-[0.65rem] tracking-wider px-2 py-1 rounded-lg transition-all"
              style={{ background: "#2a1800", border: "1px solid #3d2400", color: "#8b6914" }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = "#8b6914"; e.currentTarget.style.color = "#f0c060"; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = "#3d2400"; e.currentTarget.style.color = "#8b6914"; }}
              title="Change scripture"
            >
              📖 Change
            </button>
          )}
        </div>
        <Link href="/" className="text-center group">
          <h1 className="text-lg tracking-[3px] group-hover:opacity-80 transition-opacity" style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
            🪔 VANDANA AI
          </h1>
          <p className="text-[0.65rem] tracking-wider" style={{ color: "#8b6914" }}>
            Ancient wisdom for modern life
          </p>
        </Link>
        <div className="absolute right-4 flex items-center gap-3">
          {/* Language selector */}
          <select
            value={store.language}
            onChange={(e) => store.setLanguage(e.target.value)}
            className="text-xs px-2 py-1.5 rounded-lg outline-none cursor-pointer"
            style={{ background: "#2a1800", border: "1px solid #8b6914", color: "#f0c060" }}
          >
            <option value="en">🇬🇧 EN</option>
            <option value="hi">🇮🇳 HI</option>
          </select>

          {store.user ? (
            <>
              {store.user.picture && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={store.user.picture} alt="" referrerPolicy="no-referrer"
                  className="w-7 h-7 rounded-full border" style={{ borderColor: "#8b6914" }} />
              )}
              <span className="text-xs hidden sm:block" style={{ color: "#c8a96e" }}>
                {store.user.name?.split(" ")[0]}
              </span>
            </>
          ) : (
            <span className="text-xs hidden sm:block" style={{ color: "#6b4f20" }}>
              {Math.max(0, 3 - store.guestCount)} free left
            </span>
          )}
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">

        {/* Step 1: Pick scripture */}
        {!store.scriptureShortName && (
          <BookSelector onSelect={(s) => store.setScripture(s)} />
        )}

        {/* Step 2: Pick mode */}
        {store.scriptureShortName && !store.mode && (
          <ModeSelector
            onSelect={(m) => store.setMode(m)}
            onBack={() => store.newConversation()}
          />
        )}

        {/* Step 3a: TALK mode — full screen video */}
        {store.scriptureShortName && store.mode === "talk" && (
          <div className="relative flex flex-1 flex-col items-center justify-center overflow-hidden">
            {/* Full-screen video */}
            <div className="relative w-full h-full max-w-2xl mx-auto flex flex-col items-center justify-center gap-6 px-4">
              <div className="relative w-full rounded-3xl overflow-hidden"
                style={{
                  boxShadow: isSpeaking ? "0 0 60px #f0c06066, 0 0 120px #8b691422" : "0 0 20px #3d240044",
                  transition: "box-shadow 0.5s ease",
                  maxHeight: "65vh",
                }}>
                <video
                  ref={videoRef}
                  src={avatarVideo}
                  loop
                  muted
                  playsInline
                  className="w-full object-cover"
                  style={{ opacity: isSpeaking ? 1 : 0.75, transition: "opacity 0.4s ease" }}
                />
                {/* Listening pulse ring */}
                {isRecording && (
                  <div className="absolute inset-0 rounded-3xl animate-pulse"
                    style={{ border: "2px solid #ff4444", boxShadow: "inset 0 0 40px #ff000022" }} />
                )}
              </div>

              {/* Last assistant message as floating subtitle */}
              {store.messages.length > 0 && (() => {
                const last = [...store.messages].reverse().find(m => m.role === "assistant");
                return last && last.content !== "…" ? (
                  <motion.p
                    key={last.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center text-sm leading-relaxed px-4 max-w-lg"
                    style={{ fontFamily: "var(--font-cormorant)", color: "#c8a96e", fontSize: "1.05rem" }}>
                    {last.content}
                  </motion.p>
                ) : null;
              })()}

              {/* Status + mic */}
              <div className="flex flex-col items-center gap-3">
                <p className="text-xs tracking-widest" style={{ color: isSpeaking ? "#f0c060" : "#6b4f20" }}>
                  {status || (isRecording ? "Tap to stop" : "Tap to speak")}
                </p>
                <motion.button
                  onClick={toggleRecording}
                  whileTap={{ scale: 0.92 }}
                  className="w-20 h-20 rounded-full flex items-center justify-center text-3xl"
                  style={{
                    background: isRecording ? "#8b0000" : "#2a1800",
                    border: `3px solid ${isRecording ? "#ff4444" : "#8b6914"}`,
                    color: "#f0c060",
                    boxShadow: isRecording ? "0 0 30px #ff000055" : "0 0 15px #8b691422",
                  }}
                >
                  {isRecording ? "⏹️" : "🎤"}
                </motion.button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3b: CHAT mode — original layout */}
        {store.scriptureShortName && store.mode === "chat" && (
          <>
            {/* Avatar panel — desktop only */}
            <div className="hidden md:flex w-[280px] shrink-0 flex-col items-center justify-center gap-5 p-5"
              style={{ borderRight: "1px solid #3d2400" }}>
              <div className="relative w-full rounded-2xl overflow-hidden"
                style={{ boxShadow: isSpeaking ? "0 0 30px #f0c06044" : "none", transition: "box-shadow 0.4s ease" }}>
                <video
                  ref={videoRef}
                  src={avatarVideo}
                  loop
                  muted
                  playsInline
                  className="w-full object-cover"
                  style={{ opacity: isSpeaking ? 1 : 0.6, transition: "opacity 0.4s ease" }}
                />
              </div>
              <p className="text-xs tracking-widest transition-colors" style={{ color: isSpeaking ? "#f0c060" : "#6b4f20" }}>
                {status || (isRecording ? "Tap to stop" : "Tap to speak")}
              </p>
              <motion.button
                onClick={toggleRecording}
                whileTap={{ scale: 0.92 }}
                className="w-14 h-14 rounded-full flex items-center justify-center text-2xl"
                style={{
                  background: isRecording ? "#8b0000" : "#2a1800",
                  border: `2px solid ${isRecording ? "#ff4444" : "#8b6914"}`,
                  color: "#f0c060",
                  boxShadow: isRecording ? "0 0 20px #ff000044" : "none",
                }}
              >
                {isRecording ? "⏹️" : "🎤"}
              </motion.button>
            </div>

            <ChatPanel isTyping={isTyping} status={status} onSendText={handleSendText} />
          </>
        )}

      </div>

      {/* Mobile mic bar — chat mode only */}
      {store.mode === "chat" && (
        <div className="md:hidden flex items-center justify-center py-3 shrink-0"
          style={{ borderTop: "1px solid #3d2400" }}>
          <motion.button
            onClick={toggleRecording}
            whileTap={{ scale: 0.92 }}
            className="w-12 h-12 rounded-full flex items-center justify-center text-xl"
            style={{
              background: isRecording ? "#8b0000" : "#2a1800",
              border: `2px solid ${isRecording ? "#ff4444" : "#8b6914"}`,
              color: "#f0c060",
            }}
          >
            {isRecording ? "⏹️" : "🎤"}
          </motion.button>
        </div>
      )}

      <HistorySidebar open={historyOpen} onClose={() => setHistoryOpen(false)} />
      <LoginModal />
    </div>
  );
}
