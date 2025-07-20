// app/dashboard/agents/create/page.tsx

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Bot, Clock, Webhook, Mail, Settings, ChevronDown, Info, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface CreatedAgent {
  id: string;
  name: string;
  role: string;
  personality: any;
}

interface TriggerTemplate {
  label: string;
  examples: Array<{
    name: string;
    description: string;
    config: any;
  }>;
}

interface TriggerTemplates {
  cron: TriggerTemplate;
  webhook: TriggerTemplate;
  email_imap: TriggerTemplate;
}

export default function CreateAgentPage() {
  const [form, setForm] = useState({
    name: "",
    role: "",
    personality: "",
    expectations: "",
  });
  
  const [triggerConfig, setTriggerConfig] = useState({
    triggerType: "",
    executionMode: "single_time", // single_time or multi_time
    triggerSettings: {} as any,
  });
  
  const [triggerTemplates, setTriggerTemplates] = useState<TriggerTemplates | null>(null);
  const [selectedExample, setSelectedExample] = useState<any>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [templatesLoading, setTemplatesLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchTriggerTemplates = async () => {
      try {
        const response = await fetch('/api/triggers/templates');
        const data = await response.json();
        if (data.success) {
          setTriggerTemplates(data.templates);
        }
      } catch (error) {
        console.error('Failed to fetch trigger templates:', error);
      } finally {
        setTemplatesLoading(false);
      }
    };

    fetchTriggerTemplates();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTriggerConfigChange = (field: string, value: any) => {
    setTriggerConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTriggerSettingsChange = (field: string, value: any) => {
    setTriggerConfig(prev => ({
      ...prev,
      triggerSettings: {
        ...prev.triggerSettings,
        [field]: value
      }
    }));
  };

  const applyExample = (example: any) => {
    setSelectedExample(example);
    setTriggerConfig(prev => ({
      ...prev,
      triggerSettings: { ...example.config }
    }));
  };

  const validateForm = () => {
    const errors: string[] = [];
    
    if (!form.name.trim()) errors.push("Agent name is required");
    if (!form.role.trim()) errors.push("Agent role is required");
    if (!form.personality.trim()) errors.push("Agent personality is required");
    if (!form.expectations.trim()) errors.push("Agent expectations are required");
    
    if (triggerConfig.triggerType && triggerConfig.triggerType !== 'manual') {
      if (!triggerConfig.executionMode) {
        errors.push("Execution mode is required for non-manual triggers");
      }
      
      // Validate trigger-specific settings
      if (triggerConfig.triggerType === 'cron') {
        if (!triggerConfig.triggerSettings.triggerTimes || triggerConfig.triggerSettings.triggerTimes.length === 0) {
          errors.push("Schedule times are required for timer triggers");
        }
      } else if (triggerConfig.triggerType === 'webhook') {
        if (!triggerConfig.triggerSettings.path) {
          errors.push("Webhook path is required");
        }
      } else if (triggerConfig.triggerType === 'email_imap') {
        if (!triggerConfig.triggerSettings.mailbox) {
          errors.push("Mailbox is required for email triggers");
        }
      }
    }
    
    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);

    try {
      const payload = {
        ...form,
        ...(triggerConfig.triggerType && {
          triggerType: triggerConfig.triggerType,
          executionMode: triggerConfig.executionMode,
          triggerSettings: triggerConfig.triggerSettings
        })
      };

      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const result = await response.json();
        router.push(`/dashboard/agents?refresh=true`);
      } else {
        const errorData = await response.json();
        setValidationErrors([errorData.error || 'Failed to create agent']);
      }
    } catch (error) {
      console.error('Error creating agent:', error);
      setValidationErrors(['Network error occurred']);
    } finally {
      setLoading(false);
    }
  };

  const getTriggerIcon = (type: string) => {
    switch (type) {
      case 'cron': return <Clock className="w-4 h-4" />;
      case 'webhook': return <Webhook className="w-4 h-4" />;
      case 'email_imap': return <Mail className="w-4 h-4" />;
      case 'manual': return <Settings className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  const getTriggerLabel = (type: string) => {
    switch (type) {
      case 'cron': return 'Timer Based';
      case 'webhook': return 'Webhook';
      case 'email_imap': return 'Email';
      case 'manual': return 'Manual';
      default: return type;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F8FAFC] to-[#E6D5C3] dark:from-[#0F172A] dark:to-[#2d2d2d] p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Bot className="w-16 h-16 text-[#3B82F6] dark:text-[#8B5CF6]" />
          </div>
          <h1 className="text-4xl font-bold text-[#0F172A] dark:text-[#F8FAFC] mb-2">
            Create New Agent
          </h1>
          <p className="text-lg text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
            Design a custom AI agent with specific personality and triggers
          </p>
        </div>

        <div className="bg-white/70 dark:bg-[#0F172A]/70 backdrop-blur-sm rounded-2xl shadow-xl border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 p-8">
          {validationErrors.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-6"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="text-sm font-medium text-red-800 dark:text-red-200 mb-2">
                    Please fix the following errors:
                  </h3>
                  <ul className="list-disc list-inside space-y-1">
                    {validationErrors.map((error, index) => (
                      <li key={index} className="text-sm text-red-700 dark:text-red-300">
                        {error}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Agent Name</Label>
                <Input
                  name="name"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="e.g., Customer Support Bot"
                  className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
                />
              </div>

              <div>
                <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Agent Role</Label>
                <Input
                  name="role"
                  value={form.role}
                  onChange={handleChange}
                  placeholder="e.g., Customer Support Specialist"
                  className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
                />
              </div>
            </div>

            {/* Personality */}
            <div>
              <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Agent Personality</Label>
              <Textarea
                name="personality"
                value={form.personality}
                onChange={handleChange}
                placeholder="Describe the agent's personality, communication style, and approach to interactions..."
                rows={4}
                className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
              />
            </div>

            {/* Expectations */}
            <div>
              <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Agent Expectations</Label>
              <Textarea
                name="expectations"
                value={form.expectations}
                onChange={handleChange}
                placeholder="What should this agent accomplish? What are its main goals and expected outcomes?"
                rows={3}
                className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 focus:border-[#3B82F6] dark:focus:border-[#8B5CF6]"
              />
            </div>

            {/* Trigger Configuration */}
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Trigger Configuration</Label>
                <div className="group relative">
                  <Info className="w-4 h-4 text-[#3B82F6] dark:text-[#8B5CF6] cursor-help" />
                  <div className="invisible group-hover:visible absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
                    Optional: Configure when and how this agent should be triggered
                  </div>
                </div>
              </div>

              {/* Trigger Type Selection */}
              <div>
                <Label className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-2 block">
                  Trigger Type (Optional)
                </Label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['manual', 'cron', 'webhook', 'email_imap'].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => handleTriggerConfigChange('triggerType', triggerConfig.triggerType === type ? '' : type)}
                      className={`p-3 rounded-lg border-2 transition-all duration-200 flex flex-col items-center gap-2 ${
                        triggerConfig.triggerType === type
                          ? 'border-[#3B82F6] bg-[#3B82F6]/10 dark:border-[#8B5CF6] dark:bg-[#8B5CF6]/10'
                          : 'border-gray-200 dark:border-gray-700 hover:border-[#3B82F6]/50 dark:hover:border-[#8B5CF6]/50'
                      }`}
                    >
                      {getTriggerIcon(type)}
                      <span className="text-sm font-medium text-[#0F172A] dark:text-[#F8FAFC]">
                        {getTriggerLabel(type)}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Execution Mode - Only show for non-manual triggers */}
              {triggerConfig.triggerType && triggerConfig.triggerType !== 'manual' && (
                <div>
                  <Label className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-2 block">
                    Execution Mode
                  </Label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="executionMode"
                        value="single_time"
                        checked={triggerConfig.executionMode === 'single_time'}
                        onChange={(e) => handleTriggerConfigChange('executionMode', e.target.value)}
                        className="text-[#3B82F6]"
                      />
                      <span className="text-sm text-[#0F172A] dark:text-[#F8FAFC]">Single Time</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="executionMode"
                        value="multi_time"
                        checked={triggerConfig.executionMode === 'multi_time'}
                        onChange={(e) => handleTriggerConfigChange('executionMode', e.target.value)}
                        className="text-[#3B82F6]"
                      />
                      <span className="text-sm text-[#0F172A] dark:text-[#F8FAFC]">Multi Time</span>
                    </label>
                  </div>
                </div>
              )}

              {/* Trigger-specific configuration */}
              {triggerConfig.triggerType && triggerConfig.triggerType !== 'manual' && (
                <div className="space-y-4">
                  {triggerConfig.triggerType === 'cron' && (
                    <CronTriggerConfig 
                      settings={triggerConfig.triggerSettings} 
                      onChange={handleTriggerSettingsChange}
                    />
                  )}
                  {triggerConfig.triggerType === 'webhook' && (
                    <WebhookTriggerConfig 
                      settings={triggerConfig.triggerSettings} 
                      onChange={handleTriggerSettingsChange}
                    />
                  )}
                  {triggerConfig.triggerType === 'email_imap' && (
                    <EmailTriggerConfig 
                      settings={triggerConfig.triggerSettings} 
                      onChange={handleTriggerSettingsChange}
                    />
                  )}
                </div>
              )}
            </div>

            <Button
              type="submit"
              disabled={loading || templatesLoading}
              className="w-full bg-[#3B82F6] hover:bg-[#B8860B] text-white font-medium py-3 rounded-lg transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Creating Agent...
                </>
              ) : (
                'Create Agent'
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

// Cron Trigger Configuration Component
function CronTriggerConfig({ settings, onChange }: { settings: any; onChange: (field: string, value: any) => void }) {
  const [schedules, setSchedules] = useState(settings.triggerTimes || [{ hour: 9, minute: 0, weekday: '*' }]);

  const updateSchedule = (index: number, field: string, value: any) => {
    const updated = [...schedules];
    updated[index] = { ...updated[index], [field]: value };
    setSchedules(updated);
    onChange('triggerTimes', updated);
  };

  const addSchedule = () => {
    const newSchedule = { hour: 9, minute: 0, weekday: '*' };
    const updated = [...schedules, newSchedule];
    setSchedules(updated);
    onChange('triggerTimes', updated);
  };

  const removeSchedule = (index: number) => {
    if (schedules.length > 1) {
      const updated = schedules.filter((_, i) => i !== index);
      setSchedules(updated);
      onChange('triggerTimes', updated);
    }
  };

  return (
    <div className="space-y-4">
      <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Schedule Times</Label>
      {schedules.map((schedule, index) => (
        <div key={index} className="grid grid-cols-12 gap-3 items-center">
          <div className="col-span-3">
            <Label className="text-xs text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Hour</Label>
            <Input
              type="number"
              min="0"
              max="23"
              value={schedule.hour}
              onChange={(e) => updateSchedule(index, 'hour', parseInt(e.target.value))}
              className="bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30"
            />
          </div>
          <div className="col-span-3">
            <Label className="text-xs text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Minute</Label>
            <Input
              type="number"
              min="0"
              max="59"
              value={schedule.minute}
              onChange={(e) => updateSchedule(index, 'minute', parseInt(e.target.value))}
              className="bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30"
            />
          </div>
          <div className="col-span-4">
            <Label className="text-xs text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Weekday</Label>
            <select
              value={schedule.weekday}
              onChange={(e) => updateSchedule(index, 'weekday', e.target.value)}
              className="w-full p-2 bg-white/50 dark:bg-[#0F172A]/50 border border-[#3B82F6]/30 rounded-md"
            >
              <option value="*">Every Day</option>
              <option value="1-5">Weekdays</option>
              <option value="6,0">Weekends</option>
              <option value="1">Monday</option>
              <option value="2">Tuesday</option>
              <option value="3">Wednesday</option>
              <option value="4">Thursday</option>
              <option value="5">Friday</option>
              <option value="6">Saturday</option>
              <option value="0">Sunday</option>
            </select>
          </div>
          <div className="col-span-2 flex gap-1">
            {schedules.length > 1 && (
              <Button
                type="button"
                variant="secondary"
                onClick={() => removeSchedule(index)}
                className="w-8 h-8 p-0"
              >
                ×
              </Button>
            )}
          </div>
        </div>
      ))}
      <Button type="button" variant="secondary" onClick={addSchedule} className="w-full">
        Add Schedule
      </Button>
    </div>
  );
}

// Webhook Trigger Configuration Component
function WebhookTriggerConfig({ settings, onChange }: { settings: any; onChange: (field: string, value: any) => void }) {
  return (
    <div className="space-y-4">
      <div>
        <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Webhook Path</Label>
        <Input
          value={settings.path || ''}
          onChange={(e) => onChange('path', e.target.value)}
          placeholder="/webhooks/my-agent"
          className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
        />
        <p className="text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60 mt-1">
          The webhook will be available at: https://your-domain.com{settings.path || '/webhooks/your-path'}
        </p>
      </div>
    </div>
  );
}

// Email Trigger Configuration Component
function EmailTriggerConfig({ settings, onChange }: { settings: any; onChange: (field: string, value: any) => void }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Mailbox</Label>
          <Input
            value={settings.mailbox || ''}
            onChange={(e) => onChange('mailbox', e.target.value)}
            placeholder="INBOX"
            className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
          />
        </div>
        <div>
          <Label className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">Subject Filter (Optional)</Label>
          <Input
            value={settings.subjectFilter || ''}
            onChange={(e) => onChange('subjectFilter', e.target.value)}
            placeholder="Support Request"
            className="mt-2 bg-white/50 dark:bg-[#0F172A]/50 border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
          />
        </div>
      </div>
    </div>
  );
}


