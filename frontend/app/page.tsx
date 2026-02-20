"use client";

import { useState } from 'react';
import ChatPanel from '../components/ChatPanel';
import BrowserView from '../components/BrowserView';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    <main className="flex h-screen w-screen bg-gray-950 text-white overflow-hidden">
      {/* Sidebar / Chat Panel (30%) */}
      <div className="w-[30%] flex flex-col min-w-[300px] border-r border-gray-700 shadow-xl z-20">
        <ChatPanel sessionId={sessionId} onSessionCreated={setSessionId} />
      </div>

      {/* Main View / Browser (70%) */}
      <div className="w-[70%] flex flex-col bg-gray-900 overflow-hidden relative">
        <BrowserView sessionId={sessionId} />
      </div>
    </main>
  );
}
