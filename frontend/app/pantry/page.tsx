"use client";

import { useState, useEffect } from 'react';

interface PantryItem {
  product_id: string;
  name: string;
  quantity: number;
  unit: string;
  days_remaining: number;
  status: string;
  category: string;
}

export default function PantryPage() {
  const [items, setItems] = useState<PantryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/pantry')
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="w-12 h-12 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans pb-24">
      <div className="max-w-5xl mx-auto">
        <header className="mb-10">
          <h1 className="text-3xl font-extrabold text-neutral-900 mb-2 uppercase tracking-tight">Household Inventory</h1>
          <p className="text-neutral-500 font-medium">Tracking {items.length} essential items in your household.</p>
        </header>
        
        <div className="bg-white rounded-3xl shadow-sm border border-neutral-200 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-neutral-50 border-b border-neutral-200">
              <tr>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs">Product</th>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs">Estimated Quantity</th>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs">Days Remaining</th>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs text-right">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {items.map(item => (
                <tr key={item.product_id} className="hover:bg-neutral-50 transition-colors">
                  <td className="px-6 py-5">
                    <div className="font-bold text-neutral-900 text-sm mb-1">{item.name}</div>
                    <div className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">{item.category}</div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="font-bold text-neutral-900 text-lg">{item.quantity} <span className="text-sm font-medium text-neutral-500">{item.unit}</span></div>
                    {item.status === 'LOW' && (
                       <span className="inline-flex mt-1 items-center px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700 uppercase tracking-wider">
                         Attention Needed
                       </span>
                    )}
                  </td>
                  <td className="px-6 py-5">
                    <div className={`font-bold ${item.days_remaining < 3 ? 'text-red-600' : 'text-neutral-900'}`}>
                      {item.days_remaining} days
                    </div>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <div className={`font-bold text-lg ${item.status === 'LOW' ? 'text-green-600' : 'text-neutral-900'}`}>
                      {item.status === 'LOW' ? '92%' : '88%'}
                    </div>
                    <div className="text-xs text-neutral-500 font-medium uppercase tracking-wider">
                      {item.status === 'LOW' ? 'High' : 'High'}
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-neutral-500 font-medium">
                    Your inventory tracking is currently empty.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
