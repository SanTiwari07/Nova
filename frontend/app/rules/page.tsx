"use client";

import { useState } from 'react';

export default function RulesPage() {
  const [autoCats, setAutoCats] = useState(["Milk", "Rice", "Atta", "Eggs", "Bread"]);
  const [askCats, setAskCats] = useState(["Snacks", "Electronics"]);
  const [restrictedCats, setRestrictedCats] = useState(["Alcohol", "Tobacco"]);
  
  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans pb-24">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Your Rules</h1>
        <p className="text-neutral-500 mb-8 text-lg">Define how NOVA acts on your behalf.</p>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-200 mb-6">
          <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500 inline-block"></span>
            Automatic
          </h2>
          <p className="text-neutral-600 mb-4">NOVA can buy these without asking, as long as it's within budget and price limits.</p>
          <div className="flex flex-wrap gap-2">
            {autoCats.map(cat => (
              <span key={cat} className="px-3 py-1 bg-neutral-100 border border-neutral-200 rounded-full text-sm font-medium">{cat}</span>
            ))}
            <button className="px-3 py-1 bg-white border border-dashed border-neutral-300 text-neutral-400 rounded-full text-sm hover:bg-neutral-50">
              + Add Category
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-200 mb-6">
          <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-yellow-500 inline-block"></span>
            Ask Me First
          </h2>
          <p className="text-neutral-600 mb-4">NOVA will prepare the cart but will wait for your explicit approval.</p>
          <div className="flex flex-wrap gap-2">
            {askCats.map(cat => (
              <span key={cat} className="px-3 py-1 bg-neutral-100 border border-neutral-200 rounded-full text-sm font-medium">{cat}</span>
            ))}
            <button className="px-3 py-1 bg-white border border-dashed border-neutral-300 text-neutral-400 rounded-full text-sm hover:bg-neutral-50">
              + Add Category
            </button>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-200">
          <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 inline-block"></span>
            Never Purchase
          </h2>
          <p className="text-neutral-600 mb-4">Restricted categories that NOVA is not allowed to buy under any circumstances.</p>
          <div className="flex flex-wrap gap-2">
            {restrictedCats.map(cat => (
              <span key={cat} className="px-3 py-1 bg-neutral-100 border border-neutral-200 rounded-full text-sm font-medium">{cat}</span>
            ))}
            <button className="px-3 py-1 bg-white border border-dashed border-neutral-300 text-neutral-400 rounded-full text-sm hover:bg-neutral-50">
              + Add Category
            </button>
          </div>
        </div>
        
      </div>
    </div>
  );
}
