'use client';

import { useState } from 'react';
import { vaultAPI } from '@/lib/api';

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('');
  const [keyType, setKeyType] = useState('openai');
  const [loading, setLoading] = useState(false);
  const [savedKeys, setSavedKeys] = useState<string[]>([]);
  const [message, setMessage] = useState<{ type: string; text: string } | null>(null);

  const handleSaveKey = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await vaultAPI.saveSecret(keyType, apiKey);
      setSavedKeys([...new Set([...savedKeys, keyType])]);
      setApiKey('');
      setMessage({ type: 'success', text: 'API key saved securely!' });
    } catch (err) {
      setMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Failed to save key',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Keys Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">API Keys</h2>
          <p className="text-sm text-gray-600 mb-6">
            Store your API keys securely. They will be encrypted and never logged.
          </p>

          {message && (
            <div
              className={`mb-4 p-3 rounded text-sm ${
                message.type === 'success'
                  ? 'bg-green-100 text-green-800 border border-green-400'
                  : 'bg-red-100 text-red-800 border border-red-400'
              }`}
            >
              {message.text}
            </div>
          )}

          <form onSubmit={handleSaveKey} className="space-y-4">
            <div>
              <label htmlFor="keyType" className="block text-sm font-medium text-gray-700 mb-1">
                Provider
              </label>
              <select
                id="keyType"
                value={keyType}
                onChange={(e) => setKeyType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="tavily">Tavily</option>
                <option value="gemini">Google Gemini</option>
              </select>
            </div>

            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
                API Key
              </label>
              <input
                id="apiKey"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Paste your API key here"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition"
            >
              {loading ? 'Saving...' : 'Save Key'}
            </button>
          </form>
        </div>

        {/* Saved Keys */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Saved Keys</h2>
          {savedKeys.length === 0 ? (
            <p className="text-gray-600 text-sm">No keys saved yet</p>
          ) : (
            <div className="space-y-2">
              {savedKeys.map((key) => (
                <div
                  key={key}
                  className="flex items-center justify-between bg-gray-50 rounded p-3"
                >
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {key}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">Saved</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* General Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">General</h2>
        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4" defaultChecked />
              <span className="text-sm font-medium text-gray-700">Email notifications</span>
            </label>
          </div>
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4" defaultChecked />
              <span className="text-sm font-medium text-gray-700">Auto-save drafts</span>
            </label>
          </div>
          <div>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4" />
              <span className="text-sm font-medium text-gray-700">Dark mode</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
