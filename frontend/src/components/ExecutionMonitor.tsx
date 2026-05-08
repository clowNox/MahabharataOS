'use client';

import { useState, useEffect } from 'react';
import { streamTaskExecution } from '@/lib/api';

interface ExecutionMonitorProps {
  taskId: string;
  apiKeys?: {
    openai?: string;
    anthropic?: string;
    tavily?: string;
    gemini?: string;
  };
}

export function ExecutionMonitor({ taskId, apiKeys }: ExecutionMonitorProps) {
  const [logs, setLogs] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startExecution = async () => {
    setIsRunning(true);
    setError(null);
    setLogs([]);

    try {
      for await (const message of streamTaskExecution(taskId, apiKeys)) {
        try {
          const data = JSON.parse(message);
          setLogs((prev) => [...prev, JSON.stringify(data, null, 2)]);
        } catch {
          setLogs((prev) => [...prev, message]);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Execution Monitor</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        onClick={startExecution}
        disabled={isRunning}
        className="mb-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
      >
        {isRunning ? 'Running...' : 'Start Execution'}
      </button>

      <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm h-96 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="text-gray-500">Logs will appear here...</div>
        ) : (
          logs.map((log, i) => (
            <div key={i} className="mb-2">
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
