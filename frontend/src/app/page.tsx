'use client';

import { useState } from 'react';
import { TaskForm } from '@/components/TaskForm';
import { TaskList } from '@/components/TaskList';

export default function Dashboard() {
  const [refresh, setRefresh] = useState(0);

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <h1 className="text-4xl font-bold mb-2">MahabharataOS</h1>
        <p className="text-lg opacity-90">
          Transform raw thoughts into publish-ready content in minutes
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-blue-600">∞</div>
          <p className="text-gray-600 mt-2">Tasks Created</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-green-600">✓</div>
          <p className="text-gray-600 mt-2">Completed</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-3xl font-bold text-purple-600">→</div>
          <p className="text-gray-600 mt-2">In Progress</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <TaskForm onSuccess={() => setRefresh(refresh + 1)} />
        </div>
        <div className="lg:col-span-2">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Tasks</h2>
          <TaskList key={refresh} />
        </div>
      </div>
    </div>
  );
}
