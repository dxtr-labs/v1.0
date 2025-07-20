'use client';  // Add this line at the top of the file

import React, { createContext, useState, useContext, useEffect } from 'react';

type ThemeContextType = {
  isDarkMode: boolean;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(true); // Default to dark mode
  const [mounted, setMounted] = useState(false);

  const applyTheme = (dark: boolean) => {
    if (typeof window === 'undefined') return;
    
    const root = document.documentElement;
    const body = document.body;
    
    // Clear any existing background styles
    root.style.removeProperty('background');
    body.style.removeProperty('background');
    root.style.removeProperty('background-image');
    body.style.removeProperty('background-image');
    
    if (dark) {
      root.classList.add('dark');
      body.classList.add('dark');
      root.style.backgroundColor = '#0F172A !important';
      body.style.backgroundColor = '#0F172A !important';
    } else {
      root.classList.remove('dark');
      body.classList.remove('dark');
      root.style.backgroundColor = '#F8FAFC !important';
      body.style.backgroundColor = '#F8FAFC !important';
    }
  };

  const toggleTheme = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    applyTheme(newDarkMode);
    
    // Store preference in localStorage
    localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
  };

  useEffect(() => {
    setMounted(true);
    
    // Check for stored theme preference or system preference
    const storedTheme = localStorage.getItem('theme');
    let initialDark = false;
    
    if (storedTheme) {
      initialDark = storedTheme === 'dark';
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      initialDark = true;
    }
    
    setIsDarkMode(initialDark);
    applyTheme(initialDark);

    // Listen for system theme changes (only if no stored preference)
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        setIsDarkMode(e.matches);
        applyTheme(e.matches);
      }
    };
    
    try {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    } catch (e) {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      {mounted ? children : null}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

