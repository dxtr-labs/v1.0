"use client"

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Bot, MessageSquare, Mic, Zap, Shield, Users, TrendingUp, ChevronRight, Play, Workflow, Database, Sparkles } from 'lucide-react'
import { IconHome } from '@tabler/icons-react'
import Link from 'next/link'
import Image from 'next/image'
import Button from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Spotlight } from '@/components/ui/spotlight'
import { FloatingNav } from '@/components/ui/floating-navbar'
import BackgroundGradient from '@/components/ui/background-gradient'
import { Carousel, Cards } from '@/components/ui/apple-card'
import { AnimatedTestimonials } from '@/components/ui/animated-testimonials'

// Types for carousel data
interface CarouselItem {
  category: string;
  title: string;
  src: string;
  content: React.ReactNode;
}

export default function AutomationLandingPage() {
  const mainBgClass = "min-h-screen bg-gradient-to-br from-slate-50 to-gray-100 dark:from-slate-900 dark:to-slate-800 transition-colors duration-300";
  const [isDark, setIsDark] = useState(false);

  // ThemeToggle Component
  const ThemeToggle = ({ isDark, onToggle }: { isDark: boolean; onToggle: () => void }) => {
    return (
      <button 
        onClick={onToggle}
        className="fixed top-4 right-4 w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 dark:from-purple-600 dark:to-blue-600 flex items-center justify-center hover:from-blue-700 hover:to-purple-700 dark:hover:from-purple-700 dark:hover:to-blue-700 transition-all duration-300 z-50 shadow-lg hover:shadow-xl"
      >
        <div className="relative w-6 h-6">
          <div className={`absolute inset-0 transform transition-all duration-500 ${isDark ? 'scale-100 rotate-[360deg]' : 'scale-0 rotate-0'}`}>
            <div className="w-5 h-5 rounded-full bg-yellow-300" />
            <div className="absolute bottom-1 right-1 w-2 h-2 rounded-full bg-orange-400" />
          </div>
          <div className={`absolute inset-0 transform transition-all duration-500 ${!isDark ? 'scale-100 rotate-0' : 'scale-0 rotate-[-360deg]'}`}>
            <div className="w-5 h-5 rounded-full bg-blue-100" />
          </div>
        </div>
      </button>
    );
  };

  const testimonials = [
    {
      quote:
        "The attention to detail and innovative features have completely transformed our workflow. This is exactly what we've been looking for.",
      name: "Sarah Chen",
      designation: "Product Manager at TechFlow",
      src: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?q=80&w=3560&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    },
    {
      quote:
        "Implementation was seamless and the results exceeded our expectations. The platform's flexibility is remarkable.",
      name: "Michael Rodriguez",
      designation: "CTO at InnovateSphere",
      src: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    },
    {
      quote:
        "This solution has significantly improved our team's productivity. The intuitive interface makes complex tasks simple.",
      name: "Emily Watson",
      designation: "Operations Director at CloudScale",
      src: "https://images.unsplash.com/photo-1623582854588-d60de57fa33f?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    },
    {
      quote:
        "Outstanding support and robust features. It's rare to find a product that delivers on all its promises.",
      name: "James Kim",
      designation: "Engineering Lead at DataPro",
      src: "https://images.unsplash.com/photo-1636041293178-808a6762ab39?q=80&w=3464&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    },
    {
      quote:
        "The scalability and performance have been game-changing for our organization. Highly recommend to any growing business.",
      name: "Lisa Thompson",
      designation: "VP of Technology at FutureNet",
      src: "https://images.unsplash.com/photo-1624561172888-ac93c696e10c?q=80&w=2592&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    },
  ];

  // DummyContent Component
  const DummyContent = () => {
    return (
      <>
        {[...new Array(3).fill(1)].map((_, index) => {
          return (
            <div
              key={"dummy-content" + index}
              className="bg-[#F5F5F7] dark:bg-neutral-800 p-8 md:p-14 rounded-3xl mb-4"
            >
              <p className="text-neutral-600 dark:text-neutral-400 text-base md:text-2xl font-sans max-w-3xl mx-auto">
                <span className="font-bold text-neutral-700 dark:text-neutral-200">
                  The future of automation is conversational.
                </span>{" "}
                Create complex workflows through natural dialogue, deploy AI agents,
                and monitor their performance in real-time. Our platform transforms
                your ideas into powerful automation solutions.
              </p>
              <Image
                src="https://assets.aceternity.com/demos/default.png"
                alt="Automation platform demo"
                width={500}
                height={500}
                className="md:w-1/2 md:h-1/2 h-full w-full mx-auto object-contain"
              />
            </div>
          );
        })}
      </>
    );
  };

  const data: CarouselItem[] = [
    {
      category: "AI Automation",
      title: "Create powerful workflows with AI",
      src: "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?q=80&w=3556&auto=format&fit=crop&ixlib=rb-4.0.3",
      content: <DummyContent />,
    },
    {
      category: "Productivity",
      title: "Streamline your business processes",
      src: "https://images.unsplash.com/photo-1531554694128-c4c6665f59c2?q=80&w=3387&auto=format&fit=crop&ixlib=rb-4.0.3",
      content: <DummyContent />,
    },
    {
      category: "Integration",
      title: "Seamless n8n workflow deployment",
      src: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3",
      content: <DummyContent />,
    },
    {
      category: "Analytics",
      title: "Real-time performance monitoring",
      src: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3",
      content: <DummyContent />,
    },
    {
      category: "Security",
      title: "Enterprise-grade security built-in",
      src: "https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3",
      content: <DummyContent />,
    },
    {
      category: "Support",
      title: "24/7 Expert assistance",
      src: "https://images.unsplash.com/photo-1521791136064-7986c2920216?q=80&w=3540&auto=format&fit=crop&ixlib=rb-4.0.3",
      content: <DummyContent />,
    },
  ];

  // Navigation items
  const navItems = [
    {
      name: "Home",
      link: "/",
      icon: <IconHome className="h-4 w-4 text-neutral-500 dark:text-white" />,
    },
    {
      name: "Features",
      link: "/features",
      icon: <Zap className="h-4 w-4 text-neutral-500 dark:text-white" />,
    },
    {
      name: "Demo",
      link: "/demo",
      icon: <Play className="h-4 w-4 text-neutral-500 dark:text-white" />,
    },
    {
      name: "Contact",
      link: "/contact",
      icon: <Users className="h-4 w-4 text-neutral-500 dark:text-white" />,
    },
  ];

  React.useEffect(() => {
    // Ensure DOM is available before manipulating it
    const handleThemeInitialization = () => {
      try {
        // Check for system dark mode preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          setIsDark(true);
          if (document.documentElement) {
            document.documentElement.classList.add('dark');
          }
        }

        // Listen for system theme changes
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleChange = (e: MediaQueryListEvent) => {
          setIsDark(e.matches);
          if (document.documentElement) {
            if (e.matches) {
              document.documentElement.classList.add('dark');
            } else {
              document.documentElement.classList.remove('dark');
            }
          }
        };
        
        try {
          // Modern browsers
          mediaQuery.addEventListener('change', handleChange);
          return () => mediaQuery.removeEventListener('change', handleChange);
        } catch (e) {
          // Fallback for older browsers
          mediaQuery.addListener(handleChange);
          return () => mediaQuery.removeListener(handleChange);
        }
      } catch (error) {
        console.error('Theme initialization failed:', error);
      }
    };

    // Run after DOM is ready
    if (typeof window !== 'undefined' && document.documentElement) {
      return handleThemeInitialization();
    }
  }, []);
  
  const toggleTheme = React.useCallback(() => {
    setIsDark(prevDark => {
      const newTheme = !prevDark;
      // Ensure DOM is available before manipulating it
      if (typeof window !== 'undefined' && document.documentElement) {
        if (newTheme) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      }
      return newTheme;
    });
  }, []);

  return (
    <div className={`font-['Open_Sans'] ${isDark ? 'dark' : ''}`}>
      <div className={`relative w-full ${mainBgClass}`}>
        <ThemeToggle isDark={isDark} onToggle={toggleTheme} />
        
        <FloatingNav navItems={navItems} />
        
        {/* Spotlight Effects */}
        <Spotlight
          className="-top-40 left-0 md:left-60 md:-top-20"
          fill={isDark ? "#8B5CF6" : "#3B82F6"}
        />
        
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center py-20 lg:py-32 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto w-full">
            <div className="text-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Badge className="mb-6 bg-gray-500 dark:bg-gray-600 text-white dark:text-gray-100 px-4 py-2 text-sm font-medium">
                  🚀 The Future of Work Automation
                </Badge>
                
                <h1 className="text-4xl lg:text-7xl font-bold mb-8 text-[#0F172A] dark:text-gray-100">
                  Create AI Agents with
                  <br />
                  <span className="text-[#3B82F6] dark:text-[#8B5CF6]">Natural Conversation</span>
                </h1>
                
                <p className="text-xl lg:text-2xl text-[#0F172A]/80 dark:text-gray-100/90 max-w-4xl mx-auto mb-12 leading-relaxed">
                  Deploy intelligent AI agents through simple chat or voice commands. 
                  Automate routine tasks while empowering your human workforce to focus on 
                  creative and strategic work.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
                  <Link href="/signup">
                    <Button size="lg" className="text-lg px-8 py-4 h-auto !bg-gradient-to-r !from-blue-600 !to-purple-600 !text-white hover:!from-blue-700 hover:!to-purple-700 hover:scale-105 transition-all duration-300 border-0 shadow-lg">
                      Start Creating Agents
                      <ChevronRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                  <Button variant="secondary" size="lg" className="text-lg px-8 py-4 h-auto border-2 border-blue-500 dark:border-purple-500 text-blue-600 dark:text-purple-400 bg-transparent hover:bg-blue-50 dark:hover:bg-purple-950/20 hover:scale-105 transition-all duration-300">
                    <Play className="mr-2 h-5 w-5" />
                    Watch Demo
                  </Button>
                </div>
              </motion.div>

              {/* 3D Hero Visual */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 1, delay: 0.2 }}
                className="relative"
              >
                <BackgroundGradient className="rounded-2xl overflow-hidden">
                  <div className="relative w-full" style={{ paddingTop: '56.25%' }}> {/* 16:9 Aspect Ratio */}
                    <iframe 
                      className="absolute top-0 left-0 w-full h-full"
                      src="https://www.youtube.com/embed/FXyEMAgtKok?si=vs3n1h9oFN7vBf1q&amp;start=48"  
                      title="YouTube video player" 
                      frameBorder="0"
                      style={{ border: 'none' }}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                      referrerPolicy="strict-origin-when-cross-origin" 
                      allowFullScreen
                    ></iframe>
                  </div>
                </BackgroundGradient>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Carousel items={data} initialScroll={0}>
              {(item: CarouselItem, index: number) => (
                <div className="relative h-full w-full">
                  <Cards card={item} index={index} />
                </div>
              )}
            </Carousel>
          </div>
        </section>

{/* Testimonials Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <AnimatedTestimonials testimonials={testimonials} />
          </div>
        </section>

        {/* Stats Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto text-center">
            <div className="grid md:grid-cols-4 gap-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl lg:text-6xl font-bold text-[#3B82F6] dark:text-[#8B5CF6] mb-2">5</div>
                <div className="text-[#0F172A]/70 dark:text-gray-100/70 text-lg">AI Processing Rounds</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl lg:text-6xl font-bold text-[#3B82F6] dark:text-[#8B5CF6] mb-2">9+</div>
                <div className="text-[#0F172A]/70 dark:text-gray-100/70 text-lg">Supported Node Types</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl lg:text-6xl font-bold text-[#3B82F6] dark:text-[#8B5CF6] mb-2">90%</div>
                <div className="text-[#0F172A]/70 dark:text-gray-100/70 text-lg">Faster Deployment</div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                viewport={{ once: true }}
              >
                <div className="text-4xl lg:text-6xl font-bold text-[#3B82F6] dark:text-[#8B5CF6] mb-2">100%</div>
                <div className="text-[#0F172A]/70 dark:text-gray-100/70 text-lg">N8N Compatible</div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section id="automation" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-600 via-purple-600 to-emerald-600 dark:from-purple-900 dark:via-blue-900 dark:to-emerald-900">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
                Ready to Automate with AI?
              </h2>
              <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
                Join the future of workflow automation. Create enterprise-grade n8n workflows 
                through simple conversation - no coding required.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/automation">
                  <Button size="lg" variant="secondary" className="text-lg px-8 py-4 h-auto bg-[#0F172A] dark:bg-gray-100 text-gray-100 dark:text-[#0F172A] hover:bg-[#0F172A]/90 dark:hover:bg-gray-100/90 hover:scale-105 transition-all duration-300">
                    <Workflow className="mr-2 h-5 w-5" />
                    Start Automating Now
                    <TrendingUp className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button size="lg" variant="secondary" className="text-lg px-8 py-4 h-auto border-2 border-[#0F172A] dark:border-gray-100 text-[#0F172A] dark:text-gray-100 hover:bg-[#0F172A]/10 dark:hover:bg-gray-100/10 hover:scale-105 transition-all duration-300">
                    Get Full Access
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
    </div>
  )
}


