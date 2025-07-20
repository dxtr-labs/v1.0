'use client';

import React from 'react'
import { cn } from '../../lib/utils'

interface BackgroundGradientProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function BackgroundGradient({ children, className, ...props }: BackgroundGradientProps) {
  return (
    <div
      className={cn(
        'relative rounded-[inherit] p-[1px] overflow-hidden bg-gradient-to-r from-blue-500 to-indigo-500',
        'before:absolute before:inset-0 before:bg-gradient-to-r before:from-blue-500 before:to-indigo-500 before:blur-xl before:opacity-50 before:-z-10',
        className
      )}
      {...props}
    >
      <div className="relative rounded-[inherit] bg-background z-10">
        {children}
      </div>
    </div>
  )
}

export default BackgroundGradient
