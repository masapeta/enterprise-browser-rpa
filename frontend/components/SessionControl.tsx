"use client";

import { useState } from 'react';

interface SessionControlProps {
    onSessionCreated: (sessionId: string) => void;
}

export default function SessionControl({ onSessionCreated }: SessionControlProps) {
    const [task, setTask] = useState('');
    const [loading, setLoading] = useState(false);

    const startSession = async () => {
        if (!task) return;
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/v1/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ task }),
            });
            const data = await res.json();
            onSessionCreated(data.session_id);
        } catch (err) {
            console.error(err);
            alert('Failed to start session');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-4 border-b border-gray-700 bg-gray-800">
            <h2 className="text-xl font-bold mb-4 text-white">New Session</h2>
            <div className="flex gap-2">
                <input
                    type="text"
                    value={task}
                    onChange={(e) => setTask(e.target.value)}
                    placeholder="Enter task (e.g., 'Go to google.com...')"
                    className="flex-1 p-2 rounded bg-gray-900 border border-gray-600 text-white"
                />
                <button
                    onClick={startSession}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-white font-bold"
                >
                    {loading ? 'Starting...' : 'Run Agent'}
                </button>
            </div>
        </div>
    );
}
