'use client';

import React from 'react';
import { motion } from 'framer-motion';

export default function SettingsPage() {
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
          Settings
        </motion.h1>
        <motion.p 
          className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          Configure your account and preferences
        </motion.p>
      </div>

      {/* Content */}
      <motion.div
        className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <p className="text-[#0F172A] dark:text-[#F8FAFC] text-center py-12">
          Settings features coming soon...
        </p>
      </motion.div>
    </div>
  );
}



