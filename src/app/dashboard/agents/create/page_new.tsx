// app/dashboard/agents/create/page.tsx

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Bot } from "lucide-react";
import { motion } from "framer-motion";

interface CreatedAgent {
  AgentID: string;
  name: string;
  role: string;
  mode: string;
  personality: any;
  llm_config: any;
}

export default function CreateAgentPage() {
  const [form, setForm] = useState({
    name: "",
    role: "",
    mode: "single",
    personality: "",
  });
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, mode: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch("/api/agents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (res.ok) {
        const result: any = await res.json();
        
        // Store the agent locally for immediate display
        if (typeof window !== 'undefined') {
          try {
            const existingAgents = localStorage.getItem('local-agents');
            const agents = existingAgents ? JSON.parse(existingAgents) : [];
            agents.push(result.agent);
            localStorage.setItem('local-agents', JSON.stringify(agents));
            console.log('Stored agent locally:', result.agent);
          } catch (error) {
            console.error('Error storing agent locally:', error);
          }
        }
        
        // Redirect to enhanced chat interface
        router.push(`/dashboard/agents/${result.agent.AgentID}/chat?agentId=${result.agent.AgentID}`);
      } else {
        alert("Failed to create agent");
      }
    } catch (error) {
      console.error('Error creating agent:', error);
      alert("Error creating agent");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="h-10 w-10 rounded-full bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">Create New Agent</h1>
        </div>

        <div className="bg-white/80 dark:bg-[#0F172A]/80 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 rounded-xl p-6">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Agent Name</Label>
              <Input 
                name="name" 
                value={form.name} 
                onChange={handleChange} 
                required 
                placeholder="e.g., Marketing Assistant"
                className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
              />
            </div>

            <div>
              <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Role & Expertise</Label>
              <Input 
                name="role" 
                value={form.role} 
                onChange={handleChange} 
                required 
                placeholder="e.g., Marketing Specialist, Data Analyst, Customer Support"
                className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
              />
            </div>

            <div>
              <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Operation Mode</Label>
              <select
                name="mode"
                className="mt-2 w-full border border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 rounded-lg px-3 py-2 bg-white/50 dark:bg-[#0F172A]/50 text-[#0F172A] dark:text-[#F8FAFC] focus:border-[#3B82F6] dark:focus:border-[#8B5CF6] focus:outline-none"
                value={form.mode}
                onChange={handleModeChange}
              >
                <option value="single">Single Session</option>
                <option value="multi">Multi Session</option>
              </select>
            </div>

            <div>
              <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Personality & Instructions</Label>
              <Textarea
                name="personality"
                value={form.personality}
                onChange={handleChange}
                placeholder="Describe the agent's personality, tone, and specific instructions. e.g., 'You are a friendly and professional marketing expert who speaks clearly and provides actionable advice...'"
                rows={6}
                className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] hover:from-[#1D4ED8] hover:to-[#10B981] text-white font-semibold py-3 rounded-xl transition-all transform hover:scale-105 active:scale-95 shadow-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Creating Agent...
                </>
              ) : (
                <>
                  <Bot className="mr-2 h-5 w-5" />
                  Create Agent & Start Chat
                </>
              )}
            </Button>
          </form>
        </div>

        <div className="text-center text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60">
          After creation, you&apos;ll be taken directly to chat with your new agent
        </div>
      </motion.div>
    </div>
  );
}


