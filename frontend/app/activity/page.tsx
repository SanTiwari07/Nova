"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  CheckCircle2,
  Clock,
  ShieldCheck,
  AlertCircle,
  SlidersHorizontal,
  UtensilsCrossed,
  Package,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  Sparkles,
  RefreshCw,
  ShoppingBag
} from "lucide-react";

interface ActivityEvent {
  id: string;
  type: string;
  title: string;
  description: string;
  status: string;
  entityType: string;
  entityId?: string;
  product?: string;
  decision?: string;
  cost?: number;
  reasons: string[];
  metadata?: Record<string, any>;
  timestamp: string;
}

export default function ActivityPage() {
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>("ALL");
  const [expandedIds, setExpandedIds] = useState<Record<string, boolean>>({});

  const fetchActivity = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/audit/activity?limit=100");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setEvents(Array.isArray(data) ? data : []);
      setError(null);
    } catch (err: any) {
      console.error("Failed to fetch activity logs:", err);
      setError("Unable to load activity logs at this time.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivity();

    const handleUpdate = () => fetchActivity();
    window.addEventListener("household-updated", handleUpdate);
    window.addEventListener("budget-updated", handleUpdate);
    window.addEventListener("cart-updated", handleUpdate);

    return () => {
      window.removeEventListener("household-updated", handleUpdate);
      window.removeEventListener("budget-updated", handleUpdate);
      window.removeEventListener("cart-updated", handleUpdate);
    };
  }, []);

  const toggleExpand = (id: string) => {
    setExpandedIds((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const formatRelativeTime = (ts: string) => {
    try {
      const now = new Date();
      const date = new Date(ts);
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / (1000 * 60));
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return "Just now";
      if (diffMins < 60) return `${diffMins} min ago`;
      if (diffHours < 24) return `${diffHours} hr${diffHours > 1 ? "s" : ""} ago`;
      if (diffDays === 1) return "Yesterday";
      if (diffDays < 7) return `${diffDays} days ago`;
      return date.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
    } catch {
      return "Recently";
    }
  };

  // Group events into Today, Yesterday, Earlier
  const getGroupedEvents = (list: ActivityEvent[]) => {
    const today: ActivityEvent[] = [];
    const yesterday: ActivityEvent[] = [];
    const earlier: ActivityEvent[] = [];

    const now = new Date();
    const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const startOfYesterday = startOfToday - 24 * 60 * 60 * 1000;

    list.forEach((ev) => {
      const t = new Date(ev.timestamp).getTime();
      if (t >= startOfToday) {
        today.push(ev);
      } else if (t >= startOfYesterday) {
        yesterday.push(ev);
      } else {
        earlier.push(ev);
      }
    });

    return { today, yesterday, earlier };
  };

  const filteredEvents = events.filter((ev) => {
    if (activeFilter === "ALL") return true;
    if (activeFilter === "AUTO") return ev.decision === "AUTO" || ev.type === "PURCHASE_COMPLETED";
    if (activeFilter === "ASK") return ev.decision === "ASK" || ev.type === "PURCHASE_WAITING_APPROVAL";
    if (activeFilter === "PLANS") return ev.type === "PLAN_CREATED" || ev.entityType === "PLAN";
    if (activeFilter === "BUDGET") return ev.type === "BUDGET_CHANGED" || ev.entityType === "BUDGET";
    if (activeFilter === "INVENTORY") return ev.type === "INVENTORY_UPDATED" || ev.entityType === "PANTRY" || ev.decision === "DO_NOTHING";
    return true;
  });

  const { today, yesterday, earlier } = getGroupedEvents(filteredEvents);

  const getDecisionBadge = (ev: ActivityEvent) => {
    const dec = ev.decision || "";
    const type = ev.type || "";

    if (dec === "AUTO" || type === "PURCHASE_COMPLETED") {
      return {
        label: "Taken care of",
        badgeClass: "bg-emerald-50 text-emerald-700 border-emerald-200",
        icon: CheckCircle2,
        iconColor: "text-emerald-600",
      };
    }
    if (dec === "DO_NOTHING" || type === "AUTONOMOUS_ACTION") {
      return {
        label: "All sorted (Restraint)",
        badgeClass: "bg-blue-50 text-blue-700 border-blue-200",
        icon: ShieldCheck,
        iconColor: "text-blue-600",
      };
    }
    if (dec === "ASK" || type === "PURCHASE_WAITING_APPROVAL") {
      return {
        label: "Needs your input",
        badgeClass: "bg-amber-50 text-amber-700 border-amber-200",
        icon: AlertCircle,
        iconColor: "text-amber-600",
      };
    }
    if (type === "BUDGET_CHANGED" || ev.entityType === "BUDGET") {
      return {
        label: "Budget updated",
        badgeClass: "bg-purple-50 text-purple-700 border-purple-200",
        icon: SlidersHorizontal,
        iconColor: "text-purple-600",
      };
    }
    if (type === "PLAN_CREATED" || ev.entityType === "PLAN") {
      return {
        label: "Plan ready",
        badgeClass: "bg-orange-50 text-orange-700 border-orange-200",
        icon: UtensilsCrossed,
        iconColor: "text-[#FF9900]",
      };
    }
    if (type === "INVENTORY_UPDATED" || ev.entityType === "PANTRY") {
      return {
        label: "Pantry updated",
        badgeClass: "bg-teal-50 text-teal-700 border-teal-200",
        icon: Package,
        iconColor: "text-teal-600",
      };
    }

    return {
      label: dec || "System event",
      badgeClass: "bg-neutral-100 text-neutral-700 border-neutral-200",
      icon: Clock,
      iconColor: "text-neutral-500",
    };
  };

  const autoCount = events.filter((e) => e.decision === "AUTO" || e.type === "PURCHASE_COMPLETED").length;
  const restraintCount = events.filter((e) => e.decision === "DO_NOTHING" || e.type === "AUTONOMOUS_ACTION").length;
  const askCount = events.filter((e) => e.decision === "ASK" || e.type === "PURCHASE_WAITING_APPROVAL").length;

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-neutral-900 font-sans pb-24 pt-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-neutral-200 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
                Audit Trail
              </span>
              <span className="text-xs text-neutral-500">Autonomous Household History</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-neutral-900">
              Recently Taken Care Of
            </h1>
            <p className="text-sm text-neutral-600 mt-1">
              Real-time record of NOVA&apos;s autonomous purchases, restraint decisions, budget checks, and plans.
            </p>
          </div>

          <button
            onClick={fetchActivity}
            disabled={loading}
            className="self-start sm:self-auto inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-neutral-300 bg-white text-xs font-semibold text-neutral-700 hover:bg-neutral-50 transition-colors shadow-2xs cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {/* High-Level Intelligence Summary Cards */}
        <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-6">
          <div className="bg-white p-3.5 sm:p-4 rounded-xl border border-neutral-200/80 shadow-2xs">
            <div className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider mb-1">
              Taken Care Of
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black text-emerald-700">{autoCount}</span>
              <span className="text-xs text-emerald-600 font-medium">auto-ordered</span>
            </div>
          </div>

          <div className="bg-white p-3.5 sm:p-4 rounded-xl border border-neutral-200/80 shadow-2xs">
            <div className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider mb-1">
              Restraint Applied
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black text-blue-700">{restraintCount}</span>
              <span className="text-xs text-blue-600 font-medium">held off</span>
            </div>
          </div>

          <div className="bg-white p-3.5 sm:p-4 rounded-xl border border-neutral-200/80 shadow-2xs">
            <div className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider mb-1">
              Needs Approval
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl font-black text-amber-700">{askCount}</span>
              <span className="text-xs text-amber-600 font-medium">awaiting review</span>
            </div>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-3 mb-6 no-scrollbar">
          {[
            { key: "ALL", label: "All Activity" },
            { key: "AUTO", label: `Taken Care Of (${autoCount})` },
            { key: "ASK", label: `Needs Input (${askCount})` },
            { key: "INVENTORY", label: "Inventory & Restraint" },
            { key: "PLANS", label: "Plans" },
            { key: "BUDGET", label: "Budget" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveFilter(tab.key)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                activeFilter === tab.key
                  ? "bg-neutral-900 text-white shadow-xs"
                  : "bg-white text-neutral-600 border border-neutral-200 hover:bg-neutral-100 hover:text-neutral-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm mb-6 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && events.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-neutral-500">
            <div className="w-8 h-8 border-3 border-neutral-300 border-t-[#FF9900] rounded-full animate-spin mb-3"></div>
            <p className="text-sm font-medium">Fetching household intelligence records...</p>
          </div>
        )}

        {/* Event List */}
        {!loading && filteredEvents.length === 0 && (
          <div className="bg-white rounded-2xl border border-neutral-200 p-12 text-center max-w-lg mx-auto shadow-2xs">
            <div className="w-12 h-12 rounded-full bg-amber-50 text-[#FF9900] flex items-center justify-center mx-auto mb-3">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-neutral-900 mb-1">Nothing here yet</h3>
            <p className="text-sm text-neutral-600 mb-5">
              Once NOVA takes care of an everyday replenishment or applies restraint, you&apos;ll see the plain-English explanation right here.
            </p>
            <div className="p-3 bg-neutral-50 rounded-xl border border-neutral-200/80 text-xs text-neutral-600 text-left">
              <p className="font-semibold text-neutral-800 mb-1">Try asking NOVA:</p>
              <p className="italic text-neutral-600">&ldquo;I want to make Maggi tonight.&rdquo;</p>
              <p className="italic text-neutral-600">&ldquo;Do we have enough cooking oil?&rdquo;</p>
            </div>
          </div>
        )}

        {/* Sections: Today, Yesterday, Earlier */}
        <div className="space-y-8">
          {today.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">Today</span>
                <div className="h-px bg-neutral-200 flex-1"></div>
              </div>
              <div className="space-y-3">
                {today.map((ev) => (
                  <EventCard
                    key={ev.id}
                    event={ev}
                    badge={getDecisionBadge(ev)}
                    timeStr={formatRelativeTime(ev.timestamp)}
                    expanded={!!expandedIds[ev.id]}
                    onToggle={() => toggleExpand(ev.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {yesterday.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">Yesterday</span>
                <div className="h-px bg-neutral-200 flex-1"></div>
              </div>
              <div className="space-y-3">
                {yesterday.map((ev) => (
                  <EventCard
                    key={ev.id}
                    event={ev}
                    badge={getDecisionBadge(ev)}
                    timeStr={formatRelativeTime(ev.timestamp)}
                    expanded={!!expandedIds[ev.id]}
                    onToggle={() => toggleExpand(ev.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {earlier.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">Earlier</span>
                <div className="h-px bg-neutral-200 flex-1"></div>
              </div>
              <div className="space-y-3">
                {earlier.map((ev) => (
                  <EventCard
                    key={ev.id}
                    event={ev}
                    badge={getDecisionBadge(ev)}
                    timeStr={formatRelativeTime(ev.timestamp)}
                    expanded={!!expandedIds[ev.id]}
                    onToggle={() => toggleExpand(ev.id)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function EventCard({
  event,
  badge,
  timeStr,
  expanded,
  onToggle,
}: {
  event: ActivityEvent;
  badge: { label: string; badgeClass: string; icon: any; iconColor: string };
  timeStr: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  const Icon = badge.icon;
  const cost = event.cost ?? (event.metadata?.cost || null);

  return (
    <div className="bg-white rounded-xl border border-neutral-200/90 shadow-2xs transition-all hover:border-neutral-300 overflow-hidden">
      <div className="p-4 sm:p-5">
        <div className="flex items-start justify-between gap-3">
          {/* Main Info */}
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="mt-0.5 w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center shrink-0">
              <Icon className={`w-4 h-4 ${badge.iconColor}`} />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap mb-1">
                <span className={`inline-flex items-center text-[11px] font-bold px-2 py-0.5 rounded-full border ${badge.badgeClass}`}>
                  {badge.label}
                </span>
                <span className="text-xs text-neutral-400 font-medium">{timeStr}</span>
                {cost !== null && cost > 0 && (
                  <span className="text-xs font-bold text-neutral-900 bg-neutral-100 px-2 py-0.5 rounded-full">
                    ₹{cost}
                  </span>
                )}
              </div>

              <h3 className="text-sm sm:text-base font-bold text-neutral-900 leading-snug">
                {event.title}
              </h3>
              <p className="text-xs sm:text-sm text-neutral-600 mt-1 leading-relaxed">
                {event.description}
              </p>
            </div>
          </div>

          {/* Expand "Why?" Button */}
          {event.reasons && event.reasons.length > 0 && (
            <button
              onClick={onToggle}
              className="inline-flex items-center gap-1 text-xs font-semibold text-neutral-600 hover:text-neutral-900 bg-neutral-50 hover:bg-neutral-100 px-2.5 py-1.5 rounded-lg border border-neutral-200 transition-colors shrink-0 cursor-pointer"
            >
              <span>Why?</span>
              {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* Expandable Explanation & State Impact */}
        {expanded && event.reasons && event.reasons.length > 0 && (
          <div className="mt-4 pt-3.5 border-t border-neutral-100 text-xs">
            <div className="bg-[#FAF9F6] rounded-lg p-3 border border-neutral-200/70 mb-3">
              <p className="font-bold text-neutral-800 mb-2 uppercase tracking-wider text-[10px]">
                Deterministic Decision Rationale
              </p>
              <ul className="space-y-1.5 text-neutral-700">
                {event.reasons.map((r, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-500 font-bold">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Context Navigation Link */}
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-2">
                {event.entityType === "PRODUCT" && (
                  <Link
                    href="/orders"
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-neutral-700 hover:text-neutral-900 underline"
                  >
                    View in Orders <ArrowRight className="w-3 h-3" />
                  </Link>
                )}
                {event.entityType === "PANTRY" && (
                  <Link
                    href="/pantry"
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-neutral-700 hover:text-neutral-900 underline"
                  >
                    View in Pantry <ArrowRight className="w-3 h-3" />
                  </Link>
                )}
                {event.entityType === "BUDGET" && (
                  <Link
                    href="/budget"
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-neutral-700 hover:text-neutral-900 underline"
                  >
                    Manage Budget <ArrowRight className="w-3 h-3" />
                  </Link>
                )}
              </div>

              {event.metadata?.order_id && (
                <span className="text-[10px] text-neutral-400 font-mono">
                  Ref: {event.metadata.order_id}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
