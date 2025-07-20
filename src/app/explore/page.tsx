'use client';

import { motion } from "framer-motion";
import Link from "next/link";
import ScrollBackground from "../components/ui/scroll";

export default function ExplorePage() {
  return (
    <>
      <ScrollBackground />
      
      <div className="relative mx-auto min-h-screen flex max-w-7xl flex-col items-center justify-center p-4">
        
        {/* Navigation */}
        <nav className="absolute top-0 left-0 right-0 flex w-full items-center justify-between border-b border-neutral-200 px-4 py-4 dark:border-neutral-800">
          <div className="flex items-center gap-2">
            <div className="size-7 rounded-full bg-gradient-to-br from-violet-500 to-pink-500" />
            <h1 className="text-base font-bold md:text-2xl font-sf">DXTR LABS</h1>
          </div>
          <div className="flex gap-4">
            <Link href="/" passHref legacyBehavior>
              <a className="w-24 transform rounded-lg border border-gray-300 bg-white px-6 py-2 text-center font-medium text-black transition-all duration-300 hover:-translate-y-0.5 hover:bg-gray-100 md:w-32 dark:border-gray-700 dark:bg-black dark:text-white dark:hover:bg-gray-900 font-sf">
                Home
              </a>
            </Link>
            <Link href="/automation" passHref legacyBehavior>
              <a className="w-24 transform rounded-lg border border-gray-300 bg-white px-6 py-2 text-center font-medium text-black transition-all duration-300 hover:-translate-y-0.5 hover:bg-gray-100 md:w-32 dark:border-gray-700 dark:bg-black dark:text-white dark:hover:bg-gray-900 font-sf">
                Automation
              </a>
            </Link>
            <Link href="/chat" passHref legacyBehavior>
              <a className="w-24 transform rounded-lg bg-black px-6 py-2 text-center font-medium text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-gray-800 md:w-32 dark:bg-white dark:text-black dark:hover:bg-gray-200 font-sf">
                Chat
              </a>
            </Link>
          </div>
        </nav>

        {/* Main Content */}
        <div className="flex flex-col items-center justify-center text-center">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-4xl md:text-6xl lg:text-8xl font-bold text-black mb-8 dark:text-white"
          >
            Explore
          </motion.h1>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-black/80 mb-12 max-w-2xl dark:text-white/80"
          >
            Discover the power of automation. Browse through our features and see how AI can transform your workflow.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl"
          >
            {/* Feature Cards */}
            <Link href="/automation" passHref legacyBehavior>
              <a className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-white/30 hover:bg-white/30 transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-3xl mb-4">🤖</div>
                <h3 className="text-xl font-bold text-black mb-2 dark:text-white">AI Automation</h3>
                <p className="text-black/70 dark:text-white/70">
                  Intelligent automation powered by advanced AI algorithms
                </p>
              </a>
            </Link>

            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-white/30">
              <div className="text-3xl mb-4">💬</div>
              <h3 className="text-xl font-bold text-black mb-2 dark:text-white">Chat Interface</h3>
              <p className="text-black/70 dark:text-white/70">
                Natural language interface for seamless interaction
              </p>
            </div>

            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-white/30">
              <div className="text-3xl mb-4">⚡</div>
              <h3 className="text-xl font-bold text-black mb-2 dark:text-white">Fast Processing</h3>
              <p className="text-black/70 dark:text-white/70">
                Lightning-fast response times and execution
              </p>
            </div>

            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-white/30">
              <div className="text-3xl mb-4">🔧</div>
              <h3 className="text-xl font-bold text-black mb-2 dark:text-white">Custom Workflows</h3>
              <p className="text-black/70 dark:text-white/70">
                Build personalized automation workflows
              </p>
            </div>

            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-white/30">
              <div className="text-3xl mb-4">📊</div>
              <h3 className="text-xl font-bold text-black mb-2 dark:text-white">Analytics</h3>
              <p className="text-black/70 dark:text-white/70">
                Detailed insights and performance metrics
              </p>
            </div>

            <div className="bg-white/20 backdrop-blur-lg rounded-2xl p-6 shadow-lg border border-white/30">
              <div className="text-3xl mb-4">🔒</div>
              <h3 className="text-xl font-bold text-black mb-2 dark:text-white">Secure</h3>
              <p className="text-black/70 dark:text-white/70">
                Enterprise-grade security and privacy
              </p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="mt-12"
          >
            <Link href="/chat" passHref legacyBehavior>
              <a className="font-sf px-8 py-4 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-300 text-lg font-medium">
                Get Started
              </a>
            </Link>
          </motion.div>
        </div>
      </div>
    </>
  );
}
