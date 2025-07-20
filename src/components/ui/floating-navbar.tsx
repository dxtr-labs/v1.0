"use client";
import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "@/lib/utils";


export const FloatingNav = ({
  navItems,
  className,
}: {
  navItems: {
    name: string;
    link: string;
    icon?: JSX.Element;
  }[];
  className?: string;
}) => {
  // No scroll logic needed for always visible navbar

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className={cn(
          "flex flex-col fixed top-1/2 -translate-y-1/2 right-0 border-l border-[#3B82F6]/30 dark:border-[#8B5CF6]/30 rounded-l-2xl bg-white/90 dark:bg-black/90 backdrop-blur-xl shadow-[0_0_15px_rgba(107,114,128,0.15)] dark:shadow-[0_0_15px_rgba(156,163,175,0.15)] z-[5000] py-3 px-2 items-center justify-center space-y-2",
          className
        )}
      >
        {navItems.map((navItem: any, idx: number) => (
          <a
            key={`link=${idx}`}
            href={navItem.link}
            className={cn(
              "relative group dark:text-[#8B5CF6] items-center flex text-[#3B82F6] dark:hover:text-[#8B5CF6]/80 hover:text-[#3B82F6]/80 transition-colors"
            )}
          >
            <div className="relative flex items-center">
              <span className="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-[#3B82F6]/10 dark:hover:bg-[#8B5CF6]/10 transition-all duration-300">
                {navItem.icon}
              </span>
              <span className="absolute left-full ml-2 px-2 py-1 rounded-md bg-white/95 dark:bg-black/95 border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 shadow-lg opacity-0 invisible -translate-x-2 group-hover:opacity-100 group-hover:visible group-hover:translate-x-0 transition-all duration-300 whitespace-nowrap text-sm font-medium min-w-[60px]">
                {navItem.name}
              </span>
            </div>
          </a>
        ))}
        <button className="group relative">
          <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-[#3B82F6] dark:bg-[#8B5CF6] text-white hover:bg-[#3B82F6]/90 dark:hover:bg-[#8B5CF6]/90 transition-all duration-300">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </span>
          <span className="absolute left-full ml-2 px-2 py-1 rounded-md bg-white/95 dark:bg-black/95 border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 shadow-lg text-[#3B82F6] dark:text-[#8B5CF6] opacity-0 invisible -translate-x-2 group-hover:opacity-100 group-hover:visible group-hover:translate-x-0 transition-all duration-300 whitespace-nowrap text-sm font-medium">
            Login
          </span>
        </button>
      </motion.div>
    </AnimatePresence>
  );
};

