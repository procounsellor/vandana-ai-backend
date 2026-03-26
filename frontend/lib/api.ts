const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function authHeaders(token?: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── Auth ────────────────────────────────────────────────
export async function googleLogin(idToken: string) {
  const res = await fetch(`${API}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json() as Promise<{ token: string; user: AppUser }>;
}

// ── Conversations ───────────────────────────────────────
export async function fetchConversations(token: string) {
  const res = await fetch(`${API}/conversations`, { headers: authHeaders(token) });
  if (!res.ok) return [];
  return res.json() as Promise<Conversation[]>;
}

export async function fetchConversation(id: string, token: string) {
  const res = await fetch(`${API}/conversations/${id}`, { headers: authHeaders(token) });
  if (!res.ok) throw new Error("Not found");
  return res.json() as Promise<ConversationDetail>;
}

export async function deleteConversation(id: string, token: string) {
  await fetch(`${API}/conversations/${id}`, { method: "DELETE", headers: authHeaders(token) });
}

// ── Voice stream ────────────────────────────────────────
export function voiceStream(
  formData: FormData,
  token: string | null,
  onMeta: (transcript: string, convId: string) => void,
  onAudio: (chunk: string) => void,
  onDone: (message: string) => void,
) {
  return fetch(`${API}/avatar/voice/stream`, {
    method: "POST",
    headers: authHeaders(token),
    body: formData,
  }).then(async (res) => {
    if (!res.ok) throw new Error("Voice stream failed");
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const data = JSON.parse(line.slice(6));
        if (data.type === "meta") onMeta(data.transcript, data.conversation_id);
        else if (data.type === "audio") onAudio(data.chunk);
        else if (data.type === "done") onDone(data.message ?? "");
      }
    }
  });
}

// ── Types ───────────────────────────────────────────────
export interface AppUser {
  id: string;
  name: string;
  email: string;
  picture: string;
}

export interface Conversation {
  id: string;
  title: string;
  language_code: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: ConversationMessage[];
}
