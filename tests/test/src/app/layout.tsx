import type { Metadata } from "next";
import "./globals.css";
import { Inter } from "next/font/google";
import { cn } from "@/lib/utils";
import React from "react";
import { ThemeProvider } from '@/contexts/ThemeContext';

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AutoFlow - AI-Powered Workflow Automation",
  description: "Create sophisticated n8n workflows through natural conversation. Enterprise-grade automation made simple.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const theme = localStorage.getItem('theme') || 
                    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
                  
                  const isDark = theme === 'dark';
                  const root = document.documentElement;
                  const body = document.body;
                  
                  if (isDark) {
                    root.classList.add('dark');
                    root.style.backgroundColor = '#0F172A';
                    body.style.backgroundColor = '#0F172A';
                  } else {
                    root.classList.remove('dark');
                    root.style.backgroundColor = '#F8FAFC';
                    body.style.backgroundColor = '#F8FAFC';
                  }
                } catch (e) {
                  console.warn('Theme initialization failed:', e);
                }
              })();
            `,
          }}
        />
      </head>
      <body className={cn(inter.className, "antialiased")} suppressHydrationWarning>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}


