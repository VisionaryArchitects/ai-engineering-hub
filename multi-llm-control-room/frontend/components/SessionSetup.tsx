'use client';

import React, { useState } from 'react';
import { ModelConfig } from '@/lib/store';

interface SessionSetupProps {
  onStart: (routing: string, models: ModelConfig[]) => void;
}

const SessionSetup: React.FC<SessionSetupProps> = ({ onStart }) => {
  const [routing, setRouting] = useState('broadcast');
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [currentModel, setCurrentModel] = useState({
    provider: 'ollama',
    model_name: '',
    role: '',
  });

  const addModel = () => {
    if (currentModel.model_name && models.length < 5) {
      setModels([
        ...models,
        {
          id: `model_${models.length + 1}`,
          ...currentModel,
          temperature: 0.7,
        },
      ]);
      setCurrentModel({ provider: 'ollama', model_name: '', role: '' });
    }
  };

  const removeModel = (id: string) => {
    setModels(models.filter((m) => m.id !== id));
  };

  const handleStart = () => {
    if (models.length > 0) {
      onStart(routing, models);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-gray-800 rounded-lg">
      <h2 className="text-2xl font-bold mb-6">🚀 Create New Session</h2>

      {/* Routing Pattern */}
      <div className="mb-6">
        <label className="block text-sm font-semibold mb-2">
          Routing Pattern
        </label>
        <select
          value={routing}
          onChange={(e) => setRouting(e.target.value)}
          className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
        >
          <option value="broadcast">Broadcast (All respond)</option>
          <option value="round_robin">Round Robin (Take turns)</option>
          <option value="coordinator">Coordinator (Delegate)</option>
          <option value="voting">Voting (Consensus)</option>
        </select>
      </div>

      {/* Add Model */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg">
        <h3 className="font-semibold mb-3">Add Model ({models.length}/5)</h3>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="block text-xs mb-1">Provider</label>
            <select
              value={currentModel.provider}
              onChange={(e) =>
                setCurrentModel({ ...currentModel, provider: e.target.value })
              }
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded focus:outline-none focus:border-blue-500 text-sm"
            >
              <option value="ollama">Ollama (Local)</option>
              <option value="lmstudio">LM Studio (Local)</option>
              <option value="azure_openai">Azure OpenAI</option>
              <option value="openai_compatible">OpenAI Compatible</option>
            </select>
          </div>

          <div>
            <label className="block text-xs mb-1">Model Name</label>
            <input
              type="text"
              value={currentModel.model_name}
              onChange={(e) =>
                setCurrentModel({ ...currentModel, model_name: e.target.value })
              }
              placeholder="llama2, codellama, etc."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        </div>

        <div className="mb-3">
          <label className="block text-xs mb-1">Role (optional)</label>
          <input
            type="text"
            value={currentModel.role}
            onChange={(e) =>
              setCurrentModel({ ...currentModel, role: e.target.value })
            }
            placeholder="Architect, Coder, Reviewer, etc."
            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>

        <button
          onClick={addModel}
          disabled={!currentModel.model_name || models.length >= 5}
          className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded font-semibold transition"
        >
          + Add Model
        </button>
      </div>

      {/* Model List */}
      {models.length > 0 && (
        <div className="mb-6">
          <h3 className="font-semibold mb-2">Active Models:</h3>
          <div className="space-y-2">
            {models.map((model) => (
              <div
                key={model.id}
                className="flex items-center justify-between p-3 bg-gray-700 rounded"
              >
                <div>
                  <span className="font-semibold">{model.provider}</span> /{' '}
                  {model.model_name}
                  {model.role && (
                    <span className="ml-2 text-sm text-gray-400">
                      ({model.role})
                    </span>
                  )}
                </div>
                <button
                  onClick={() => removeModel(model.id)}
                  className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Start Button */}
      <button
        onClick={handleStart}
        disabled={models.length === 0}
        className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-bold text-lg transition"
      >
        🚀 Start Session
      </button>
    </div>
  );
};

export default SessionSetup;
