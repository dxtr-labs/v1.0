'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface AgentData {
  agent_id: string;
  name: string;
  role: string;
  mode: string;
  status: string;
}

export default function AgentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const agentId = params.id as string;
  const [agent, setAgent] = useState<AgentData | null>(null);

  useEffect(() => {
    if (!agentId) return;
    fetch(`/api/agents/${agentId}`)
      .then(res => res.json())
      .then(data => setAgent(data));
  }, [agentId]);

  const handleLaunchChat = () => {
    router.push(`/dashboard/agents/${agent?.agent_id}/chat?agentId=${agent?.agent_id}`);
  };

  if (!agent) return (
    <div className="p-6">
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-[#DAA520]/20 dark:bg-[#D2BD96]/20 rounded w-1/3"></div>
        <div className="h-4 bg-[#DAA520]/20 dark:bg-[#D2BD96]/20 rounded w-1/2"></div>
        <div className="h-4 bg-[#DAA520]/20 dark:bg-[#D2BD96]/20 rounded w-1/4"></div>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Agent Header */}
      <div className="bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-sm border border-[#DAA520]/20 dark:border-[#D2BD96]/20 rounded-xl p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="h-16 w-16 rounded-full bg-gradient-to-r from-[#DAA520] to-[#D2BD96] flex items-center justify-center">
            <span className="text-white font-bold text-xl">{agent?.name?.charAt(0)?.toUpperCase() || 'A'}</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-[#1a1a1a] dark:text-[#F2EBE2] mb-2">{agent?.name || 'Loading...'}</h1>
            <p className="text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70 text-lg">{agent?.role || 'Loading...'}</p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-2 mb-6">
          <div className={`h-3 w-3 rounded-full ${agent?.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <span className="text-sm font-medium text-[#1a1a1a]/80 dark:text-[#F2EBE2]/80">
            {agent?.status === 'active' ? 'Active' : 'Inactive'}
          </span>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleLaunchChat}
            className="px-6 py-3 bg-[#DAA520] hover:bg-[#DAA520]/80 dark:bg-[#D2BD96] dark:hover:bg-[#D2BD96]/80 text-white rounded-lg font-medium transition-all duration-200 hover:scale-105"
          >
            Launch Chat
          </button>
          <button
            onClick={() => router.push(`/dashboard/agents/${agent?.agent_id}/edit`)}
            className="px-6 py-3 border-2 border-[#DAA520] dark:border-[#D2BD96] text-[#DAA520] dark:text-[#D2BD96] hover:bg-[#DAA520]/10 dark:hover:bg-[#D2BD96]/10 rounded-lg font-medium transition-all duration-200"
          >
            Edit Agent
          </button>
        </div>
      </div>

      {/* Agent Details */}
      <div className="bg-white/80 dark:bg-[#1a1a1a]/80 backdrop-blur-sm border border-[#DAA520]/20 dark:border-[#D2BD96]/20 rounded-xl p-6">
        <h2 className="text-xl font-semibold text-[#1a1a1a] dark:text-[#F2EBE2] mb-4">Agent Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">Mode</label>
            <p className="text-[#1a1a1a] dark:text-[#F2EBE2] font-medium">{agent?.mode || 'Loading...'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-[#1a1a1a]/70 dark:text-[#F2EBE2]/70">Role</label>
            <p className="text-[#1a1a1a] dark:text-[#F2EBE2] font-medium">{agent?.role || 'Loading...'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
