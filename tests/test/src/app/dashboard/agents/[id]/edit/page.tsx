'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, ArrowLeft } from "lucide-react";

interface AgentData {
  id: string;  // Changed from AgentID to id
  name: string;
  role: string;
  mode: string;
  personality?: any;
  description?: string;
}

export default function EditAgentPage() {
  const router = useRouter();
  const params = useParams();
  const agentId = params.id as string;
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [agent, setAgent] = useState<AgentData | null>(null);
  const [form, setForm] = useState({
    name: '',
    role: '',
    mode: 'single',
    personality: '',
    description: ''
  });

  useEffect(() => {
    if (agentId) {
      fetchAgent();
    }
  }, [agentId]);

  const fetchAgent = async () => {
    try {
      const response = await fetch(`/api/agents/${agentId}`);
      if (response.ok) {
        const agentData = await response.json();
        setAgent(agentData);
        setForm({
          name: agentData.name || '',
          role: agentData.role || '',
          mode: agentData.mode || 'single',
          personality: typeof agentData.personality === 'string' ? agentData.personality : '',
          description: agentData.description || ''
        });
      }
    } catch (error) {
      console.error('Failed to fetch agent:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await fetch(`/api/agents/${agentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      });

      if (response.ok) {
        router.push('/dashboard/agents');
      } else {
        alert('Failed to update agent. Please try again.');
      }
    } catch (error) {
      console.error('Update error:', error);
      alert('Failed to update agent. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin h-6 w-6 text-[#DAA520] mr-2" />
          <span className="text-[#1a1a1a]">Loading agent details...</span>
        </div>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="p-6 max-w-2xl mx-auto">
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-[#1a1a1a] mb-2">Agent not found</h2>
          <p className="text-gray-600 mb-4">The agent you're looking for doesn't exist.</p>
          <Button onClick={() => router.push('/dashboard/agents')}>
            Back to Agents
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard/agents')}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Agents
        </Button>
        <h1 className="text-2xl font-bold text-[#1a1a1a]">✏️ Edit Agent</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Agent Name</Label>
          <Input
            id="name"
            name="name"
            value={form.name}
            onChange={handleChange}
            required
            placeholder="Enter agent name"
          />
        </div>

        <div>
          <Label htmlFor="role">Role</Label>
          <Input
            id="role"
            name="role"
            value={form.role}
            onChange={handleChange}
            required
            placeholder="e.g., Customer Support, Data Analyst"
          />
        </div>

        <div>
          <Label htmlFor="mode">Mode</Label>
          <select
            id="mode"
            name="mode"
            value={form.mode}
            onChange={handleChange}
            className="w-full border border-[#D2BD96] rounded px-3 py-2 bg-[#F2EBE2] text-[#1a1a1a]"
          >
            <option value="single">Single</option>
            <option value="multi">Multi</option>
          </select>
        </div>

        <div>
          <Label htmlFor="personality">Personality & Instructions</Label>
          <Textarea
            id="personality"
            name="personality"
            value={form.personality}
            onChange={handleChange}
            placeholder="Describe how this agent should behave and respond..."
            rows={4}
          />
        </div>

        <div>
          <Label htmlFor="description">Description (Optional)</Label>
          <Textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Brief description of what this agent does..."
            rows={2}
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="submit"
            disabled={saving}
            className="bg-[#DAA520] text-white hover:bg-[#B8941C]"
          >
            {saving ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                Updating...
              </div>
            ) : (
              'Update Agent'
            )}
          </Button>
          
          <Button
            type="button"
            variant="ghost"
            onClick={() => router.push('/dashboard/agents')}
            className="border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
