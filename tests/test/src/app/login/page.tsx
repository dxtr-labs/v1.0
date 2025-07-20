
"use client";

import React, { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import AuthLayout from "@/components/auth/AuthLayout";
import { motion, AnimatePresence } from "framer-motion";
import {
  IconBrandGithub,
  IconBrandGoogle,
} from "@tabler/icons-react";
// import Spline from '@splinetool/react-spline/next';
import { useAuth } from '@/hooks/useAuth';
import { Loader2, AlertCircle } from 'lucide-react';

// Login Form Component
export function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const { login, isLoading, error } = useAuth();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!formData.email || !formData.password) return;
    
    // Call login function - no promise handling in Client Component
    login({
      email: formData.email,
      password: formData.password
    });
  };

  return (
    <div className="w-full">
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          className="mb-4 p-3 rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center space-x-2"
        >
          <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
          <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
        </motion.div>
      )}
      
      <form className="space-y-6" onSubmit={handleSubmit}>
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <LabelInputContainer className="mb-4">
            <Label htmlFor="email">Email Address</Label>
            <Input 
              id="email" 
              name="email"
              placeholder="your@email.com" 
              type="email" 
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <LabelInputContainer className="mb-6">
            <Label htmlFor="password">Password</Label>
            <Input 
              id="password" 
              name="password"
              placeholder="••••••••" 
              type="password" 
              value={formData.password}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="group/btn relative block h-12 w-full rounded-md bg-gray-500 dark:bg-gray-600 text-white dark:text-gray-100 font-medium hover:bg-gray-500/90 dark:hover:bg-gray-600/90 transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Signing In...</span>
            </div>
          ) : (
            'Sign In'
          )}
          <BottomGradient />
        </motion.button>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="my-8 h-[1px] w-full bg-gradient-to-r from-transparent via-gray-400/30 dark:via-gray-600/30 to-transparent" 
        />

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col space-y-4"
        >
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="group/btn shadow-lg relative flex h-12 w-full items-center justify-center space-x-2 rounded-md bg-[#F8FAFC] dark:bg-[#0F172A] hover:bg-[#F8FAFC]/80 dark:hover:bg-[#0F172A]/80 px-4 font-medium text-[#0F172A] dark:text-[#F8FAFC] transition-all duration-300 border border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
            type="button"
          >
            <IconBrandGoogle className="h-5 w-5" />
            <span>Continue with Google</span>
            <BottomGradient />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="group/btn shadow-lg relative flex h-12 w-full items-center justify-center space-x-2 rounded-md bg-[#F8FAFC] dark:bg-[#0F172A] hover:bg-[#F8FAFC]/80 dark:hover:bg-[#0F172A]/80 px-4 font-medium text-[#0F172A] dark:text-[#F8FAFC] transition-all duration-300 border border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
            type="button"
          >
            <IconBrandGithub className="h-5 w-5" />
            <span>Continue with GitHub</span>
            <BottomGradient />
          </motion.button>
        </motion.div>
      </form>
    </div>
  );
}

