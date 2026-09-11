"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function AutonomyPage() {
  const router = useRouter();
  const [selected, setSelected] = useState<string | null>(null);
  
  const options = [
    {
      id: "ESSENTIALS",
      title: "Keep my essentials stocked",
      desc: "Monitor everyday items and help keep them available.",
      examples: "Milk, Rice, Atta, Oil, Eggs"
    },
    {
      id: "ROUTINE",
      title: "Repeat my usual orders",
      desc: "Remember what you regularly buy and make routine reordering effortless.",
      examples: "Coffee every ~20 days, Cleaning supplies monthly"
    },
    {
      id: "MEALS",
      title: "Plan meals & ingredients",
      desc: "Tell NOVA what you want to make. It figures out what's missing.",
      examples: '"I want to make Maggi tonight."'
    },
    {
      id: "BUDGET",
      title: "Stay within my budget",
      desc: "Give NOVA a spending limit and let it manage routine purchases around it.",
      examples: "₹2,000 / week limit"
    },
    {
      id: "FULL_AUTOPILOT",
      title: "Let NOVA manage my household",
      desc: "Monitor essentials, predict needs, respect my rules and act when appropriate.",
      isRecommended: true
    }
  ];

  const handleComplete = async () => {
    if (!selected) return;
    
    await fetch('/api/onboarding/autonomy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile: selected })
    });
    
    router.push('/store');
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans flex flex-col items-center pb-24">
      <div className="max-w-3xl w-full">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">What should NOVA take care of?</h1>
        <p className="text-neutral-500 mb-12 text-lg">You decide how much autonomy you want. NOVA handles the routine.</p>
        
        <div className="flex flex-col gap-4 mb-12">
          {options.map(opt => (
            <div 
              key={opt.id} 
              onClick={() => setSelected(opt.id)}
              className={`p-6 rounded-xl border-2 cursor-pointer transition-all ${selected === opt.id ? 'border-neutral-900 bg-white shadow-sm' : 'border-neutral-200 bg-white hover:border-neutral-300'}`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-lg mb-1 flex items-center gap-3">
                    {opt.title}
                    {opt.isRecommended && <span className="bg-neutral-900 text-white text-xs px-2 py-1 rounded">Recommended</span>}
                  </h3>
                  <p className="text-neutral-600">{opt.desc}</p>
                  {opt.examples && <p className="text-sm text-neutral-400 mt-2 font-mono bg-neutral-50 p-2 rounded inline-block">{opt.examples}</p>}
                </div>
                <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${selected === opt.id ? 'border-neutral-900' : 'border-neutral-300'}`}>
                  {selected === opt.id && <div className="w-3 h-3 bg-neutral-900 rounded-full"></div>}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex justify-end sticky bottom-8">
          <button 
            onClick={handleComplete}
            disabled={!selected}
            className="px-8 py-4 bg-neutral-900 text-white rounded-xl font-medium hover:bg-neutral-800 disabled:opacity-50 shadow-lg"
          >
            Enter NOVA
          </button>
        </div>
      </div>
    </div>
  );
}
