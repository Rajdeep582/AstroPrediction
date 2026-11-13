import type { Metadata, Viewport } from "next";
import { Cormorant_Garamond, Inter } from "next/font/google";
import Starfield from "@/components/Starfield";
import { Providers } from "@/components/providers";
import { PERF_BOOT_SCRIPT } from "@/lib/perf";
import "./globals.css";
import "./cinematic.css";
import "./analysis.css";
import "./readable.css";
import "./perf.css";

const serif = Cormorant_Garamond({ subsets: ["latin"], weight: ["400", "500", "600"], style: ["normal", "italic"], variable: "--font-serif", display: "swap" });
const sans = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:4000"),
  title: { default: "Jyotish Studio — Vedic astrology, precisely calculated", template: "%s · Jyotish Studio" },
  description: "Swiss-Ephemeris Vedic birth charts with 16 divisional charts, Vimshottari dasha, yogas, doshas, Shadbala, Ashtakavarga, transits and AI interpretation.",
  keywords: ["kundli", "vedic astrology", "birth chart", "jyotish", "dasha", "navamsa", "panchang", "kundli matching"],
  openGraph: { type: "website", siteName: "Jyotish Studio", title: "Jyotish Studio", description: "Premium Vedic astrology workspace." },
};

export const viewport: Viewport = {
  themeColor: "#07080f",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  viewportFit: "cover",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${serif.variable} ${sans.variable}`} suppressHydrationWarning>
      <head><script dangerouslySetInnerHTML={{ __html: PERF_BOOT_SCRIPT }} /></head>
      <body>
        <Starfield />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
