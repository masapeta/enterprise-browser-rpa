"use client";

import { useState } from 'react';
import SessionControl from '../components/SessionControl';
import LogViewer from '../components/LogViewer';
import BrowserView from '../components/BrowserView';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    <main className="flex h-screen w-screen bg-gray-950 text-white overflow-hidden">
      {/* Sidebar / Control Panel (30%) */}
      <div className="w-[30%] flex flex-col border-r border-gray-700">
        <div className="p-4 border-b border-gray-700 font-bold text-lg bg-gray-900">
          Agentic RPA Platform
        </div>

        <SessionControl onSessionCreated={setSessionId} />

        <div className="flex-1 flex flex-col min-h-0">
          <div className="p-2 bg-gray-800 text-xs font-semibold uppercase tracking-wider text-gray-400">
            Live Logs
          </div>
          <LogViewer sessionId={sessionId} />
        </div>
      </div>

      {/* Main View / Browser (70%) */}
      <div className="w-[70%] flex flex-col bg-gray-900">
        <BrowserView sessionId={sessionId} />
      </div>
    </main>
  );
}
