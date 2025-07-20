// app/dashboard/agents/create/page.tsx

"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Send, Bot, User } from "lucide-react";

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

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
  const [createdAgent, setCreatedAgent] = useState<CreatedAgent | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
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
        setCreatedAgent(result.agent);
        
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
        }
        
        // Add welcome message from the agent
        const welcomeMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'assistant',
          content: `Hello! I'm ${form.name}, your new ${form.role} agent. I'm ready to help you with your tasks. What would you like to work on?`,
          timestamp: new Date()
        };
        setChatMessages([welcomeMessage]);
      } else {
        alert("Failed to create agent.");
      }
    } catch (error) {
      console.error('Agent creation error:', error);
      alert("Failed to create agent.");
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !createdAgent) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: chatInput,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput("");
    setChatLoading(true);

    try {
      const res = await fetch("/api/chat/mcpai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: chatInput,
          agentId: createdAgent.AgentID,
          agentConfig: {
            name: createdAgent.name,
            role: createdAgent.role,
            personality: createdAgent.personality,
            llm_config: createdAgent.llm_config
          }
        }),
      });

      if (res.ok) {
        const result: any = await res.json();
        const assistantMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: result.response,
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: "Sorry, I encountered an error. Please try again.",
          timestamp: new Date()
        };
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {!showChat ? (
        // Agent Creation Form
        <>
          <h1 className="text-2xl font-bold text-[#0F172A]">➕ Create New Agent</h1>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <Label>Name</Label>
              <Input name="name" value={form.name} onChange={handleChange} required />
            </div>

            <div>
              <Label>Role</Label>
              <Input name="role" value={form.role} onChange={handleChange} required />
            </div>

            <div>
              <Label>Mode</Label>
              <select
                name="mode"
                className="w-full border border-[#8B5CF6] rounded px-3 py-2 bg-[#F8FAFC] text-[#0F172A]"
                value={form.mode}
                onChange={handleModeChange}
              >
                <option value="single">Single</option>
                <option value="multi">Multi</option>
              </select>
            </div>

            <div>
              <Label>Personality & Instructions</Label>
              <Textarea
                name="personality"
                value={form.personality}
                onChange={handleChange}
                placeholder="Describe how this agent should behave, respond, and what tasks it should help with..."
                rows={4}
              />
            </div>

            <Button type="submit" disabled={loading} className="bg-[#3B82F6] text-white hover:bg-[#1D4ED8]">
              {loading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Creating Agent...
                </div>
              ) : (
                "Create Agent & Start Chat"
              )}
            </Button>
          </form>
        </>
      ) : (
        // Chat Interface
        <>
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-[#0F172A]">
              💬 Chat with {createdAgent?.name}
            </h1>
            <div className="flex gap-2">
              <Button 
                variant="ghost" 
                onClick={() => {
                  // Add a timestamp to force a refresh
                  router.push(`/dashboard/agents?refresh=${Date.now()}`);
                }}
                className="border border-[#3B82F6] text-[#3B82F6] hover:bg-[#3B82F6] hover:text-white"
              >
                View All Agents
              </Button>
              <Button 
                variant="ghost" 
                onClick={() => setShowChat(false)}
                className="border border-[#8B5CF6] text-[#0F172A] hover:bg-[#8B5CF6]"
              >
                Back to Create
              </Button>
            </div>
          </div>

          {/* Agent Info Card */}
          <div className="bg-[#F8FAFC] border border-[#8B5CF6] rounded-lg p-4">
            <h3 className="font-semibold text-[#0F172A] mb-2">Agent Details</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><strong>Name:</strong> {createdAgent?.name}</div>
              <div><strong>Role:</strong> {createdAgent?.role}</div>
              <div><strong>Mode:</strong> {createdAgent?.mode}</div>
              <div><strong>ID:</strong> {createdAgent?.AgentID}</div>
            </div>
          </div>

          {/* Chat Container */}
          <div className="bg-white border border-[#8B5CF6] rounded-lg h-96 flex flex-col">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg flex items-start gap-2 ${
                      message.type === 'user'
                        ? 'bg-[#3B82F6] text-white'
                        : 'bg-[#F8FAFC] text-[#0F172A] border border-[#8B5CF6]'
                    }`}
                  >
                    {message.type === 'assistant' && (
                      <Bot className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    )}
                    {message.type === 'user' && (
                      <User className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="text-sm">{message.content}</div>
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-[#F8FAFC] text-[#0F172A] border border-[#8B5CF6] px-4 py-2 rounded-lg flex items-center gap-2">
                    <Bot className="h-4 w-4" />
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat Input */}
            <div className="border-t border-[#8B5CF6] p-4">
              <form onSubmit={handleChatSubmit} className="flex gap-2">
                <Input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder={`Message ${createdAgent?.name}...`}
                  disabled={chatLoading}
                  className="flex-1"
                />
                <Button 
                  type="submit" 
                  disabled={chatLoading || !chatInput.trim()}
                  className="bg-[#3B82F6] text-white hover:bg-[#1D4ED8]"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </div>
        </>
      )}
    </div>
  );
}


