
import React from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '@/contexts/ThemeContext';

interface AuthLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  leftContent?: React.ReactNode;
}

const AuthLayout = ({ children, title, subtitle, leftContent }: AuthLayoutProps) => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <div className={`min-h-screen w-full flex items-center justify-center p-4 relative bg-[#F8FAFC] dark:bg-[#0F172A] transition-colors duration-300`}>
      {/* Theme Toggle Button */}
      <button 
        onClick={toggleTheme}
        className="fixed top-4 right-4 w-12 h-12 rounded-full bg-[#3B82F6] dark:bg-[#8B5CF6] flex items-center justify-center hover:opacity-80 transition-all duration-300 z-50 shadow-lg"
      >
        <div className="relative w-6 h-6">
          <div className={`absolute inset-0 transform transition-all duration-500 ${isDarkMode ? 'scale-100 rotate-[360deg]' : 'scale-0 rotate-0'}`}>
            <div className="w-5 h-5 rounded-full bg-[#F8FAFC] dark:bg-[#0F172A]" />
            <div className="absolute bottom-1 right-1 w-2 h-2 rounded-full bg-[#0F172A] dark:bg-[#F8FAFC]" />
          </div>
          <div className={`absolute inset-0 transform transition-all duration-500 ${!isDarkMode ? 'scale-100 rotate-0' : 'scale-0 rotate-[-360deg]'}`}>
            <div className="w-5 h-5 rounded-full bg-[#F8FAFC] dark:bg-[#0F172A]" />
          </div>
        </div>
      </button>

      {/* Main Content Container */}
      <div className="relative z-10 w-full max-w-7xl mx-auto flex items-center justify-center min-h-screen">
        {leftContent && (
          <div className="hidden lg:flex lg:w-1/2 items-center justify-center p-8">
            <motion.div 
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="w-full max-w-lg"
            >
              {leftContent}
            </motion.div>
          </div>
        )}
        
        {/* Form Content */}
        <div className={`w-full ${leftContent ? 'lg:w-1/2 lg:pl-8' : 'max-w-md mx-auto'} flex items-center justify-center`}>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: leftContent ? 0.3 : 0 }}
            className={`w-full max-w-md p-8 rounded-2xl shadow-2xl bg-white dark:bg-[#0F172A] text-[#0F172A] dark:text-white border border-[#0F172A]/10 dark:border-white/10`}
          >
            {title && (
              <div className="relative mb-6">
                <motion.h1 
                  className="text-3xl font-bold mb-2 text-[#0F172A] dark:text-white"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: leftContent ? 0.5 : 0.2 }}
                >
                  {title}
                </motion.h1>
                {subtitle && (
                  <motion.p 
                    className="text-[#0F172A]/70 dark:text-white/80"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: leftContent ? 0.6 : 0.3 }}
                  >
                    {subtitle}
                  </motion.p>
                )}
              </div>
            )}
            {children}
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;



