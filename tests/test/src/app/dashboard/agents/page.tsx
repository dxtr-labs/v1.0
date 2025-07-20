'use client';

import React, { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Loader2, MoreVertical, Edit2, Trash2, Eye, Play, Clock, Zap, Mail, Calendar } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

interface Trigger {
    id: string;
    trigger_type: 'cron' | 'webhook' | 'email_imap';
    trigger_config: any;
    is_active: boolean;
}

interface Agent {
    id: string;  // Changed from AgentID to id to match backend
    name: string;
    role: string;
    mode?: string;
    status?: string;
    description?: string;
    created?: string;
    triggers?: Trigger[];
}

export default function AgentsPage() {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [loading, setLoading] = useState(true);
    const [openMenuId, setOpenMenuId] = useState<string | null>(null);
    const [deleteLoading, setDeleteLoading] = useState<string | null>(null);
    const [triggerLoading, setTriggerLoading] = useState<string | null>(null);
    const menuRef = useRef<HTMLDivElement>(null);
    const searchParams = useSearchParams();

    // Close menu when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setOpenMenuId(null);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const fetchAgents = () => {
        console.log('Fetching agents...');
        setLoading(true);
        
        // Fetch from API
        fetch("/api/agents", { credentials: 'include' })
            .then((res) => res.json())
            .then((data: any) => {
                console.log('Fetched agents data:', data);
                const agentsArray = Array.isArray(data.agents) ? data.agents : [];
                setAgents(agentsArray);
                setLoading(false);
            })
            .catch((error) => {
                console.error('Error fetching agents:', error);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchAgents();

        // Refresh agents when page becomes visible (when navigating back from create page)
        const handleVisibilityChange = () => {
            if (!document.hidden) {
                fetchAgents();
            }
        };

        const handleFocus = () => {
            fetchAgents();
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('focus', handleFocus);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibilityChange);
            window.removeEventListener('focus', handleFocus);
        };
    }, []);

    // Refresh when URL params change (like when coming from create page)
    useEffect(() => {
        if (searchParams) {
            const refresh = searchParams.get('refresh');
            if (refresh) {
                console.log('Refreshing agents due to URL param');
                fetchAgents();
            }
        }
    }, [searchParams]);

    const handleDeleteAgent = async (agentId: string) => {
        console.log('Delete button clicked for agent:', agentId);
        if (!confirm('Are you sure you want to delete this agent? This action cannot be undone.')) {
            return;
        }

        console.log('User confirmed deletion for agent:', agentId);
        setDeleteLoading(agentId);
        try {
            const response = await fetch(`/api/agents/${agentId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            
            if (response.ok) {
                // Remove agent from state
                setAgents(agents.filter(agent => agent.id !== agentId));
                setOpenMenuId(null);
                console.log('Agent deleted successfully');
            } else {
                const errorData = await response.json();
                console.error('Delete failed:', errorData);
                alert('Failed to delete agent. Please try again.');
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert('Failed to delete agent. Please try again.');
        } finally {
            setDeleteLoading(null);
        }
    };

    const handleManualTrigger = async (agentId: string) => {
        if (!confirm('Are you sure you want to manually trigger this agent?')) {
            return;
        }

        setTriggerLoading(agentId);
        try {
            const response = await fetch(`/api/agents/${agentId}/trigger/manual`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ trigger_data: {} })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('Manual trigger successful:', result);
                alert('Agent triggered successfully! Check the execution history for results.');
                setOpenMenuId(null);
            } else {
                const errorData = await response.json();
                console.error('Manual trigger failed:', errorData);
                alert(`Failed to trigger agent: ${(errorData as any)?.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Manual trigger error:', error);
            alert('Failed to trigger agent. Please try again.');
        } finally {
            setTriggerLoading(null);
        }
    };

    const getTriggerIcon = (triggerType: string) => {
        switch (triggerType) {
            case 'cron':
                return <Clock className="w-3 h-3" />;
            case 'webhook':
                return <Zap className="w-3 h-3" />;
            case 'email_imap':
                return <Mail className="w-3 h-3" />;
            default:
                return <Calendar className="w-3 h-3" />;
        }
    };

    const getTriggerLabel = (triggerType: string) => {
        switch (triggerType) {
            case 'cron':
                return 'Timer';
            case 'webhook':
                return 'Webhook';
            case 'email_imap':
                return 'Email';
            default:
                return 'Unknown';
        }
    };

    const canManualTrigger = (agent: Agent) => {
        return agent.triggers && agent.triggers.length > 0;
    };

    const toggleMenu = (agentId: string) => {
        console.log('Toggling menu for agent:', agentId);
        console.log('Current openMenuId:', openMenuId);
        const newMenuId = openMenuId === agentId ? null : agentId;
        setOpenMenuId(newMenuId);
        console.log('New openMenuId:', newMenuId);
    };

    return (
        <div className="min-h-full w-full overflow-y-auto pb-8">
            {/* Header */}
            <div className="mb-8">
                <motion.div 
                    className="flex justify-between items-center"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <div>
                        <h1 className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC] mb-2">
                            🧠 AI Agent Station
                        </h1>
                        <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                            Deploy and manage your intelligent agents
                        </p>
                    </div>
                    <Link href="/dashboard/agents/create">
                        <motion.button
                            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <Plus className="w-4 h-4" />
                            Create Agent
                        </motion.button>
                    </Link>
                </motion.div>
            </div>

            {/* Content */}
            {loading ? (
                <motion.div
                    className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    <div className="flex items-center justify-center space-x-3 py-12">
                        <Loader2 className="animate-spin h-6 w-6 text-[#3B82F6] dark:text-[#8B5CF6]" />
                        <span className="text-[#0F172A] dark:text-[#F8FAFC]">Loading agents...</span>
                    </div>
                </motion.div>
            ) : agents.length === 0 ? (
                <motion.div
                    className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                >
                    <div className="text-center py-12">
                        <h3 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-2">
                            No agents created yet
                        </h3>
                        <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-6">
                            Create your first AI agent to get started with automation
                        </p>
                        <Link href="/dashboard/agents/create">
                            <button className="px-6 py-3 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300">
                                Create Your First Agent
                            </button>
                        </Link>
                    </div>
                </motion.div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-visible">
                    {agents.map((agent, index) => (
                        <motion.div
                            key={agent.id}
                            className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 hover:shadow-lg transition-all duration-300 relative overflow-visible"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
                            whileHover={{ scale: 1.02 }}
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-[#0F172A] dark:text-[#F8FAFC]">
                                    {agent.name}
                                </h3>
                                <div className="flex items-center gap-2">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                        agent.status === 'active' 
                                            ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' 
                                            : 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300'
                                    }`}>
                                        {agent.status || 'active'}
                                    </span>
                                    
                                    {/* Manual trigger button for trigger-enabled agents */}
                                    {canManualTrigger(agent) && (
                                        <button
                                            onClick={() => handleManualTrigger(agent.id)}
                                            disabled={triggerLoading === agent.id}
                                            className="px-2 py-1 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white rounded-full text-xs font-medium hover:shadow-md transition-all duration-300 flex items-center gap-1 disabled:opacity-50"
                                            title="Trigger Agent Manually"
                                        >
                                            {triggerLoading === agent.id ? (
                                                <Loader2 className="w-3 h-3 animate-spin" />
                                            ) : (
                                                <Play className="w-3 h-3" />
                                            )}
                                            Trigger
                                        </button>
                                    )}
                                    
                                    {/* 3-dots menu */}
                                    <div className="relative" ref={openMenuId === agent.id ? menuRef : null}>
                                        <button
                                            onClick={() => toggleMenu(agent.id)}
                                            className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                            aria-label="Agent menu"
                                        >
                                            <MoreVertical className="w-4 h-4 text-gray-500" />
                                        </button>
                                        
                                        <AnimatePresence>
                                            {openMenuId === agent.id && (
                                                <motion.div
                                                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                                                    animate={{ opacity: 1, scale: 1, y: 0 }}
                                                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                                                    transition={{ duration: 0.15 }}
                                                    className="absolute right-0 top-8 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 py-2 z-[100] overflow-visible"
                                                    style={{ 
                                                        transform: 'translateZ(0)',
                                                        minWidth: '192px'
                                                    }}
                                                >
                                                    <Link href={`/dashboard/agents/agent_${agent.id}?agent_id=${agent.id}`}>
                                                        <button className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2">
                                                            <Eye className="w-4 h-4" />
                                                            View Details
                                                        </button>
                                                    </Link>
                                                    
                                                    {canManualTrigger(agent) && (
                                                        <button
                                                            onClick={() => handleManualTrigger(agent.id)}
                                                            disabled={triggerLoading === agent.id}
                                                            className="w-full px-4 py-2 text-left text-sm text-[#3B82F6] dark:text-[#8B5CF6] hover:bg-[#3B82F6]/10 dark:hover:bg-[#8B5CF6]/10 flex items-center gap-2 disabled:opacity-50"
                                                        >
                                                            {triggerLoading === agent.id ? (
                                                                <Loader2 className="w-4 h-4 animate-spin" />
                                                            ) : (
                                                                <Play className="w-4 h-4" />
                                                            )}
                                                            Manual Trigger
                                                        </button>
                                                    )}
                                                    
                                                    <Link href={`/dashboard/agents/${agent.id}/edit`}>
                                                        <button className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2">
                                                            <Edit2 className="w-4 h-4" />
                                                            Edit Agent
                                                        </button>
                                                    </Link>
                                                    
                                                    <hr className="my-1 border-gray-200 dark:border-gray-700" />
                                                    
                                                    <button
                                                        onClick={() => handleDeleteAgent(agent.id)}
                                                        disabled={deleteLoading === agent.id}
                                                        className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center gap-2 disabled:opacity-50 font-medium"
                                                    >
                                                        {deleteLoading === agent.id ? (
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                        ) : (
                                                            <Trash2 className="w-4 h-4" />
                                                        )}
                                                        Delete Agent
                                                    </button>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </div>
                                </div>
                            </div>
                            
                            <p className="text-sm text-[#3B82F6] dark:text-[#8B5CF6] font-medium mb-2">
                                {agent.role}
                            </p>

                            {/* Trigger Information */}
                            {agent.triggers && agent.triggers.length > 0 && (
                                <div className="mb-3">
                                    <div className="text-xs text-[#0F172A]/60 dark:text-[#F8FAFC]/60 mb-1">
                                        Triggers:
                                    </div>
                                    <div className="flex flex-wrap gap-1">
                                        {agent.triggers.map((trigger, idx) => (
                                            <div
                                                key={trigger.id || idx}
                                                className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${
                                                    trigger.is_active
                                                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                                                        : 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300'
                                                }`}
                                            >
                                                {getTriggerIcon(trigger.trigger_type)}
                                                <span>{getTriggerLabel(trigger.trigger_type)}</span>
                                                {!trigger.is_active && (
                                                    <span className="text-red-500 ml-1">●</span>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {agent.description && (
                                <p className="text-sm text-[#0F172A]/60 dark:text-[#F8FAFC]/60 mb-4 line-clamp-2">
                                    {agent.description}
                                </p>
                            )}
                            
                            <Link
                                href={`/dashboard/agents/${agent.id}/chat?agentId=${agent.id}`}
                                className="inline-block text-sm text-[#3B82F6] dark:text-[#8B5CF6] hover:underline font-medium"
                            >
                                Launch Chat →
                            </Link>

                            {canManualTrigger(agent) && (
                                <button
                                    onClick={() => handleManualTrigger(agent.id)}
                                    disabled={triggerLoading === agent.id}
                                    className="inline-flex items-center gap-2 text-sm text-[#3B82F6] dark:text-[#8B5CF6] hover:underline font-medium disabled:opacity-50"
                                >
                                    {triggerLoading === agent.id ? (
                                        <Loader2 className="w-3 h-3 animate-spin" />
                                    ) : (
                                        <Play className="w-3 h-3" />
                                    )}
                                    Trigger Now →
                                </button>
                            )}
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}


