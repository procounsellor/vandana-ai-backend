"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/lib/store";

export default function LoginModal() {
  const { showLoginModal, setShowLoginModal } = useStore();

  function handleGoogleClick() {
    window.google?.accounts.id.prompt();
  }

  return (
    <AnimatePresence>
      {showLoginModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center"
          style={{ background: "rgba(0,0,0,0.8)" }}
          onClick={() => setShowLoginModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: "spring", damping: 20 }}
            onClick={(e) => e.stopPropagation()}
            className="flex flex-col items-center gap-5 rounded-3xl p-10 max-w-sm w-[90%] text-center"
            style={{ background: "#1a0f00", border: "1px solid #8b6914" }}
          >
            <div className="text-5xl" style={{ textShadow: "0 0 30px #f0c06088" }}>ॐ</div>
            <div>
              <h2 className="text-xl font-semibold mb-2" style={{ fontFamily: "var(--font-cinzel)", color: "#f0c060" }}>
                Continue your journey
              </h2>
              <p className="text-sm leading-relaxed" style={{ color: "#c8a96e" }}>
                You&apos;ve used your 3 free conversations.<br />Sign in to continue receiving Vandana&apos;s guidance.
              </p>
            </div>
            <button
              onClick={handleGoogleClick}
              className="flex items-center gap-3 bg-white text-gray-700 font-medium text-sm px-6 py-3 rounded-xl hover:shadow-lg transition-shadow"
            >
              <img src="https://www.google.com/favicon.ico" alt="" className="w-5 h-5" />
              Sign in with Google
            </button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
