'use client';
import dynamic from 'next/dynamic';
import React from 'react';

// Dynamically load Spline with SSR disabled
const Spline = dynamic(() => import('@splinetool/react-spline/next'), {
  ssr: false,
});

export default function SplineCanvas() {
  return (
    <div className="w-full h-[600px] rounded-2xl overflow-hidden shadow-2xl bg-[#F5F5F7]/50 dark:bg-neutral-800/50 backdrop-blur-xl border border-[#0F172A]/10 dark:border-[#F8FAFC]/10">
      <Spline scene="https://prod.spline.design/PPoMGSaBQytYC2D9/scene.splinecode" style={{ width: '100%', height: '100%' }} />
    </div>
  );
}



