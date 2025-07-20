'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar, SidebarBody, SidebarLink } from '@/components/navbar_menu/navbar';
import {
  IconArrowLeft,
  IconBrandTabler,
  IconSettings,
  IconUserBolt,
  IconCreditCard,
  IconRobot,
  IconNetwork,
  IconTool,
} from '@tabler/icons-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface UserData {
  id: string;
  email: string;
  name: string;
  username: string;
  credits: number;
  isOrganization: boolean;
}

export default function DashboardPage() {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'include' })
      .then(res => res.ok ? res.json() : Promise.reject('Auth failed'))
      .then((data: any) => {
        setUser(data.user);
        setLoading(false);
      })
      .catch(() => {
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        setLoading(false);
      });
  }, []);

  const handleLogout = () => {
    fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
      .then(() => window.location.href = '/login')
      .catch(() => window.location.href = '/login');
  };

  const links = [
    {
      label: "Dashboard",
      href: "#",
      icon: (
        <IconBrandTabler className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Credits",
      href: "#",
      icon: (
        <IconCreditCard className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Connectivity",
      href: "#",
      icon: (
        <IconNetwork className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Agent Station",
      href: "#",
      icon: (
        <IconRobot className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Automation Engine",
      href: "#",
      icon: (
        <IconTool className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Settings",
      href: "#",
      icon: (
        <IconSettings className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F8FAFC] dark:bg-[#0F172A] text-[#0F172A] dark:text-[#F8FAFC] text-xl transition-colors duration-300">
        Loading...
      </div>
    );
  }

  if (!user) return null;

  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-full flex-1 flex-col overflow-hidden bg-[#F8FAFC] dark:bg-[#0F172A] md:flex-row transition-colors duration-300",
        "h-screen"
      )}
    >
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10">
          <div className="flex flex-1 flex-col overflow-x-hidden overflow-y-auto">
            {open ? <Logo /> : <LogoIcon />}
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <SidebarLink key={idx} link={link} />
              ))}
            </div>
          </div>
          <div>
            <SidebarLink
              link={{
                label: user.name,
                href: "#",
                icon: (
                  <div className="h-7 w-7 shrink-0 rounded-full bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center text-white font-bold text-sm">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                ),
              }}
            />
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 mt-2 w-full text-left py-2 text-[#0F172A] dark:text-[#F8FAFC] hover:bg-[#3B82F6]/10 dark:hover:bg-[#8B5CF6]/10 rounded-md px-2 transition-colors"
            >
              <IconArrowLeft className="h-5 w-5 shrink-0" />
              {open && <span className="text-sm">Logout</span>}
            </button>
          </div>
        </SidebarBody>
      </Sidebar>
      <DashboardContent user={user} />
    </div>
  );
}

export const Logo = () => {
  return (
    <a
      href="#"
      className="relative z-20 flex items-center space-x-2 py-1 text-sm font-normal text-[#0F172A] dark:text-[#F8FAFC]"
    >
      <motion.div 
        className="h-8 w-8 shrink-0 rounded bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center"
        animate={{
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        <span className="text-white font-bold text-sm">DX</span>
      </motion.div>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="font-bold whitespace-pre text-[#0F172A] dark:text-[#F8FAFC]"
      >
        DXTR Labs
      </motion.span>
    </a>
  );
};

export const LogoIcon = () => {
  return (
    <a
      href="#"
      className="relative z-20 flex items-center space-x-2 py-1 text-sm font-normal text-[#0F172A] dark:text-[#F8FAFC]"
    >
      <motion.div 
        className="h-8 w-8 shrink-0 rounded bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center"
        animate={{
          scale: [1, 1.05, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        <span className="text-white font-bold text-sm">DX</span>
      </motion.div>
    </a>
  );
};

const DashboardContent = ({ user }: { user: UserData }) => {
  return (
    <div className="flex flex-1">
      <div className="flex h-full w-full flex-1 flex-col gap-6 rounded-tl-2xl bg-white/80 dark:bg-[#0F172A]/80 backdrop-blur-xl border-l border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 p-6 md:p-10">
        {/* Welcome Header */}
        <div className="mb-6">{/* REBUILT */}
          <h1 className="text-3xl font-bold text-[#0F172A] dark:text-[#F8FAFC] mb-2">Welcome back, {user.name}!</h1>
          <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70">Here&apos;s what&apos;s happening with your AI automation platform.</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <StatsCard
            title="Credits"
            value={user.credits.toString()}
            icon={<IconCreditCard className="h-6 w-6" />}
            color="from-[#3B82F6] to-[#8B5CF6]"
          />
          <StatsCard
            title="Active Agents"
            value="3"
            icon={<IconRobot className="h-6 w-6" />}
            color="from-[#3B82F6] to-[#8B5CF6]"
          />
          <StatsCard
            title="Automations"
            value="12"
            icon={<IconTool className="h-6 w-6" />}
            color="from-[#3B82F6] to-[#8B5CF6]"
          />
          <StatsCard
            title="Connections"
            value="8"
            icon={<IconNetwork className="h-6 w-6" />}
            color="from-[#3B82F6] to-[#8B5CF6]"
          />
        </div>

        {/* Main Content Areas */}
        <div className="flex flex-1 gap-6">
          <div className="flex-1 bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-xl rounded-xl p-6 border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
            <h3 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">Recent Activity</h3>
            <div className="space-y-3">
              <ActivityItem 
                title="New automation created"
                description="Email processing workflow"
                time="2 hours ago"
              />
              <ActivityItem 
                title="Agent training completed"
                description="Customer support agent updated"
                time="5 hours ago"
              />
              <ActivityItem 
                title="Integration connected"
                description="Slack workspace linked"
                time="1 day ago"
              />
            </div>
          </div>
          
          <div className="flex-1 bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-xl rounded-xl p-6 border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
            <h3 className="text-xl font-semibold text-[#0F172A] dark:text-[#F8FAFC] mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 gap-3">
              <QuickActionButton 
                title="Create New Agent"
                description="Set up a new AI agent"
                icon={<IconRobot className="h-5 w-5" />}
              />
              <QuickActionButton 
                title="Build Automation"
                description="Create a new workflow"
                icon={<IconTool className="h-5 w-5" />}
              />
              <QuickActionButton 
                title="Connect Service"
                description="Integrate external platform"
                icon={<IconNetwork className="h-5 w-5" />}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatsCard = ({ title, value, icon, color }: {
  title: string;
  value: string;
  icon: React.ReactNode;
  color: string;
}) => (
  <div className="bg-white/60 dark:bg-[#0F172A]/60 backdrop-blur-xl rounded-xl p-4 border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70 text-sm">{title}</p>
        <p className="text-2xl font-bold text-[#0F172A] dark:text-[#F8FAFC]">{value}</p>
      </div>
      <div className={`p-3 rounded-lg bg-gradient-to-r ${color} text-white`}>
        {icon}
      </div>
    </div>
  </div>
);

const ActivityItem = ({ title, description, time }: {
  title: string;
  description: string;
  time: string;
}) => (
  <div className="p-3 bg-white/40 dark:bg-[#0F172A]/40 rounded-lg border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20">
    <h4 className="text-[#0F172A] dark:text-[#F8FAFC] font-medium text-sm">{title}</h4>
    <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70 text-xs">{description}</p>
    <p className="text-[#0F172A]/50 dark:text-[#F8FAFC]/50 text-xs mt-1">{time}</p>
  </div>
);

const QuickActionButton = ({ title, description, icon }: {
  title: string;
  description: string;
  icon: React.ReactNode;
}) => (
  <button className="p-4 bg-white/40 dark:bg-[#0F172A]/40 hover:bg-white/60 dark:hover:bg-[#0F172A]/60 rounded-lg border border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 transition-colors text-left">
    <div className="flex items-center gap-3">
      <div className="text-[#3B82F6] dark:text-[#8B5CF6]">{icon}</div>
      <div>
        <h4 className="text-[#0F172A] dark:text-[#F8FAFC] font-medium text-sm">{title}</h4>
        <p className="text-[#0F172A]/70 dark:text-[#F8FAFC]/70 text-xs">{description}</p>
      </div>
    </div>
  </button>
);



