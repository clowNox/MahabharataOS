// Task Types
export interface Task {
  id: string;
  project_id: string;
  title: string;
  original_prompt: string;
  context: Record<string, any>;
  status?: 'pending' | 'approved' | 'rejected' | 'in_progress' | 'pending_review';
  created_at?: string;
  updated_at?: string;
}

export interface Run {
  id: string;
  task_id: string;
  status: string;
  outputs: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface DelegationNode {
  id: string;
  department: string;
  objective: string;
  status: string;
  output?: Record<string, any>;
  depends_on: string[];
}

export interface Campaign {
  id: string;
  title: string;
  description: string;
  duration_days: number;
  plan: DailyPlan[];
  created_at: string;
  status: string;
}

export interface DailyPlan {
  day: number;
  theme: string;
  task_title: string;
  task_description: string;
}

// API Response Types
export interface ApiResponse<T> {
  status: string;
  data?: T;
  error?: string;
}

export interface ExecutionStreamMessage {
  type: 'step' | 'output' | 'error' | 'complete';
  step?: string;
  content?: string;
  data?: Record<string, any>;
}
