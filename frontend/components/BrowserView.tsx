"use client";

import { useState, useEffect } from 'react';

interface BrowserViewProps {
    sessionId: string | null;
}

export default function BrowserView({ sessionId }: BrowserViewProps) {
    // In a real implementation, this would subscribe toscreenshot updates via WS or poll an endpoint
    // For now, we'll placeholder it or assume the logs contain base64 screenshots
    const [screenshot, setScreenshot] = useState<string | null>(null);

    useEffect(() => {
        if (!sessionId) return;

        const ws = new WebSocket(`ws://localhost:8000/api/v1/sessions/${sessionId}/ws`);

        ws.onopen = () => {
            console.log('Connected to session WS');
        };

        ws.onmessage = (event) => {
            try {
                const parsed = JSON.parse(event.data);
                if (parsed.type === 'image') {
                    setScreenshot(parsed.data);
                }
            } catch (e) {
                // Ignore non-JSON or other formats
                const data = event.data;
                if (typeof data === 'string' && data.startsWith('data:image')) {
                    setScreenshot(data);
                }
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            ws.close();
        };
    }, [sessionId]);

    if (!sessionId) {
        return (
            <div className="h-full flex items-center justify-center bg-gray-900 text-gray-500">
                No active browser session
            </div>
        );
    }

    return (
        <div className="h-full bg-gray-100 flex flex-col">
            <div className="bg-gray-200 p-2 border-b border-gray-300 flex justify-between items-center">
                <span className="text-xs text-gray-600">Live Browser View</span>
                {screenshot && <span className="text-xs text-green-600 animate-pulse">● Live</span>}
            </div>
            <div className="flex-1 flex items-center justify-center p-4 bg-gray-900 overflow-hidden relative">
                {screenshot ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={screenshot} alt="Browser State" className="max-h-full max-w-full object-contain shadow-lg" />
                ) : (
                    <div className="text-gray-500 flex flex-col items-center animate-pulse">
                        <svg className="w-10 h-10 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <span>Waiting for stream...</span>
                    </div>
                )}

                {/* Result Overlay removed in favor of chat interface */}
            </div>
        </div>
    );
}
