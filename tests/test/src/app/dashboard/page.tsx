'use client';

import React from 'react';
import { motion } from 'framer-motion';

export default function DashboardPage() {
  return (
    <div className="h-full w-full">
      {/* Dashboard Header */}
      <div className="mb-8">
        <motion.h1 
          className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC] mb-2"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Dashboard
        </motion.h1>
        <motion.p 
          className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          Welcome to your DXTR Labs automation workspace
        </motion.p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { title: "Active Agents", value: "3", change: "+12%" },
          { title: "Credits Used", value: "1,234", change: "+8%" },
          { title: "Workflows", value: "12", change: "+4%" },
          { title: "Success Rate", value: "98.5%", change: "+2%" },
        ].map((stat, index) => (
          <motion.div
            key={index}
            className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <h3 className="text-sm font-medium text-[#0F172A]/70 dark:text-[#F8FAFC]/70 mb-2">
              {stat.title}
            </h3>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">
                {stat.value}
              </span>
              <span className="text-sm text-[#3B82F6] dark:text-[#8B5CF6] font-medium">
                {stat.change}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recent Activity */}
      <motion.div
        className="p-6 rounded-lg bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-sm border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <h2 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">
          Recent Activity
        </h2>
        <div className="space-y-3">
          {[
            { action: "Workflow completed", target: "Customer Onboarding", time: "2 minutes ago" },
            { action: "Agent deployed", target: "Email Assistant", time: "15 minutes ago" },
            { action: "Credits refilled", target: "500 credits", time: "1 hour ago" },
            { action: "Automation started", target: "Data Processing", time: "2 hours ago" },
          ].map((activity, index) => (
            <div 
              key={index}
              className="flex items-center justify-between py-3 border-b border-[#3B82F6]/10 dark:border-[#8B5CF6]/10 last:border-b-0"
            >
              <div>
                <p className="text-[#0F172A] dark:text-[#F8FAFC] font-medium">
                  {activity.action}
                </p>
                <p className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                  {activity.target}
                </p>
              </div>
              <span className="text-sm text-[#3B82F6] dark:text-[#8B5CF6]">
                {activity.time}
              </span>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}



