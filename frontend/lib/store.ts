import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AppUser, Conversation } from "./api";

const GUEST_LIMIT = 3;

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface Store {
  // Auth
  token: string | null;
  user: AppUser | null;
  guestCount: number;
  setAuth: (token: string, user: AppUser) => void;
  logout: () => void;
  incrementGuest: () => void;
  isLoggedIn: () => boolean;
  isGuestLimitReached: () => boolean;

  // Conversation
  conversationId: string | null;
  messages: Message[];
  language: string;
  history: Conversation[];
  scriptureShortName: string | null;
  setConversationId: (id: string | null) => void;
  addMessage: (msg: Message) => void;
  setMessages: (msgs: Message[]) => void;
  updateLastAssistant: (content: string) => void;
  setLanguage: (lang: string) => void;
  setHistory: (h: Conversation[]) => void;
  setScripture: (s: string) => void;
  newConversation: () => void;

  // UI
  showLoginModal: boolean;
  setShowLoginModal: (v: boolean) => void;
}

export const useStore = create<Store>()(
  persist(
    (set, get) => ({
      // Auth
      token: null,
      user: null,
      guestCount: 0,
      setAuth: (token, user) => set({ token, user, showLoginModal: false }),
      logout: () => set({ token: null, user: null }),
      incrementGuest: () => set((s) => ({ guestCount: s.guestCount + 1 })),
      isLoggedIn: () => !!get().token,
      isGuestLimitReached: () => !get().token && get().guestCount >= GUEST_LIMIT,

      // Conversation
      conversationId: null,
      messages: [],
      language: "en",
      history: [],
      scriptureShortName: null,
      setConversationId: (id) => set({ conversationId: id }),
      addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
      setMessages: (msgs) => set({ messages: msgs }),
      updateLastAssistant: (content) =>
        set((s) => {
          const msgs = [...s.messages];
          for (let i = msgs.length - 1; i >= 0; i--) {
            if (msgs[i].role === "assistant") { msgs[i] = { ...msgs[i], content }; break; }
          }
          return { messages: msgs };
        }),
      setLanguage: (language) => set({ language }),
      setHistory: (history) => set({ history }),
      setScripture: (scriptureShortName) => set({ scriptureShortName }),
      newConversation: () => set({ conversationId: null, messages: [], scriptureShortName: null }),

      // UI
      showLoginModal: false,
      setShowLoginModal: (v) => set({ showLoginModal: v }),
    }),
    {
      name: "vandana-store",
      partialize: (s) => ({ token: s.token, user: s.user, guestCount: s.guestCount, language: s.language, scriptureShortName: s.scriptureShortName }),
    }
  )
);
