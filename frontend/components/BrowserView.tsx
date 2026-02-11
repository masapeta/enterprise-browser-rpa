"use client";

import { useState, useEffect } from 'react';

interface BrowserViewProps {
    sessionId: string | null;
}

export default function BrowserView({ sessionId }: BrowserViewProps) {
    // In a real implementation, this would subscribe toscreenshot updates via WS or poll an endpoint
    // For now, we'll placeholder it or assume the logs contain base64 screenshots
    const [screenshot, setScreenshot] = useState<string | null>(null);

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
                <span className="text-xs text-gray-600">Live Browser View (Simulated)</span>
            </div>
            <div className="flex-1 flex items-center justify-center p-4">
                {screenshot ? (
                    <img src={`data:image/jpeg;base64,${screenshot}`} alt="Browser State" className="max-h-full shadow-lg" />
                ) : (
                    <div className="text-gray-400">Waiting for screenshot update...</div>
                )}
            </div>
        </div>
    );
}
