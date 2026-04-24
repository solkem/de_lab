import "./globals.css";
import type { Metadata } from "next";


export const metadata: Metadata = {
  title: "LakeForge",
  description: "Databricks-like Data Engineering practice platform",
};


export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

