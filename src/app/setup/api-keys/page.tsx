'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

export default function APIKeysSetupPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [model, setModel] = useState('');
  const [returnUrl, setReturnUrl] = useState('/chat');
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const modelParam = searchParams.get('model');
    const returnUrlParam = searchParams.get('returnUrl');
    
    if (modelParam) setModel(modelParam);
    if (returnUrlParam) setReturnUrl(returnUrlParam);
  }, [searchParams]);

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      alert('Please enter a valid API key');
      return;
    }

    setIsLoading(true);
    try {
      // Save API key to local storage for now (in production, this should be more secure)
      localStorage.setItem(`${model}_api_key`, apiKey);
      
      // Redirect back to the workflow builder
      router.push(returnUrl);
    } catch (error) {
      console.error('Failed to save API key:', error);
      alert('Failed to save API key. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUseDeepSeek = () => {
    // Redirect back to workflow builder without saving API key
    router.push(returnUrl);
  };

  const getModelInfo = (modelName: string) => {
    switch (modelName.toLowerCase()) {
      case 'gemini':
        return {
          name: 'Google Gemini Pro',
          icon: '🤖',
          description: 'Advanced AI from Google with excellent reasoning capabilities',
          apiKeyUrl: 'https://ai.google.dev/',
          placeholder: 'Enter your Google AI Studio API key...'
        };
      case 'openai':
        return {
          name: 'OpenAI GPT',
          icon: '🧠',
          description: 'Powerful language model from OpenAI',
          apiKeyUrl: 'https://platform.openai.com/api-keys',
          placeholder: 'Enter your OpenAI API key...'
        };
      case 'claude':
        return {
          name: 'Anthropic Claude',
          icon: '💎',
          description: 'Safe, helpful AI assistant from Anthropic',
          apiKeyUrl: 'https://console.anthropic.com/',
          placeholder: 'Enter your Anthropic API key...'
        };
      default:
        return {
          name: 'AI Model',
          icon: '🤖',
          description: 'External AI model',
          apiKeyUrl: '#',
          placeholder: 'Enter your API key...'
        };
    }
  };

  const modelInfo = getModelInfo(model);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">{modelInfo.icon}</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Setup {modelInfo.name}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            {modelInfo.description}
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={modelInfo.placeholder}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="text-xs text-gray-500 dark:text-gray-400">
            <p>
              Need an API key? Get one from{' '}
              <a 
                href={modelInfo.apiKeyUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                {modelInfo.name}
              </a>
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleSaveApiKey}
              disabled={isLoading || !apiKey.trim()}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:cursor-not-allowed"
            >
              {isLoading ? 'Saving...' : 'Save & Continue'}
            </button>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-600 pt-4">
            <div className="text-center">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                Prefer to use free AI instead?
              </p>
              <button
                onClick={handleUseDeepSeek}
                className="flex items-center justify-center gap-2 w-full bg-green-50 dark:bg-green-900/20 border border-green-300 dark:border-green-600 text-green-700 dark:text-green-300 font-medium py-2 px-4 rounded-md hover:bg-green-100 dark:hover:bg-green-900/40 transition-colors"
              >
                <span>🏠</span>
                Use DeepSeek (Free & Local)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
