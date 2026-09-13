"use client";

import { useState, useEffect, useCallback } from "react";
import ProductImage from "@/components/ProductImage";
import { Sparkles, CheckCircle2, Clock, AlertCircle, MinusCircle, ShieldCheck, ChevronDown, ChevronUp } from "lucide-react";

interface OrderItem {
  name: string;
  price: number;
  qty?: number;
  imageUrl?: string;
}

interface Order {
  id: string;
  status: string;
  total: number;
  items: OrderItem[];
  decision?: string;
  decision_label?: string;
  nova_reason?: string[];
  source?: string;
  created_at?: string;
}

interface AuditEntry {
  id: string;
  product: string;
  decision: string;
  reasons: string[];
  timestamp: string;
  imageUrl?: string;
}

const DECISION_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode; bg: string }> = {
  AUTO: { label: "Taken care of by NOVA", color: "text-emerald-700", bg: "bg-emerald-50 border-emerald-100", icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" /> },
  ASK: { label: "Waiting for your approval", color: "text-amber-700", bg: "bg-amber-50 border-amber-100", icon: <AlertCircle className="w-4 h-4 text-amber-500" /> },
  ASK_APPROVED: { label: "Approved by you", color: "text-emerald-700", bg: "bg-emerald-50 border-emerald-100", icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" /> },
  DO_NOTHING: { label: "No action needed", color: "text-neutral-500", bg: "bg-neutral-50 border-neutral-100", icon: <MinusCircle className="w-4 h-4 text-neutral-400" /> },
  WAIT: { label: "Waiting for better price", color: "text-blue-700", bg: "bg-blue-50 border-blue-100", icon: <Clock className="w-4 h-4 text-blue-500" /> },
  BLOCKED: { label: "Blocked by your rules", color: "text-red-700", bg: "bg-red-50 border-red-100", icon: <ShieldCheck className="w-4 h-4 text-red-500" /> },
  CHECKOUT_COMPLETED: { label: "Order placed", color: "text-emerald-700", bg: "bg-emerald-50 border-emerald-100", icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" /> },
};

function getConfig(decision: string) {
  return DECISION_CONFIG[decision] ?? {
    label: decision || "Order",
    color: "text-neutral-600",
    bg: "bg-neutral-50 border-neutral-100",
    icon: <Sparkles className="w-4 h-4 text-neutral-400" />,
  };
}

function timeAgo(isoStr?: string) {
  if (!isoStr) return "";
  try {
    const diff = Date.now() - new Date(isoStr).getTime();
    const mins = Math.round(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.round(diff / 3600000);
    if (hrs < 24) return `${hrs}h ago`;
    return new Date(isoStr).toLocaleDateString("en-IN");
  } catch { return ""; }
}

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [activity, setActivity] = useState<AuditEntry[]>([]);
  const [pendingCount, setPendingCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [liveOrders, activityRes, pendingRes] = await Promise.all([
        fetch("/api/orders").then((r) => r.json()).catch(() => []),
        fetch("/api/audit/activity").then((r) => r.json()).catch(() => []),
        fetch("/api/orders/pending").then((r) => r.json()).catch(() => ({ count: 0 })),
      ]);
      setOrders(Array.isArray(liveOrders) ? liveOrders : []);
      setActivity(Array.isArray(activityRes) ? activityRes : []);
      setPendingCount(pendingRes?.count ?? 0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const refresh = () => loadData();
    window.addEventListener("household-updated", refresh);
    window.addEventListener("cart-updated", refresh);
    return () => {
      window.removeEventListener("household-updated", refresh);
      window.removeEventListener("cart-updated", refresh);
    };
  }, [loadData]);

  const handleApprove = async (auditId: string, product: string) => {
    await fetch(`/api/audit/activity`, { method: "GET" }); // refresh
    await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: `Please approve and proceed with purchasing ${product}` }),
    });
    window.dispatchEvent(new Event("household-updated"));
    await loadData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center pt-20">
        <div className="w-8 h-8 border-4 border-neutral-200 border-t-neutral-800 rounded-full animate-spin" />
      </div>
    );
  }

  // Pending ASK items from audit trail
  const pendingItems = activity.filter((a) => a.decision === "ASK");
  // Recent decisions (all types, most recent first)
  const recentDecisions = activity.slice(0, 20);

  const hasAnyData = orders.length > 0 || recentDecisions.length > 0;

  return (
    <div className="min-h-screen bg-[#FAFAF8] pt-20 pb-32">
      <div className="max-w-2xl mx-auto px-4 md:px-6">

        {/* Header */}
        <div className="pt-8 pb-6">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-1">NOVA · Decisions & Orders</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Orders</h1>
          <p className="text-neutral-500">
            Everything NOVA has done - and what still needs your input.
          </p>
        </div>

        {/* Needs approval */}
        {pendingItems.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xs font-bold tracking-widest text-amber-600 uppercase mb-3">
              Needs your approval · {pendingItems.length}
            </h2>
            <div className="space-y-3">
              {pendingItems.map((item) => (
                <div key={item.id} className="bg-white rounded-2xl border border-amber-100 p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-start gap-3">
                        {item.imageUrl && (
                          <div className="w-12 h-12 shrink-0 border border-amber-100 rounded-lg overflow-hidden bg-white relative">
                            <ProductImage src={item.imageUrl} alt={item.product} className="object-contain p-1" fill sizes="48px" />
                          </div>
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="font-bold text-neutral-900 mb-1">{item.product}</p>
                          {item.reasons.map((r, i) => (
                            <p key={i} className="text-xs text-neutral-500 mb-0.5 line-clamp-1">{r}</p>
                          ))}
                          <p className="text-[10px] text-neutral-400 mt-1">{timeAgo(item.timestamp)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => handleApprove(item.id, item.product)}
                      className="flex-1 py-2 rounded-xl bg-neutral-900 text-white text-sm font-bold hover:bg-neutral-800 transition-colors"
                    >
                      Approve
                    </button>
                    <button className="px-4 py-2 rounded-xl border border-neutral-200 text-neutral-600 text-sm font-bold hover:bg-neutral-50 transition-colors">
                      Decline
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Commerce orders placed by agent */}
        {orders.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-3">
              Placed orders · {orders.length}
            </h2>
            <div className="space-y-3">
              {orders.map((order) => {
                const cfg = getConfig(order.decision || "AUTO");
                const isExpanded = expandedId === order.id;
                return (
                  <div key={order.id} className="bg-white rounded-2xl border border-neutral-200 overflow-hidden">
                    <div className="p-4">
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex items-center gap-2">
                          {cfg.icon}
                          <p className={`text-xs font-bold uppercase tracking-wide ${cfg.color}`}>
                            {order.decision_label || cfg.label}
                          </p>
                        </div>
                        <p className="text-base font-black text-neutral-900">₹{order.total?.toLocaleString("en-IN")}</p>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mb-2">
                        {(order.items || []).slice(0, 3).map((item, i) => (
                          <div key={i} className="flex items-center gap-1.5 text-xs pr-2 py-0.5 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-600 overflow-hidden">
                            {item.imageUrl ? (
                              <div className="w-5 h-5 shrink-0 bg-white border-r border-neutral-100 relative">
                                <ProductImage src={item.imageUrl} alt={item.name} className="object-contain p-0.5" fill sizes="20px" />
                              </div>
                            ) : (
                              <div className="w-1.5" />
                            )}
                            <span className={item.imageUrl ? "" : "pl-0.5"}>{item.name}</span>
                          </div>
                        ))}
                        {(order.items?.length ?? 0) > 3 && (
                          <span className="text-xs px-2 py-1 bg-neutral-50 border border-neutral-100 rounded-lg text-neutral-400 flex items-center">
                            +{(order.items?.length ?? 0) - 3} more
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-neutral-400">{order.id} · {timeAgo(order.created_at)}</p>
                    </div>

                    {/* Why? expandable */}
                    <button
                      className="w-full border-t border-neutral-100 px-4 py-3 flex items-center justify-between hover:bg-neutral-50 transition-colors"
                      onClick={() => setExpandedId(isExpanded ? null : order.id)}
                    >
                      <span className="flex items-center gap-2 text-xs font-bold text-neutral-600">
                        <Sparkles className="w-3.5 h-3.5 text-[#FF9900]" />
                        Why did NOVA do this?
                      </span>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-neutral-400" /> : <ChevronDown className="w-4 h-4 text-neutral-400" />}
                    </button>
                    {isExpanded && (
                      <div className="px-4 py-4 bg-amber-50/50 border-t border-amber-100">
                        {(order.nova_reason || []).map((r, i) => (
                          <p key={i} className="text-sm text-neutral-700 mb-1 flex items-start gap-1.5">
                            <span className="text-amber-500 mt-0.5">›</span> {r}
                          </p>
                        ))}
                        <div className="mt-3 space-y-2">
                          {(order.items || []).map((item, i) => (
                            <div key={i} className="flex items-center justify-between py-2 border-t border-amber-100/50">
                              <div className="flex items-center gap-3">
                                {item.imageUrl && (
                                  <div className="w-10 h-10 shrink-0 border border-neutral-100 rounded bg-white relative overflow-hidden">
                                    <ProductImage src={item.imageUrl} alt={item.name} className="object-contain p-1" fill sizes="40px" />
                                  </div>
                                )}
                                <p className="text-sm text-neutral-700 font-medium">{item.name} <span className="text-neutral-400">x{item.qty || 1}</span></p>
                              </div>
                              <p className="text-sm font-bold text-neutral-900">₹{item.price}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* NOVA decision trail */}
        {recentDecisions.length > 0 && (
          <section className="mb-6">
            <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-3">
              NOVA decision trail
            </h2>
            <div className="bg-white rounded-2xl border border-neutral-200 divide-y divide-neutral-100 overflow-hidden">
              {recentDecisions.map((entry) => {
                const cfg = getConfig(entry.decision);
                return (
                  <div key={entry.id} className="px-4 py-3.5 flex items-start gap-3">
                    <span className="mt-0.5 shrink-0">{cfg.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                        <p className={`text-xs font-bold uppercase tracking-wide ${cfg.color}`}>{cfg.label}</p>
                        <p className="text-[10px] text-neutral-400">{timeAgo(entry.timestamp)}</p>
                      </div>
                      <div className="flex items-center gap-3 mt-1.5">
                        {entry.imageUrl ? (
                          <div className="w-12 h-12 shrink-0 border border-neutral-100 rounded-lg overflow-hidden bg-white relative">
                            <ProductImage src={entry.imageUrl} alt={entry.product} className="object-contain p-1" fill sizes="48px" />
                          </div>
                        ) : null}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-neutral-800 font-medium truncate">{entry.product}</p>
                          {entry.reasons[0] && (
                            <p className="text-xs text-neutral-500 mt-0.5 line-clamp-2">{entry.reasons[0]}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Empty state */}
        {!hasAnyData && (
          <div className="text-center py-16">
            <MinusCircle className="w-10 h-10 text-neutral-300 mx-auto mb-4" />
            <p className="font-bold text-neutral-500 mb-2">NOVA hasn't needed to place anything yet.</p>
            <p className="text-sm text-neutral-400">
              Use the command box on the home page to give NOVA something to do.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
