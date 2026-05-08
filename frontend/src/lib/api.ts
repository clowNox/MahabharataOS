const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  apiKeys?: {
    openai?: string;
    anthropic?: string;
    tavily?: string;
    gemini?: string;
  };
}

function buildHeaders(options: RequestOptions): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (options.apiKeys?.openai) {
    headers['X-OpenAI-Key'] = options.apiKeys.openai;
  }
  if (options.apiKeys?.anthropic) {
    headers['X-Anthropic-Key'] = options.apiKeys.anthropic;
  }
  if (options.apiKeys?.tavily) {
    headers['X-Tavily-Key'] = options.apiKeys.tavily;
  }
  if (options.apiKeys?.gemini) {
    headers['X-Gemini-Key'] = options.apiKeys.gemini;
  }

  return { ...headers, ...options.headers };
}

async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const method = options.method || 'GET';

  const response = await fetch(url, {
    method,
    headers: buildHeaders(options),
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error: ${response.status} - ${errorText}`);
  }

  // Handle empty responses
  const contentType = response.headers.get('content-type');
  if (!contentType || contentType.includes('application/json')) {
    const text = await response.text();
    return text ? JSON.parse(text) : ({} as T);
  }

  return response.json();
}

// Task API
export const taskAPI = {
  createTask: (data: any, apiKeys?: any) =>
    request('/api/tasks', {
      method: 'POST',
      body: data,
      apiKeys,
    }),

  listTasks: (skip = 0, limit = 50) =>
    request(`/api/tasks?skip=${skip}&limit=${limit}`),

  getTask: (taskId: string) =>
    request(`/api/tasks/${taskId}`),

  getTaskCount: () =>
    request('/api/tasks/count'),

  updateTaskStatus: (taskId: string, status: string) =>
    request(`/api/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: { status },
    }),

  executeTask: (taskId: string, apiKeys?: any) =>
    request(`/api/tasks/${taskId}/execute`, {
      method: 'POST',
      apiKeys,
    }),

  getLatestRun: (taskId: string) =>
    request(`/api/tasks/${taskId}/latest_run`),

  getDelegationChain: (taskId: string) =>
    request(`/api/tasks/${taskId}/delegation`),

  updateDelegationChain: (taskId: string, nodes: any[]) =>
    request(`/api/tasks/${taskId}/delegation`, {
      method: 'PATCH',
      body: nodes,
    }),
};

// Campaign API
export const campaignAPI = {
  generatePlan: (data: any, apiKeys?: any) =>
    request('/api/campaigns/generate', {
      method: 'POST',
      body: data,
      apiKeys,
    }),

  getCampaign: (campaignId: string) =>
    request(`/api/campaigns/${campaignId}`),

  executeCampaignDay: (campaignId: string, day: number, apiKeys?: any) =>
    request(`/api/campaigns/${campaignId}/execute/${day}`, {
      method: 'POST',
      apiKeys,
    }),

  executeNextCampaignDay: (campaignId: string, apiKeys?: any) =>
    request(`/api/campaigns/${campaignId}/execute_next`, {
      method: 'POST',
      apiKeys,
    }),

  scheduleCampaign: (campaignId: string) =>
    request(`/api/campaigns/${campaignId}/schedule`, {
      method: 'POST',
    }),
};

// Vault API
export const vaultAPI = {
  saveSecret: (key: string, value: string) =>
    request('/api/vault/save', {
      method: 'POST',
      body: { key, value },
    }),

  getVaultStatus: () =>
    request('/api/vault/status'),
};

// Stream execution
export async function* streamTaskExecution(
  taskId: string,
  apiKeys?: any
): AsyncGenerator<string> {
  const url = `${API_BASE}/api/tasks/${taskId}/execute`;
  const headers = buildHeaders({ apiKeys });

  const response = await fetch(url, {
    method: 'POST',
    headers,
  });

  if (!response.ok) {
    throw new Error(`Stream error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');

    for (let i = 0; i < lines.length - 1; i++) {
      const line = lines[i].trim();
      if (line.startsWith('data: ')) {
        yield line.slice(6);
      }
    }

    buffer = lines[lines.length - 1];
  }

  if (buffer.trim().startsWith('data: ')) {
    yield buffer.trim().slice(6);
  }
}
