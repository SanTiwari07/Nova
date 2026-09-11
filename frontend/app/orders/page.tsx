"use client";

import { useState, useEffect } from 'react';

interface Order {
  id: string;
  status: string;
  items: any[];
  total: number;
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/orders')
      .then(res => res.json())
      .then(data => setOrders(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-neutral-50">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans pb-24">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-neutral-900 mb-8">Orders</h1>
        
        <div className="space-y-6">
          {orders.map(order => (
            <div key={order.id} className="bg-white rounded-2xl shadow-sm border border-neutral-200 overflow-hidden">
              <div className="bg-neutral-50 p-4 border-b border-neutral-200 flex justify-between items-center">
                <div>
                  <p className="text-sm text-neutral-500 font-medium">Order ID: {order.id}</p>
                  <p className="text-xs text-neutral-400 mt-1">NOVA Demo Order · Simulated Purchase</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-neutral-900">Total: ₹{order.total}</p>
                  <span className="inline-block mt-1 px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded uppercase tracking-wider">
                    {order.status}
                  </span>
                </div>
              </div>
              <div className="p-4">
                <ul className="divide-y divide-neutral-100">
                  {order.items.map((item, idx) => (
                    <li key={idx} className="py-3 flex justify-between items-center">
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-neutral-500">{item.brand} • {item.pack_size}</p>
                      </div>
                      <p className="font-medium text-neutral-700">₹{item.price}</p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
          
          {orders.length === 0 && (
            <div className="text-center text-neutral-500 py-12 bg-white rounded-2xl shadow-sm border border-neutral-200">
              You have no recent orders.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
