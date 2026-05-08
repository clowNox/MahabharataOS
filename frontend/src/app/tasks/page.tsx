'use client';

import Link from 'next/link';
import { TaskList } from '@/components/TaskList';

export default function TasksPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        <Link
          href="/"
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition"
        >
          + New Task
        </Link>
      </div>

      <TaskList />
    </div>
  );
}
