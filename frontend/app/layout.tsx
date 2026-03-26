import type { Metadata } from "next";
import { Inter, Cinzel, Cormorant_Garamond } from "next/font/google";
import GoogleInit from "@/components/GoogleInit";
import "./globals.css";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"] });
const cinzel = Cinzel({ variable: "--font-cinzel", subsets: ["latin"], weight: ["400", "600", "700"] });
const cormorant = Cormorant_Garamond({ variable: "--font-cormorant", subsets: ["latin"], weight: ["300", "400", "500", "600", "700"], style: ["normal", "italic"] });

export const metadata: Metadata = {
  title: "Vandana AI — Ancient Wisdom for Modern Life",
  description: "A spiritual guide rooted in the Bhagavad Gita",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${cinzel.variable} ${cormorant.variable}`}>
      <body className="antialiased">
        {children}
        <GoogleInit />
      </body>
    </html>
  );
}
