"use client";

import Link from 'next/link';
import Image from 'next/image';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-neutral-900 text-white flex flex-col font-sans relative overflow-hidden">
      {/* Decorative AI background */}
      <div className="absolute inset-0 opacity-10">
        <Image src="/assets/fallbacks/hero.png" alt="Background" fill className="object-cover" />
      </div>
      <div className="absolute inset-0 bg-gradient-to-t from-neutral-900 via-neutral-900/80 to-neutral-900/20"></div>

      <nav className="relative z-10 w-full p-8 flex justify-between items-center">
        <div className="font-extrabold text-xl tracking-tight">HOUSEHOLD AUTOPILOT</div>
      </nav>

      <div className="relative z-10 flex-grow flex flex-col justify-center items-center text-center px-8">
        <div className="max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 mb-8 backdrop-blur-md">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-xs font-bold tracking-widest uppercase">Agentic Intelligence</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold mb-6 tracking-tighter leading-tight">
            The autonomous <br /> operating system <br /> for your home.
          </h1>
          
          <p className="text-xl md:text-2xl text-neutral-400 mb-12 font-medium max-w-2xl mx-auto">
            Household Autopilot understands your home, predicts what you need, and uses commerce to automatically execute decisions.
          </p>
          
          <Link 
            href="/store"
            className="inline-flex items-center gap-3 px-8 py-4 bg-white text-neutral-900 font-bold rounded-full text-lg hover:bg-neutral-100 transition-transform hover:scale-105 active:scale-95"
          >
            Start Autopilot
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </Link>
        </div>
      </div>
    </div>
  );
}