// Signup Form Component (from existing signup page)
export function SignupForm() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    isOrganization: false
  });
  const { signup, isLoading, error } = useAuth();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    console.log('🔄 Signup form submitted with data:', formData);
    
    // Basic validation
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.password) {
      console.log('❌ Form validation failed: Missing required fields');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      console.log('❌ Form validation failed: Password mismatch');
      return;
    }
    
    console.log('✅ Form validation passed, calling signup...');
    
    // Call signup function without promise chains to avoid async issues
    signup({
      email: formData.email,
      password: formData.password,
      firstName: formData.firstName,
      lastName: formData.lastName,
      isOrganization: formData.isOrganization
    });
  };

  return (
    <div className="w-full">
      {error && (
        <motion.div 
          initial={{ opacity: 0, y: -10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          className="mb-4 p-3 rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center space-x-2"
        >
          <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
          <span className="text-sm text-red-600 dark:text-red-400">{error}</span>
        </motion.div>
      )}
      
      <form className="space-y-6" onSubmit={handleSubmit}>
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-4 flex flex-col space-y-2 md:flex-row md:space-y-0 md:space-x-2"
        >
          <LabelInputContainer>
            <Label htmlFor="firstname">First name</Label>
            <Input 
              id="firstname" 
              name="firstName"
              placeholder="Tyler" 
              type="text" 
              value={formData.firstName}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
          <LabelInputContainer>
            <Label htmlFor="lastname">Last name</Label>
            <Input 
              id="lastname" 
              name="lastName"
              placeholder="Durden" 
              type="text" 
              value={formData.lastName}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <LabelInputContainer className="mb-4">
            <Label htmlFor="email">Email Address</Label>
            <Input 
              id="email" 
              name="email"
              placeholder="your@email.com" 
              type="email" 
              value={formData.email}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <LabelInputContainer className="mb-4">
            <Label htmlFor="password">Password</Label>
            <Input 
              id="password" 
              name="password"
              placeholder="••••••••" 
              type="password" 
              value={formData.password}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <LabelInputContainer className="mb-6">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input 
              id="confirmPassword" 
              name="confirmPassword"
              placeholder="••••••••" 
              type="password" 
              value={formData.confirmPassword}
              onChange={handleInputChange}
              required
            />
          </LabelInputContainer>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="group/btn relative block h-12 w-full rounded-md bg-[#3B82F6] dark:bg-[#8B5CF6] text-[#F8FAFC] dark:text-[#0F172A] font-medium hover:bg-[#3B82F6]/90 dark:hover:bg-[#8B5CF6]/90 transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Creating Account...</span>
            </div>
          ) : (
            'Create Account'
          )}
          <BottomGradient />
        </motion.button>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="my-8 h-[1px] w-full bg-gradient-to-r from-transparent via-[#3B82F6]/30 dark:via-[#8B5CF6]/30 to-transparent" 
        />

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex flex-col space-y-4"
        >
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="group/btn shadow-lg relative flex h-12 w-full items-center justify-center space-x-2 rounded-md bg-[#F8FAFC] dark:bg-[#0F172A] hover:bg-[#F8FAFC]/80 dark:hover:bg-[#0F172A]/80 px-4 font-medium text-[#0F172A] dark:text-[#F8FAFC] transition-all duration-300 border border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
            type="button"
          >
            <IconBrandGoogle className="h-5 w-5" />
            <span>Continue with Google</span>
            <BottomGradient />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="group/btn shadow-lg relative flex h-12 w-full items-center justify-center space-x-2 rounded-md bg-[#F8FAFC] dark:bg-[#0F172A] hover:bg-[#F8FAFC]/80 dark:hover:bg-[#0F172A]/80 px-4 font-medium text-[#0F172A] dark:text-[#F8FAFC] transition-all duration-300 border border-[#3B82F6]/30 dark:border-[#8B5CF6]/30"
            type="button"
          >
            <IconBrandGithub className="h-5 w-5" />
            <span>Continue with GitHub</span>
            <BottomGradient />
          </motion.button>
        </motion.div>
      </form>
    </div>
  );
}

const BottomGradient = () => {
  return (
    <>
      <span className="absolute inset-x-0 -bottom-px block h-px w-full bg-gradient-to-r from-transparent via-[#3B82F6] dark:via-[#8B5CF6] to-transparent opacity-0 transition duration-500 group-hover/btn:opacity-100" />
      <span className="absolute inset-x-10 -bottom-px mx-auto block h-px w-1/2 bg-gradient-to-r from-transparent via-[#3B82F6]/60 dark:via-[#8B5CF6]/60 to-transparent opacity-0 blur-sm transition duration-500 group-hover/btn:opacity-100" />
    </>
  );
};

const LabelInputContainer = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <div className={cn("flex w-full flex-col space-y-2", className)}>
      {children}
    </div>
  );
};

