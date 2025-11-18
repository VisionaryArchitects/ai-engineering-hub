import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Multi-LLM Control Room",
  description: "Orchestrate multiple AI models in collaborative sessions",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
