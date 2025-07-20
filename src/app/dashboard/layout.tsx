'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
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

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

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
      href: "/dashboard",
      icon: (
        <IconBrandTabler className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Credits",
      href: "/dashboard/credits",
      icon: (
        <IconCreditCard className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Connectivity",
      href: "/dashboard/connectivity",
      icon: (
        <IconNetwork className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Agent Station",
      href: "/dashboard/agents",
      icon: (
        <IconRobot className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Automation Engine",
      href: "/dashboard/automation",
      icon: (
        <IconTool className="h-5 w-5 shrink-0 text-[#3B82F6] dark:text-[#8B5CF6]" />
      ),
    },
    {
      label: "Settings",
      href: "/dashboard/settings",
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
            <Logo />
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <SidebarLink 
                  key={idx} 
                  link={{
                    ...link,
                    href: link.href,
                  }}
                  className={pathname === link.href ? "bg-[#3B82F6]/10 dark:bg-[#8B5CF6]/10 rounded-md" : ""}
                />
              ))}
            </div>
          </div>
          <div>
            <SidebarLink
              link={{
                label: user?.name || 'User',
                href: "#",
                icon: (
                  <div className="h-7 w-7 shrink-0 rounded-full bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center text-white font-bold text-sm">
                    {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
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
      
      {/* Dynamic Content Area */}
      <div className="flex flex-1">
        <div className="flex h-full w-full flex-1 flex-col gap-6 rounded-tl-2xl bg-white/80 dark:bg-[#0F172A]/80 backdrop-blur-xl border-l border-[#3B82F6]/20 dark:border-[#8B5CF6]/20 p-6 md:p-10">
          {children}
        </div>
      </div>
    </div>
  );
}

export const Logo = () => {
  return (
    <a
      href="/dashboard"
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



