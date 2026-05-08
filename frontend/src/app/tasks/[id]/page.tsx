'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { taskAPI } from '@/lib/api';
import { Task, Run } from '@/types';
import { ExecutionMonitor } from '@/components/ExecutionMonitor';
import { formatDate } from '@/lib/utils';

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [run, setRun] = useState<Run | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openaiKey, setOpenaiKey] = useState('');

  useEffect(() => {
    loadTask();
  }, [taskId]);

  const loadTask = async () => {
    try {
      setLoading(true);
      const [taskData, runData] = await Promise.all([
        taskAPI.getTask(taskId),
        taskAPI.getLatestRun(taskId).catch(() => null),
      ]);
      setTask(taskData);
      setRun(runData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load task');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus: string) => {
    try {
      await taskAPI.updateTaskStatus(taskId, newStatus);
      if (task) {
        setTask({ ...task, status: newStatus as any });
      }
    } catch (err) {
      alert('Failed to update status');
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }

  if (error || !task) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || 'Task not found'}</p>
        <button
          onClick={() => router.push('/tasks')}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          Back to Tasks
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{task.title}</h1>
          <p className="text-gray-600 mt-1">ID: {task.id}</p>
        </div>
        <button
          onClick={() => router.push('/tasks')}
          className="text-gray-600 hover:text-gray-900"
        >
          ← Back
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Task Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Task Details</h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Original Prompt</label>
                <p className="mt-1 text-gray-600 bg-gray-50 rounded p-3">{task.original_prompt}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Status</label>
                <div className="mt-2 flex gap-2">
                  {['pending', 'approved', 'rejected', 'in_progress'].map((status) => (
                    <button
                      key={status}
                      onClick={() => handleStatusUpdate(status)}
                      className={`px-3 py-1 rounded text-sm font-medium transition ${
                        task.status === status
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>
              {task.created_at && (
                <div>
                  <label className="text-sm font-medium text-gray-700">Created</label>
                  <p className="mt-1 text-gray-600">{formatDate(task.created_at)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Execution Results */}
          {run && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Latest Execution</h2>
              <pre className="bg-gray-50 rounded p-4 overflow-x-auto text-sm">
                {JSON.stringify(run.outputs, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* API Keys */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">API Keys</h3>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-gray-700">OpenAI Key</label>
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="space-y-2">
              <button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition">
                Execute Task
              </button>
              <button className="w-full bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-2 px-4 rounded-lg transition">
                View Pipeline
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Execution Monitor */}
      <ExecutionMonitor
        taskId={taskId}
        apiKeys={openaiKey ? { openai: openaiKey } : undefined}
      />
    </div>
  );
}
