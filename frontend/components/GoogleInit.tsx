"use client";
import Script from "next/script";
import { useStore } from "@/lib/store";
import { googleLogin, fetchConversations } from "@/lib/api";

export default function GoogleInit() {
  const { setAuth, setHistory } = useStore();
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID ?? "";

  function initGoogle() {
    if (!window.google || !clientId) return;
    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: async (res: { credential: string }) => {
        const data = await googleLogin(res.credential);
        setAuth(data.token, data.user);
        fetchConversations(data.token).then(setHistory);
      },
    });
  }

  return (
    <Script
      src="https://accounts.google.com/gsi/client"
      strategy="afterInteractive"
      onLoad={initGoogle}
    />
  );
}
