'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Inter } from 'next/font/google';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });
const queryClient = new QueryClient();

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-100 flex h-screen overflow-hidden`}>
        <QueryClientProvider client={queryClient}>
          <Sidebar />
          <div className="flex-1 flex flex-col h-screen overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto p-8 bg-black/20">
              {children}
            </main>
          </div>
        </QueryClientProvider>
      </body>
    </html>
  );
}
