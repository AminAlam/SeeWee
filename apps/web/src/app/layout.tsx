import type { ReactNode } from "react";
import { AppShell } from "@/components/AppShell";
import "./globals.css";

export const metadata = {
  title: "SeeWee",
  description: "Local-first CV manager"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body style={{ overflow: "hidden", height: "100vh" }}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
