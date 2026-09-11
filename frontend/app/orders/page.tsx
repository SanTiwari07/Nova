"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function OrdersPage() {
  const [orders, setOrders] = useState<any[]>([]);
  const [historyOrders, setHistoryOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/orders").then(r => r.json()).catch(() => []),
      fetch("/api/purchase-history").then(r => r.json()).catch(() => { products: [] }),
    ]).then(([liveOrders, history]) => {
      setOrders(liveOrders || []);
      // Build order list from history service
      // Use seeded orders from history for demo richness
      setHistoryOrders([]);
    }).finally(() => setLoading(false));
  }, []);

  // Seeded demo orders for display
  const demoOrders: any[] = [
    {
      order_id: "AMZ-2026-001",
      order_date: "2026-09-08",
      status: "DELIVERED",
      total: 876,
      retailer: "Amazon",
      source: "AMAZON_MOCK",
      items: [
        { name: "Aashirvaad Atta 5kg", price: 289, qty: 1 },
        { name: "Tata Sampann Toor Dal 1kg", price: 142, qty: 2 },
        { name: "Tata Salt 1kg", price: 25, qty: 2 },
        { name: "Dettol Soap Pack of 4", price: 139, qty: 1 },
        { name: "Harpic Power Plus 750ml", price: 109, qty: 1 },
      ],
      nova_analysis: {
        recurring_items: 5,
        early_purchases: 1,
        below_avg_price_items: 2,
        summary: "5 recurring household items. 2 items purchased at below-average prices. Atta was bought 1 week earlier than usual.",
      },
    },
    {
      order_id: "AMZ-2026-002",
      order_date: "2026-08-28",
      status: "DELIVERED",
      total: 1363,
      retailer: "Amazon",
      source: "AMAZON_MOCK",
      items: [
        { name: "Fortune Sunflower Oil 5L", price: 749, qty: 1 },
        { name: "Tata Chai Classic Tea 500g", price: 215, qty: 1 },
        { name: "Surf Excel Detergent 3kg", price: 399, qty: 1 },
      ],
      nova_analysis: {
        recurring_items: 3,
        early_purchases: 0,
        below_avg_price_items: 1,
        summary: "3 recurring household items. Tea was purchased at a below-average price. Detergent was slightly above average — NOVA noted this.",
      },
    },
    ...orders.map(o => ({
      order_id: o.id,
      order_date: new Date().toISOString().split("T")[0],
      status: o.status || "CONFIRMED",
      total: o.total,
      retailer: "Amazon",
      source: "AMAZON_MOCK",
      items: (o.items || []).map((i: any) => ({ name: i.name, price: i.price, qty: 1 })),
      nova_analysis: {
        recurring_items: o.items?.length || 0,
        early_purchases: 0,
        below_avg_price_items: 0,
        summary: "Order placed via NOVA autopilot.",
      },
    })),
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FCFBF9] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">Amazon · Demo data</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Orders</h1>
          <p className="text-neutral-500">Your Amazon household orders, enhanced with NOVA intelligence.</p>
        </div>

        {/* Orders list */}
        <div className="space-y-4">
          {demoOrders.map(order => (
            <div key={order.order_id} className="bg-white rounded-2xl border border-neutral-200 overflow-hidden hover:shadow-sm transition-all">
              {/* Order header */}
              <div className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="text-xs font-bold text-neutral-400 uppercase">Amazon</span>
                      <span className="text-neutral-200">·</span>
                      <span className="text-xs text-neutral-400">{order.order_date}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${order.status === "DELIVERED" ? "bg-green-100 text-green-700" : "bg-orange-100 text-orange-700"}`}>
                        {order.status}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-neutral-100 text-neutral-400 rounded-full">Demo data</span>
                    </div>
                    <p className="text-xs text-neutral-500">{order.order_id}</p>
                  </div>
                  <p className="text-lg font-black text-neutral-900 shrink-0">₹{order.total.toLocaleString("en-IN")}</p>
                </div>

                {/* Items preview */}
                <div className="mt-3 flex flex-wrap gap-1">
                  {order.items.slice(0, 3).map((item: any, i: number) => (
                    <span key={i} className="text-xs px-2 py-1 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-600">{item.name}</span>
                  ))}
                  {order.items.length > 3 && (
                    <span className="text-xs px-2 py-1 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-400">+{order.items.length - 3} more</span>
                  )}
                </div>
              </div>

              {/* NOVA analysis bar */}
              <div
                className="border-t border-neutral-100 bg-orange-50 p-4 cursor-pointer hover:bg-orange-100/50 transition-colors"
                onClick={() => setExpandedId(expandedId === order.order_id ? null : order.order_id)}
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm">✦</span>
                  <p className="text-xs text-orange-800 flex-1">{order.nova_analysis.summary}</p>
                  <svg className={`text-orange-400 transition-transform ${expandedId === order.order_id ? "rotate-180" : ""}`} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                </div>
              </div>

              {/* Expanded NOVA detail + Learn actions */}
              {expandedId === order.order_id && (
                <div className="border-t border-orange-100 p-5 bg-orange-50/50">
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {[
                      { label: "Recurring items", value: String(order.nova_analysis.recurring_items) },
                      { label: "Early purchases", value: String(order.nova_analysis.early_purchases || 0) },
                      { label: "Below avg price", value: String(order.nova_analysis.below_avg_price_items || 0) },
                    ].map(stat => (
                      <div key={stat.label} className="bg-white rounded-xl p-3 border border-orange-100">
                        <p className="text-lg font-black text-neutral-900">{stat.value}</p>
                        <p className="text-xs text-neutral-400 mt-0.5">{stat.label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-2">
                    {order.items.map((item: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-white rounded-xl border border-orange-100">
                        <div>
                          <p className="text-sm font-medium text-neutral-900">{item.name}</p>
                          <p className="text-xs text-neutral-400">Qty: {item.qty} · ₹{item.price}</p>
                        </div>
                        <div className="flex gap-1">
                          <button className="px-2 py-1 text-[10px] font-semibold text-neutral-600 bg-neutral-100 rounded-lg hover:bg-neutral-200 transition-colors">One-time</button>
                          <button className="px-2 py-1 text-[10px] font-semibold text-neutral-600 bg-neutral-100 rounded-lg hover:bg-neutral-200 transition-colors">Recurring</button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <p className="text-xs text-neutral-400 mt-3">Mark items to help NOVA learn your preferences.</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
