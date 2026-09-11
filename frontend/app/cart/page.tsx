"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function CartPage() {
  const [cart, setCart] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);
  const router = useRouter();

  // In this demo we don't have a GET /cart, but we can simulate it by storing items in a global state
  // OR we can just add a quick GET /api/cart to the backend. Let's assume we add it.
  
  useEffect(() => {
    fetch('/api/cart')
      .then(res => res.json())
      .then(data => setCart(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleCheckout = async () => {
    if (checkingOut) return;
    setCheckingOut(true);
    await fetch('/api/checkout', { method: 'POST' });
    router.push('/orders');
  };

  if (loading) return <div className="min-h-screen flex justify-center pt-32">Loading...</div>;

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Cart</h1>
        
        {(!cart || !cart.items || cart.items.length === 0) ? (
          <div className="bg-white p-12 text-center rounded-2xl shadow-sm border border-neutral-200 text-neutral-500">
            Your cart is empty.
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-neutral-200 overflow-hidden">
            <div className="p-6">
              <ul className="divide-y divide-neutral-100">
                {cart.items.map((item: any, idx: number) => (
                  <li key={idx} className="py-4 flex justify-between items-center">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-neutral-100 rounded relative">
                        <img src={item.image} alt={item.name} className="object-cover w-full h-full rounded" />
                      </div>
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-neutral-500">{item.pack_size}</p>
                      </div>
                    </div>
                    <p className="font-medium">₹{item.price}</p>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-neutral-50 p-6 border-t border-neutral-200 flex justify-between items-center">
              <div>
                <p className="text-neutral-500 text-sm mb-1">Total</p>
                <p className="text-2xl font-bold">₹{cart.items.reduce((acc: number, cur: any) => acc + cur.price, 0)}</p>
              </div>
              <button 
                onClick={handleCheckout}
                disabled={checkingOut}
                className="px-8 py-4 bg-neutral-900 text-white font-medium rounded-xl hover:bg-neutral-800 disabled:opacity-50"
              >
                {checkingOut ? 'Placing Order...' : 'Place Simulated Order'}
              </button>
            </div>
            <div className="text-center pb-4 bg-neutral-50">
              <p className="text-xs text-neutral-400">Demo checkout. This is a simulated purchase. No real payment will be made.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
