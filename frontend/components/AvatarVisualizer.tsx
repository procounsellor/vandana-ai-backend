"use client";
import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

interface Props {
  isSpeaking: boolean;
  analyserRef: React.MutableRefObject<AnalyserNode | null>;
}

export default function AvatarVisualizer({ isSpeaking, analyserRef }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;

    function drawIdle() {
      ctx.clearRect(0, 0, 260, 260);
      ctx.beginPath();
      ctx.arc(130, 130, 110, 0, Math.PI * 2);
      ctx.strokeStyle = "#3d240066";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    function drawVisualizer() {
      frameRef.current = requestAnimationFrame(drawVisualizer);
      const analyser = analyserRef.current;
      if (!analyser) { drawIdle(); return; }

      const data = new Uint8Array(analyser.frequencyBinCount);
      analyser.getByteFrequencyData(data);
      ctx.clearRect(0, 0, 260, 260);

      const cx = 130, cy = 130, radius = 90, bins = data.length, total = bins * 2, barMaxH = 40;
      for (let i = 0; i < total; i++) {
        const binIdx = i < bins ? i : total - 1 - i;
        const angle = (i / total) * Math.PI * 2 - Math.PI / 2;
        const barH = (data[binIdx] / 255) * barMaxH;
        const alpha = 0.35 + (data[binIdx] / 255) * 0.65;
        ctx.strokeStyle = `rgba(240,192,96,${alpha})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius);
        ctx.lineTo(cx + Math.cos(angle) * (radius + barH), cy + Math.sin(angle) * (radius + barH));
        ctx.stroke();
      }
      ctx.beginPath();
      ctx.arc(cx, cy, radius - 2, 0, Math.PI * 2);
      ctx.strokeStyle = "#8b691422";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    if (isSpeaking) {
      drawVisualizer();
    } else {
      cancelAnimationFrame(frameRef.current);
      drawIdle();
    }

    return () => cancelAnimationFrame(frameRef.current);
  }, [isSpeaking, analyserRef]);

  return (
    <div className="relative w-[260px] h-[260px] flex items-center justify-center">
      <canvas ref={canvasRef} width={260} height={260} className="absolute inset-0" />
      <motion.div
        className="text-[5.5rem] select-none z-10 leading-none"
        style={{ color: "#f0c060", fontFamily: "serif" }}
        animate={isSpeaking ? {
          textShadow: [
            "0 0 20px #f0c06066, 0 0 40px #f0c06033",
            "0 0 50px #f0c060bb, 0 0 90px #f0c06066",
            "0 0 20px #f0c06066, 0 0 40px #f0c06033",
          ],
        } : {
          textShadow: "0 0 20px #f0c06044, 0 0 40px #f0c06022",
        }}
        transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
      >
        ॐ
      </motion.div>
    </div>
  );
}