export default function LoginPage() {
  const [showSignup, setShowSignup] = useState(false);

  // Enhanced animation variants for the form container
  const containerVariants = {
    login: {
      height: "auto",
      transition: {
        duration: 0.6,
        ease: [0.4, 0.0, 0.2, 1],
        when: "beforeChildren"
      }
    },
    signup: {
      height: "auto", 
      transition: {
        duration: 0.6,
        ease: [0.4, 0.0, 0.2, 1],
        when: "beforeChildren"
      }
    }
  };

  // Content animation variants
  const contentVariants = {
    hidden: {
      opacity: 0,
      y: 20,
      scale: 0.95,
      filter: "blur(10px)"
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      filter: "blur(0px)",
      transition: {
        duration: 0.5,
        ease: [0.4, 0.0, 0.2, 1],
        staggerChildren: 0.1
      }
    },
    exit: {
      opacity: 0,
      y: -20,
      scale: 0.95,
      filter: "blur(10px)",
      transition: {
        duration: 0.3,
        ease: [0.4, 0.0, 1, 1]
      }
    }
  };

  // Form field animation variants
  const fieldVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.3 }
    }
  };

  return (
    <AuthLayout 
      leftContent={
        <div className="w-full h-[600px] rounded-2xl overflow-hidden shadow-2xl bg-[#F8FAFC]/10 dark:bg-[#0F172A]/10 backdrop-blur-xl border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 flex items-center justify-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            className="text-center"
          >
            {/* DXTR Labs Logo with Dynamic Color Fill */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="relative"
            >
              <svg
                width="280"
                height="120"
                viewBox="0 0 280 120"
                className="mx-auto"
                xmlns="http://www.w3.org/2000/svg"
              >
                {/* Background glow effect */}
                <defs>
                  <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#3B82F6" className="dark:stop-color-[#8B5CF6]">
                      <animate attributeName="stop-color" 
                        values="#3B82F6;#0F172A;#3B82F6;#F8FAFC;#3B82F6" 
                        dur="8s" 
                        repeatCount="indefinite"
                        className="dark:hidden" />
                      <animate attributeName="stop-color" 
                        values="#8B5CF6;#F8FAFC;#8B5CF6;#0F172A;#8B5CF6" 
                        dur="8s" 
                        repeatCount="indefinite"
                        className="hidden dark:inline" />
                    </stop>
                    <stop offset="50%" stopColor="#F8FAFC" className="dark:stop-color-[#0F172A]">
                      <animate attributeName="stop-color" 
                        values="#F8FAFC;#3B82F6;#0F172A;#3B82F6;#F8FAFC" 
                        dur="8s" 
                        repeatCount="indefinite"
                        className="dark:hidden" />
                      <animate attributeName="stop-color" 
                        values="#0F172A;#8B5CF6;#F8FAFC;#8B5CF6;#0F172A" 
                        dur="8s" 
                        repeatCount="indefinite"
                        className="hidden dark:inline" />
                    </stop>
                    <stop offset="100%" stopColor="#0F172A" className="dark:stop-color-[#F8FAFC]">
                      <animate attributeName="stop-color" 
                        values="#0F172A;#F8FAFC;#3B82F6;#F8FAFC;#0F172A" 
                        dur="8s" 
                        repeatCount="indefinite"
                        className="dark:hidden" />
                      <animate attributeName="stop-color" 
                        values="#F8FAFC;#0F172A;#8B5CF6;#0F172A;#F8FAFC" 
                        dur="8s" 
                        repeatCount="indefinite"
                        className="hidden dark:inline" />
                    </stop>
                  </linearGradient>
                  
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                    <feMerge> 
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>

                {/* DXTR Text with white outline */}
                <text
                  x="140"
                  y="50"
                  textAnchor="middle"
                  className="text-4xl font-black tracking-wider"
                  fill="url(#logoGradient)"
                  filter="url(#glow)"
                  stroke="white"
                  strokeWidth="1"
                  style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                >
                  DXTR
                </text>

                {/* Labs Text with white outline */}
                <text
                  x="140"
                  y="85"
                  textAnchor="middle"
                  className="text-xl font-medium tracking-widest"
                  fill="url(#logoGradient)"
                  stroke="white"
                  strokeWidth="0.5"
                  opacity="0.9"
                  style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}
                >
                  LABS
                </text>
              </svg>
            </motion.div>

            {/* Animated tagline */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1, duration: 0.8 }}
              className="mt-6 text-lg font-medium text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
            >
              Accelerating Digital Transformation
            </motion.p>

            {/* Floating particles effect with landing page colors */}
            <div className="absolute inset-0 pointer-events-none">
              {[...Array(6)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 rounded-full bg-gradient-to-r from-[#3B82F6] to-[#F8FAFC] dark:from-[#8B5CF6] dark:to-[#0F172A] opacity-30"
                  initial={{ 
                    x: Math.random() * 280, 
                    y: Math.random() * 120,
                    scale: 0 
                  }}
                  animate={{
                    y: [null, -20, 20],
                    opacity: [0.3, 0.8, 0.3],
                    scale: [0, 1, 0]
                  }}
                  transition={{
                    duration: 3 + i,
                    repeat: Infinity,
                    delay: i * 0.5
                  }}
                />
              ))}
            </div>
          </motion.div>
        </div>
      }
    >
      {/* Animated Container with morphing effect */}
      <motion.div
        layout
        variants={containerVariants}
        animate={showSignup ? "signup" : "login"}
        className="w-full max-w-md mx-auto"
      >
        <AnimatePresence mode="wait" initial={false}>
          {!showSignup ? (
            <motion.div
              key="login"
              variants={contentVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              layout
            >
              <motion.div 
                className="text-center mb-8"
                variants={fieldVariants}
              >
                <motion.h1 
                  className="text-3xl font-bold mb-2 text-[#0F172A] dark:text-[#F8FAFC]"
                  variants={fieldVariants}
                >
                  Welcome Back
                </motion.h1>
                <motion.p 
                  className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
                  variants={fieldVariants}
                >
                  Sign in to your account
                </motion.p>
              </motion.div>
              
              <motion.div variants={fieldVariants}>
                <LoginForm />
              </motion.div>
              
              <motion.button
                onClick={() => setShowSignup(true)}
                className="mt-6 w-full text-center text-[#0F172A] dark:text-[#F8FAFC] hover:text-[#3B82F6] dark:hover:text-[#8B5CF6] transition-colors"
                whileHover={{ 
                  scale: 1.02,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ 
                  scale: 0.98,
                  transition: { duration: 0.1 }
                }}
                variants={fieldVariants}
              >
                Don&apos;t have an account? <span className="font-semibold underline">Create Account</span>
              </motion.button>
            </motion.div>
          ) : (
            <motion.div
              key="signup"
              variants={contentVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              layout
            >
              <motion.div 
                className="text-center mb-8"
                variants={fieldVariants}
              >
                <motion.h1 
                  className="text-3xl font-bold mb-2 text-[#0F172A] dark:text-[#F8FAFC]"
                  variants={fieldVariants}
                >
                  Create Account
                </motion.h1>
                <motion.p 
                  className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70"
                  variants={fieldVariants}
                >
                  Join DevLabs to start automating your workflows
                </motion.p>
              </motion.div>
              
              <motion.div variants={fieldVariants}>
                <SignupForm />
              </motion.div>
              
              <motion.button
                onClick={() => setShowSignup(false)}
                className="mt-6 w-full text-center text-[#0F172A] dark:text-[#F8FAFC] hover:text-[#3B82F6] dark:hover:text-[#8B5CF6] transition-colors"
                whileHover={{ 
                  scale: 1.02,
                  transition: { duration: 0.2 }
                }}
                whileTap={{ 
                  scale: 0.98,
                  transition: { duration: 0.1 }
                }}
                variants={fieldVariants}
              >
                Already have an account? <span className="font-semibold underline">Sign In</span>
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </AuthLayout>
  );
}


