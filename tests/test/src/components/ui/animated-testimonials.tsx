"use client"

import React from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';

interface Testimonial {
  quote: string;
  name: string;
  designation: string;
  src?: string;
}

interface AnimatedTestimonialsProps {
  testimonials: Testimonial[];
}

export function AnimatedTestimonials({ testimonials }: AnimatedTestimonialsProps) {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="bg-white/5 backdrop-blur-lg rounded-2xl p-6 border border-white/10"
            >
              <p className="text-[#0F172A] dark:text-[#F8FAFC] mb-6 italic">
                &ldquo;{testimonial.quote}&rdquo;
              </p>
              <div className="flex items-center gap-4">
                {testimonial.src ? (
                  <Image
                    src={testimonial.src}
                    alt={testimonial.name}
                    width={48}
                    height={48}
                    className="rounded-full object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-[#3B82F6] dark:bg-[#8B5CF6] flex items-center justify-center text-[#0F172A]">
                    {testimonial.name.split(' ').map(n => n[0]).join('')}
                  </div>
                )}
                <div>
                  <div className="font-medium text-[#0F172A] dark:text-[#F8FAFC]">
                    {testimonial.name}
                  </div>
                  <div className="text-sm text-[#0F172A]/70 dark:text-[#F8FAFC]/70">
                    {testimonial.designation}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}


