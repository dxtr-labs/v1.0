'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface CreditTransaction {
    type: string;
    amount: number;
    description: string;
    timestamp: string;
}

interface CreditData {
    credits: number;
    transactions: CreditTransaction[];
}

export default function CreditsPage() {
    const [creditData, setCreditData] = useState<CreditData | null>(null);
    const [loading, setLoading] = useState(true);
    const [refilling, setRefilling] = useState(false);

    useEffect(() => {
        fetchCreditData();
    }, []);

    const fetchCreditData = () => {
        fetch("/api/credits/history", { credentials: 'include' })
            .then((res) => res.json())
            .then((data: any) => {
                setCreditData(data as CreditData);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    const handleRefill = async () => {
        setRefilling(true);
        try {
            await fetch('/api/credits/refill', { 
                method: 'POST', 
                credentials: 'include' 
            });
            await fetchCreditData(); // Refresh data
        } catch (error) {
            console.error('Refill failed:', error);
        }
        setRefilling(false);
    };

    return (
        <div className="h-full w-full">
            {/* Header */}
            <div className="mb-8">
                <motion.h1 
                    className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC] mb-2"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    💰 Credits
                </motion.h1>
                <motion.p 
                    className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                >
                    Manage your DXTR Labs credit balance and transaction history
                </motion.p>
            </div>

            {loading ? (
                <motion.div
                    className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    <div className="flex items-center justify-center space-x-3 py-12">
                        <Loader2 className="animate-spin h-6 w-6 text-[#3B82F6] dark:text-[#8B5CF6]" />
                        <span className="text-[#0F172A] dark:text-[#F8FAFC]">Loading credit information...</span>
                    </div>
                </motion.div>
            ) : creditData ? (
                <>
                    {/* Credit Balance Card */}
                    <motion.div
                        className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 mb-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h2 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-2">
                                    Current Balance
                                </h2>
                                <p className="text-3xl font-bold text-[#3B82F6] dark:text-[#8B5CF6]">
                                    {creditData.credits.toLocaleString()} credits
                                </p>
                            </div>
                            <motion.button
                                onClick={handleRefill}
                                disabled={refilling}
                                className="px-6 py-3 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white rounded-lg font-medium hover:shadow-lg transition-all duration-300 disabled:opacity-50"
                                whileHover={{ scale: refilling ? 1 : 1.05 }}
                                whileTap={{ scale: refilling ? 1 : 0.95 }}
                            >
                                {refilling ? (
                                    <div className="flex items-center gap-2">
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Adding...
                                    </div>
                                ) : (
                                    '+ Add 100 Credits'
                                )}
                            </motion.button>
                        </div>
                        <div className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                            Credits are used for API calls, agent executions, and automation workflows
                        </div>
                    </motion.div>

                    {/* Transaction History */}
                    <motion.div
                        className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                    >
                        <h2 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">
                            Recent Transactions
                        </h2>
                        <div className="space-y-3">
                            {creditData.transactions.slice(0, 10).map((txn, index) => (
                                <motion.div
                                    key={index}
                                    className="flex items-center justify-between py-3 border-b border-[#3B82F6]/10 dark:border-[#8B5CF6]/10 last:border-b-0"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.3, delay: 0.4 + index * 0.05 }}
                                >
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                                txn.type === 'Refill' 
                                                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' 
                                                    : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                                            }`}>
                                                {txn.type}
                                            </span>
                                        </div>
                                        <p className="text-sm text-[#0F172A] dark:text-[#F8FAFC] font-medium">
                                            {txn.description}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className={`font-semibold ${
                                            txn.amount > 0 
                                                ? 'text-green-600 dark:text-green-400' 
                                                : 'text-red-600 dark:text-red-400'
                                        }`}>
                                            {txn.amount > 0 ? '+' : ''}{txn.amount} credits
                                        </p>
                                        <p className="text-xs text-[#0F172A]/50 dark:text-[#F8FAFC]/50">
                                            {new Date(txn.timestamp).toLocaleString()}
                                        </p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </>
            ) : (
                <motion.div
                    className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                >
                    <p className="text-red-500 dark:text-red-400 text-center py-12">
                        Failed to load credit data. Please try again later.
                    </p>
                </motion.div>
            )}
        </div>
    );
}



