"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useRef, useCallback } from "react";
import BudgetModal from "@/components/BudgetModal";
import {
  Package,
  UtensilsCrossed,
  Search,
  ArrowRight,
  ChevronDown,
  Wallet,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  RotateCcw,
  SlidersHorizontal,
  Info,
  Layers,
  ShoppingBag,
  ExternalLink,
  ShieldCheck,
  User,
  X
} from "lucide-react";

interface SuggestionItem {
  type: "budget" | "household" | "plan" | "product";
  title: string;
  subtitle?: string;
  badge?: string;
  badgeColor?: string;
  price?: number;
  imageUrl?: string;
  href: string;
}

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const [cartCount, setCartCount] = useState(0);
  const [budgetRemaining, setBudgetRemaining] = useState<number | null>(null);
  const [budgetModalOpen, setBudgetModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [swiggyStatus, setSwiggyStatus] = useState<{
    authenticated: boolean;
    active_address?: any;
    mode?: string;
  }>({ authenticated: false });

  // Navigation Dropdown
  const [moreMenuOpen, setMoreMenuOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const moreMenuRef = useRef<HTMLDivElement>(null);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  // Search suggestions & keyboard navigation state
  const [suggestions, setSuggestions] = useState<{
    household_context?: any;
    budget_context?: any;
    plans?: any[];
    products?: any[];
  } | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);

  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const fetchHeaderData = useCallback(() => {
    Promise.all([
      fetch("/api/cart").then((r) => r.json()).catch(() => ({ items: [] })),
      fetch("/api/budget").then((r) => r.json()).catch(() => ({ remaining: null })),
      fetch("/api/auth/swiggy/status").then((r) => r.json()).catch(() => ({ authenticated: false })),
    ]).then(([cart, bud, swiggy]) => {
      setCartCount(cart?.items?.length || 0);
      setBudgetRemaining(bud?.remaining ?? null);
      setSwiggyStatus(swiggy || { authenticated: false });
    });
  }, []);

  useEffect(() => {
    fetchHeaderData();
    const refresh = () => fetchHeaderData();
    window.addEventListener("cart-updated", refresh);
    window.addEventListener("swiggy-updated", refresh);
    window.addEventListener("household-updated", refresh);
    window.addEventListener("budget-updated", refresh);

    return () => {
      window.removeEventListener("cart-updated", refresh);
      window.removeEventListener("swiggy-updated", refresh);
      window.removeEventListener("household-updated", refresh);
      window.removeEventListener("budget-updated", refresh);
    };
  }, [fetchHeaderData, pathname]);

  // Click outside listener for dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
      if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
        setMoreMenuOpen(false);
      }
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setProfileMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Build flattened suggestion items for keyboard navigation
  const flatItems: SuggestionItem[] = [];
  if (suggestions) {
    if (suggestions.budget_context) {
      flatItems.push({
        type: "budget",
        title: `Budget: ₹${suggestions.budget_context.remaining?.toLocaleString("en-IN")} remaining`,
        subtitle: `Monthly budget of ₹${suggestions.budget_context.monthly?.toLocaleString("en-IN")}`,
        badge: "Budget",
        badgeColor: "bg-emerald-100 text-emerald-800",
        href: "/budget",
      });
    }
    if (suggestions.household_context) {
      const hc = suggestions.household_context;
      flatItems.push({
        type: "household",
        title: hc.item_name,
        subtitle: `${hc.quantity} ${hc.unit} remaining (~${hc.days_remaining}d supply) · ${hc.suggested_action || ""}`,
        badge: hc.status_headline || (hc.urgency === "URGENT" ? "Running low" : "All sorted"),
        badgeColor: hc.urgency === "URGENT" ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700",
        href: `/pantry`,
      });
    }
    if (suggestions.plans && suggestions.plans.length > 0) {
      suggestions.plans.forEach((p) => {
        flatItems.push({
          type: "plan",
          title: p.title,
          subtitle: p.description,
          badge: "Tonight's plan",
          badgeColor: "bg-amber-100 text-amber-800",
          href: "/plans",
        });
      });
    }
    if (suggestions.products && suggestions.products.length > 0) {
      suggestions.products.slice(0, 4).forEach((prod: any) => {
        flatItems.push({
          type: "product",
          title: prod.name,
          subtitle: `${prod.brand ? prod.brand + " · " : ""}${prod.pack_size || prod.unit || ""}`,
          price: prod.price,
          imageUrl: prod.imageUrl,
          badge: "Product",
          badgeColor: "bg-neutral-100 text-neutral-600",
          href: `/search?q=${encodeURIComponent(prod.name)}`,
        });
      });
    }
  }

  const handleInputChange = (val: string) => {
    setSearchQuery(val);
    setSelectedIndex(-1);
    if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);

    if (!val.trim() || val.trim().length < 2) {
      setSuggestions(null);
      setShowSuggestions(false);
      return;
    }

    setSearchLoading(true);
    setShowSuggestions(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(val.trim())}&limit=5`);
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data);
        }
      } catch (err) {
        console.error("Search suggestion fetch failed:", err);
      } finally {
        setSearchLoading(false);
      }
    }, 180);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setShowSuggestions(false);
      setSelectedIndex(-1);
      return;
    }

    if (!showSuggestions || flatItems.length === 0) {
      if (e.key === "Enter" && searchQuery.trim()) {
        setShowSuggestions(false);
        router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      }
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < flatItems.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : flatItems.length - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      setShowSuggestions(false);
      if (selectedIndex >= 0 && selectedIndex < flatItems.length) {
        const item = flatItems[selectedIndex];
        router.push(item.href);
      } else if (searchQuery.trim()) {
        router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      }
    }
  };

  const handleSelectSuggestion = (href: string) => {
    setShowSuggestions(false);
    setSelectedIndex(-1);
    router.push(href);
  };

  const handleResetDemo = async () => {
    await fetch("/api/demo/reset", { method: "POST" });
    setProfileMenuOpen(false);
    window.dispatchEvent(new Event("household-updated"));
    window.dispatchEvent(new Event("cart-updated"));
    window.dispatchEvent(new Event("budget-updated"));
    router.push("/");
    router.refresh();
  };

  const primaryNav = [
    { href: "/", label: "Today" },
    { href: "/pantry", label: "Pantry" },
    { href: "/store", label: "Store" },
    { href: "/plans", label: "Plans" },
    { href: "/orders", label: "Orders" },
    { href: "/budget", label: "Budget" },
  ];

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md text-neutral-900 border-b border-neutral-200 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
          
          {/* ── Brand & Primary Navigation ───────────────────────────── */}
          <div className="flex items-center gap-6 shrink-0">
            <Link href="/" className="flex items-center group shrink-0" aria-label="NOVA Home">
              <img
                src="/logo.png"
                alt="NOVA"
                className="h-8 sm:h-9 w-auto object-contain transition-transform group-hover:opacity-90"
              />
            </Link>

            {/* Main Tabs */}
            <nav className="hidden md:flex items-center gap-1">
              {primaryNav.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-neutral-900 text-white shadow-xs font-bold"
                        : "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100"
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}

              {/* More Dropdown */}
              <div ref={moreMenuRef} className="relative">
                <button
                  type="button"
                  onClick={() => setMoreMenuOpen(!moreMenuOpen)}
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-all ${
                    moreMenuOpen || ["/rules", "/memory", "/activity", "/autopilot", "/how-it-works"].includes(pathname)
                      ? "bg-neutral-900 text-white"
                      : "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100"
                  }`}
                >
                  <span>More</span>
                  <ChevronDown className={`w-3.5 h-3.5 transition-transform ${moreMenuOpen ? "rotate-180" : ""}`} />
                </button>

                {moreMenuOpen && (
                  <div className="absolute left-0 top-full mt-2 w-52 bg-white text-neutral-900 rounded-xl shadow-xl border border-neutral-200 py-1.5 z-50 text-xs font-medium">
                    <Link
                      href="/rules"
                      onClick={() => setMoreMenuOpen(false)}
                      className="flex items-center gap-2.5 px-3.5 py-2 hover:bg-neutral-100 text-neutral-800"
                    >
                      <ShieldCheck className="w-4 h-4 text-neutral-500" />
                      <span>Rules &amp; Autopilot Limits</span>
                    </Link>
                    <Link
                      href="/memory"
                      onClick={() => setMoreMenuOpen(false)}
                      className="flex items-center gap-2.5 px-3.5 py-2 hover:bg-neutral-100 text-neutral-800"
                    >
                      <Sparkles className="w-4 h-4 text-neutral-500" />
                      <span>Household Memory</span>
                    </Link>
                    <Link
                      href="/activity"
                      onClick={() => setMoreMenuOpen(false)}
                      className="flex items-center gap-2.5 px-3.5 py-2 hover:bg-neutral-100 text-neutral-800"
                    >
                      <Clock className="w-4 h-4 text-neutral-500" />
                      <span>Activity &amp; Audit Trail</span>
                    </Link>
                    <Link
                      href="/autopilot"
                      onClick={() => setMoreMenuOpen(false)}
                      className="flex items-center gap-2.5 px-3.5 py-2 hover:bg-neutral-100 text-neutral-800"
                    >
                      <SlidersHorizontal className="w-4 h-4 text-neutral-500" />
                      <span>Autopilot Controls</span>
                    </Link>

                    <div className="my-1 border-t border-neutral-100" />

                    <Link
                      href="/how-it-works"
                      onClick={() => setMoreMenuOpen(false)}
                      className="flex items-center justify-between px-3.5 py-2 bg-amber-50/70 hover:bg-amber-100/70 text-amber-900 font-semibold"
                    >
                      <div className="flex items-center gap-2">
                        <Layers className="w-4 h-4 text-amber-700" />
                        <span>How NOVA Works</span>
                      </div>
                      <span className="text-[9px] bg-amber-200/80 text-amber-900 px-1.5 py-0.5 rounded font-bold uppercase">
                        System
                      </span>
                    </Link>
                  </div>
                )}
              </div>
            </nav>
          </div>

          {/* ── Center: Search Bar with Universal Intelligence ───────── */}
          <div ref={searchContainerRef} className="flex-1 max-w-md relative">
            <div className="relative flex items-center">
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => handleInputChange(e.target.value)}
                onFocus={() => {
                  if (suggestions) setShowSuggestions(true);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Search pantry, plans, products, budget..."
                className="w-full bg-neutral-100 text-neutral-900 placeholder-neutral-400 text-xs rounded-xl pl-9 pr-8 py-2 border border-neutral-200 focus:outline-none focus:border-amber-500 focus:bg-white focus:ring-1 focus:ring-amber-500/30 transition-all shadow-2xs"
              />
              <div className="absolute left-3 pointer-events-none text-neutral-400">
                <Search className="w-3.5 h-3.5" />
              </div>
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery("");
                    setSuggestions(null);
                    setShowSuggestions(false);
                  }}
                  className="absolute right-2.5 text-neutral-400 hover:text-neutral-700"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Interactive Suggestions Dropdown */}
            {showSuggestions && suggestions && flatItems.length > 0 && (
              <div className="absolute left-0 right-0 top-full mt-2 bg-white text-neutral-900 rounded-2xl shadow-2xl border border-neutral-200 overflow-hidden z-50 text-left">
                {/* 1. Household Context Preview */}
                {suggestions.household_context && (
                  <div
                    onClick={() => handleSelectSuggestion("/pantry")}
                    className={`p-3 border-b border-neutral-100 cursor-pointer transition-colors ${
                      selectedIndex === flatItems.findIndex((i) => i.type === "household")
                        ? "bg-amber-50"
                        : "hover:bg-neutral-50"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-amber-900">
                        <Package className="w-3.5 h-3.5 text-amber-700" />
                        <span>Your Pantry</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        suggestions.household_context.urgency === "URGENT"
                          ? "bg-red-100 text-red-700"
                          : "bg-emerald-100 text-emerald-800"
                      }`}>
                        {suggestions.household_context.status_headline || suggestions.household_context.status}
                      </span>
                    </div>
                    <p className="text-sm font-bold text-neutral-900">
                      {suggestions.household_context.item_name}
                    </p>
                    <p className="text-xs text-neutral-600 mt-0.5">
                      ~{suggestions.household_context.quantity} {suggestions.household_context.unit} remaining (~{suggestions.household_context.days_remaining} days)
                    </p>
                    {suggestions.household_context.usual_purchase && (
                      <p className="text-[11px] text-amber-800 font-medium mt-1">
                        Usual purchase: {suggestions.household_context.usual_purchase}
                      </p>
                    )}
                  </div>
                )}

                {/* 2. Budget Context Preview */}
                {suggestions.budget_context && (
                  <div
                    onClick={() => handleSelectSuggestion("/budget")}
                    className={`p-3 border-b border-neutral-100 cursor-pointer transition-colors ${
                      selectedIndex === flatItems.findIndex((i) => i.type === "budget")
                        ? "bg-emerald-50"
                        : "hover:bg-neutral-50"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-emerald-900">
                        <Wallet className="w-3.5 h-3.5 text-emerald-600" />
                        <span>Household Budget</span>
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                        Active
                      </span>
                    </div>
                    <p className="text-sm font-bold text-neutral-900">
                      ₹{suggestions.budget_context.remaining?.toLocaleString("en-IN")} remaining
                    </p>
                    <p className="text-xs text-neutral-500 mt-0.5">
                      of ₹{suggestions.budget_context.monthly?.toLocaleString("en-IN")} monthly budget
                    </p>
                  </div>
                )}

                {/* 3. Suggested Plans */}
                {suggestions.plans && suggestions.plans.length > 0 && (
                  <div className="p-2 border-b border-neutral-100">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 px-2 py-1 flex items-center gap-1">
                      <UtensilsCrossed className="w-3 h-3 text-amber-500" />
                      Tonight&apos;s Plans
                    </p>
                    {suggestions.plans.map((p) => {
                      const idx = flatItems.findIndex((i) => i.title === p.title);
                      return (
                        <div
                          key={p.plan_id}
                          onClick={() => handleSelectSuggestion("/plans")}
                          className={`p-2 rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                            selectedIndex === idx ? "bg-amber-50" : "hover:bg-neutral-50"
                          }`}
                        >
                          <div>
                            <p className="text-xs font-bold text-neutral-900">{p.title}</p>
                            <p className="text-[11px] text-neutral-500">{p.description}</p>
                          </div>
                          <ArrowRight className="w-3.5 h-3.5 text-neutral-400" />
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* 4. Products */}
                {suggestions.products && suggestions.products.length > 0 && (
                  <div className="p-2">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 px-2 py-1 flex items-center gap-1">
                      <ShoppingBag className="w-3 h-3 text-neutral-400" />
                      Available Products
                    </p>
                    {suggestions.products.slice(0, 4).map((prod: any) => {
                      const idx = flatItems.findIndex((i) => i.title === prod.name);
                      return (
                        <div
                          key={prod.id}
                          onClick={() => handleSelectSuggestion(`/search?q=${encodeURIComponent(prod.name)}`)}
                          className={`p-2 rounded-lg cursor-pointer flex items-center justify-between transition-colors ${
                            selectedIndex === idx ? "bg-amber-50" : "hover:bg-neutral-50"
                          }`}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            {prod.imageUrl ? (
                              <img
                                src={prod.imageUrl}
                                alt=""
                                className="w-7 h-7 object-contain rounded bg-neutral-50 shrink-0"
                              />
                            ) : (
                              <div className="w-7 h-7 rounded bg-neutral-100 flex items-center justify-center shrink-0">
                                <Package className="w-3.5 h-3.5 text-neutral-400" />
                              </div>
                            )}
                            <div className="truncate">
                              <p className="text-xs font-semibold text-neutral-900 truncate">{prod.name}</p>
                              <p className="text-[11px] text-neutral-400">{prod.pack_size || prod.unit || ""}</p>
                            </div>
                          </div>
                          <span className="text-xs font-bold text-neutral-900 shrink-0 pl-2">
                            ₹{prod.price}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Bottom Bar */}
                <div
                  onClick={() => handleSelectSuggestion(`/search?q=${encodeURIComponent(searchQuery)}`)}
                  className="p-2.5 bg-neutral-50 border-t border-neutral-100 hover:bg-neutral-100 text-xs font-semibold text-neutral-700 flex items-center justify-between cursor-pointer"
                >
                  <span>See all results for &ldquo;<span className="text-amber-600">{searchQuery}</span>&rdquo;</span>
                  <span className="text-[10px] text-neutral-400 font-normal">Press Enter</span>
                </div>
              </div>
            )}
          </div>

          {/* ── Right Section: Budget, Swiggy Pill, Cart, Profile ────── */}
          <div className="flex items-center gap-2 shrink-0">
            
            {/* Budget Indicator */}
            {budgetRemaining !== null && (
              <button
                type="button"
                onClick={() => setBudgetModalOpen(true)}
                className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-neutral-100 hover:bg-neutral-200/80 border border-neutral-200 text-xs font-medium transition-colors"
                title="View and edit household budget"
              >
                <Wallet className="w-3.5 h-3.5 text-amber-600" />
                <span className="text-neutral-600">Budget:</span>
                <span className="font-bold text-neutral-900">₹{budgetRemaining.toLocaleString("en-IN")}</span>
              </button>
            )}

            {/* Cart Link */}
            <Link
              href="/cart"
              className="relative p-2 rounded-lg text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 transition-colors"
              aria-label="Household Cart"
            >
              <ShoppingBag className="w-5 h-5" />
              {cartCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-amber-400 text-neutral-950 text-[10px] font-black rounded-full flex items-center justify-center leading-none">
                  {cartCount}
                </span>
              )}
            </Link>

            {/* Profile / Demo Settings Dropdown */}
            <div ref={profileMenuRef} className="relative">
              <button
                type="button"
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="w-8 h-8 rounded-full bg-neutral-100 hover:bg-neutral-200 text-neutral-700 flex items-center justify-center border border-neutral-200 transition-colors"
                aria-label="Household Settings"
              >
                <User className="w-4 h-4 text-neutral-600" />
              </button>

              {profileMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-white text-neutral-900 rounded-xl shadow-xl border border-neutral-200 py-1.5 z-50 text-xs font-medium">
                  <div className="px-3.5 py-2 border-b border-neutral-100">
                    <p className="font-bold text-neutral-900 text-xs">Household Autopilot</p>
                    <p className="text-[10px] text-neutral-500">Family of 4</p>
                  </div>
                  <Link
                    href="/rules"
                    onClick={() => setProfileMenuOpen(false)}
                    className="flex items-center gap-2 px-3.5 py-2 hover:bg-neutral-100 text-neutral-800"
                  >
                    <SlidersHorizontal className="w-3.5 h-3.5 text-neutral-500" />
                    <span>Autopilot Rules</span>
                  </Link>
                  <Link
                    href="/how-it-works"
                    onClick={() => setProfileMenuOpen(false)}
                    className="flex items-center gap-2 px-3.5 py-2 hover:bg-neutral-100 text-neutral-800"
                  >
                    <Layers className="w-3.5 h-3.5 text-neutral-500" />
                    <span>System Architecture</span>
                  </Link>
                  <div className="my-1 border-t border-neutral-100" />
                  <button
                    type="button"
                    onClick={handleResetDemo}
                    className="w-full flex items-center gap-2 px-3.5 py-2 text-left hover:bg-red-50 text-red-600 font-semibold cursor-pointer"
                  >
                    <RotateCcw className="w-3.5 h-3.5 text-red-500" />
                    <span>Reset Demo State</span>
                  </button>
                </div>
              )}
            </div>

          </div>

        </div>
      </header>

      {/* Spacer for 64px fixed header */}
      <div className="h-16" />

      {/* Budget Editor Modal */}
      <BudgetModal
        isOpen={budgetModalOpen}
        onClose={() => setBudgetModalOpen(false)}
      />
    </>
  );
}
