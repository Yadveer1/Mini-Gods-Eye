// // [SYSTEM_CHECK]: GODS_EYE ROOT LAYOUT
// // [CLASSIFICATION]: COMMAND CENTER SHELL

import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

// // [FONT]: Tactical monospace font
const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

// // [META]: SEO Configuration
export const metadata: Metadata = {
  title: "GODS_EYE // COMMAND CENTER",
  description: "Tactical Surveillance System - Real-time Human Detection",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${jetbrainsMono.variable} font-mono antialiased bg-[#050505] text-white min-h-screen noise`}
      >
        {children}
      </body>
    </html>
  );
}
