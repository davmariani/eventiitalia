import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Feste Italia | Eventi e idee per gite",
  description: "Scopri sagre, festival, mercatini e idee per gite in tutta Italia.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="it">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
