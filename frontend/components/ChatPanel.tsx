"use client";

import { useState, useEffect, useRef } from 'react';

interface ChatMessage {
    id: string;
    sender: 'user' | 'agent';
    text: string;
}

interface ChatPanelProps {
    sessionId: string | null;
    onSessionCreated: (sessionId: string) => void;
}

export default function ChatPanel({ sessionId, onSessionCreated }: ChatPanelProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const wsRef = useRef<WebSocket | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        if (!sessionId) return;

        const ws = new WebSocket(`ws://localhost:8000/api/v1/sessions/${sessionId}/ws`);
        wsRef.current = ws;

        ws.onopen = () => console.log('Chat WS connected');
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'chat') {
                    setMessages((prev) => [...prev, {
                        id: Date.now().toString() + Math.random(),
                        sender: data.sender || 'agent',
                        text: data.message
                    }]);
                }
            } catch (e) {
                // Ignore non-JSON or other messages like images (handled by BrowserView)
            }
        };

        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [sessionId]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userText = input.trim();
        setInput('');

        setMessages((prev) => [...prev, {
            id: Date.now().toString(),
            sender: 'user',
            text: userText
        }]);

        if (!sessionId) {
            setLoading(true);
            try {
                const res = await fetch('http://localhost:8000/api/v1/sessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task: userText }),
                });
                if (!res.ok) throw new Error('Failed to start session');
                const data = await res.json();
                onSessionCreated(data.session_id);
            } catch (err: any) {
                console.error(err);
                alert(err.message);
            } finally {
                setLoading(false);
            }
        } else {
            // Send via WS
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                wsRef.current.send(userText);
            }
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-900 border-r border-gray-700">
            <div className="p-4 border-b border-gray-700 font-bold text-lg bg-gray-800 text-white shadow-sm z-10">
                Agentic RPA Chat
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-gray-500 text-center mt-10">
                        Ask the agent to perform a browser task...
                    </div>
                )}
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[90%] p-3 shadow-md ${msg.sender === 'user' ? 'bg-blue-600 text-white rounded-2xl rounded-br-sm' : 'bg-gray-700 text-gray-100 rounded-2xl rounded-bl-sm whitespace-pre-wrap'}`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-700 text-gray-400 p-3 rounded-2xl rounded-bl-sm">
                            <span className="animate-pulse">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-gray-700 bg-gray-800">
                <div className="flex gap-2 relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type an instruction (e.g. 'Go to google.com')"
                        className="flex-1 p-3 bg-gray-950 border border-gray-600 rounded-lg text-white outline-none focus:border-blue-500 transition-colors shadow-inner"
                        disabled={loading && !sessionId} // Disabled only before session creation
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading && !sessionId}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-bold text-white transition-colors shadow-md disabled:opacity-50"
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
