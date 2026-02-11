"use client";

import { useEffect, useState, useRef } from 'react';

interface LogViewerProps {
    sessionId: string | null;
}

export default function LogViewer({ sessionId }: LogViewerProps) {
    const [logs, setLogs] = useState<string[]>([]);
    const wsRef = useRef<WebSocket | null>(null);
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!sessionId) return;

        const ws = new WebSocket(`ws://localhost:8000/api/v1/sessions/${sessionId}/ws`);
        wsRef.current = ws;

        ws.onmessage = (event) => {
            setLogs((prev) => [...prev, event.data]);
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
        };

        return () => {
            ws.close();
        };
    }, [sessionId]);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    if (!sessionId) {
        return <div className="p-4 text-gray-500">Select or start a session to view logs.</div>;
    }

    return (
        <div className="flex-1 overflow-auto p-4 bg-black font-mono text-sm text-green-400">
            {logs.map((log, i) => (
                <div key={i} className="whitespace-pre-wrap break-all border-b border-gray-900 pb-1 mb-1">
                    {log}
                </div>
            ))}
            <div ref={endRef} />
        </div>
    );
}
