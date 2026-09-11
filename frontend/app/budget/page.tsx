"use client";

import { useState, useEffect } from 'react';

interface BudgetState {
  monthly: number;
  spent: number;
  remaining: number;
  auto_limit: number;
}

export default function BudgetPage() {
  const [budget, setBudget] = useState<BudgetState | null>(null);

  useEffect(() => {
    fetch('/api/budget')
      .then(res => res.json())
      .then(data => setBudget(data));
  }, []);

  if (!budget) return <div className="min-h-screen flex items-center justify-center bg-neutral-50">Loading...</div>;

  const percentSpent = Math.min(100, Math.round((budget.spent / budget.monthly) * 100));

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans pb-24">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-neutral-900 mb-8">Household Budget</h1>
        
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-neutral-200 mb-8">
          <div className="flex justify-between items-end mb-4">
            <div>
              <p className="text-neutral-500 mb-1">Monthly Budget</p>
              <h2 className="text-4xl font-bold">₹{budget.monthly}</h2>
            </div>
            <div className="text-right">
              <p className="text-neutral-500 mb-1">Spent</p>
              <h2 className="text-2xl font-bold text-neutral-700">₹{budget.spent}</h2>
            </div>
          </div>
          
          <div className="w-full bg-neutral-100 rounded-full h-4 mb-4">
            <div className="bg-neutral-900 h-4 rounded-full" style={{ width: `${percentSpent}%` }}></div>
          </div>
          
          <div className="flex justify-between text-sm">
            <span className="font-medium text-neutral-600">{percentSpent}% used</span>
            <span className="font-bold text-green-600">₹{budget.remaining} remaining</span>
          </div>
        </div>
        
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-neutral-200">
          <h3 className="text-xl font-bold mb-4">Automatic Purchase Limit</h3>
          <p className="text-neutral-600 mb-6">
            NOVA will automatically buy eligible items if their price is under this limit. Items above this limit will require your approval.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-3xl font-bold">₹{budget.auto_limit}</span>
            <button className="px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 font-medium">
              Edit Limit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
