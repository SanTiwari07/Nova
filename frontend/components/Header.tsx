"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import BudgetModal from "@/components/BudgetModal";
import {
  SlidersHorizontal,
  Sparkles,
  Bot,
  Package,
  UtensilsCrossed,
  Search,
  ArrowRight
} from "lucide-react";

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const [cartCount, setCartCount] = useState(0);
  const [budgetRemaining, setBudgetRemaining] = useState<number | null>(null);
  const [budgetModalOpen, setBudgetModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchCategory, setSearchCategory] = useState("All");
  const [categories, setCategories] = useState<string[]>([]);
  const [swiggyStatus, setSwiggyStatus] = useState<{
    authenticated: boolean;
    active_address?: any;
    active_address_id?: string;
    mode?: string;
  }>({ authenticated: false });

  // Interactive suggestions state
  const [suggestions, setSuggestions] = useState<{
    household_context?: any;
    plans?: any[];
    products?: any[];
  } | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  const fetchHeaderData = () => {
    Promise.all([
      fetch("/api/cart").then((r) => r.json()).catch(() => ({ items: [] })),
      fetch("/api/budget").then((r) => r.json()).catch(() => ({ remaining: null })),
      fetch("/api/products/categories").then((r) => r.json()).catch(() => []),
      fetch("/api/auth/swiggy/status").then((r) => r.json()).catch(() => ({ authenticated: false })),
    ]).then(([cart, bud, cats, swiggy]) => {
      setCartCount(cart?.items?.length || 0);
      setBudgetRemaining(bud?.remaining ?? null);
      setCategories(cats || []);
      setSwiggyStatus(swiggy || { authenticated: false });
    });
  };

  const handleConnectSwiggy = async () => {
    try {
      const res = await fetch("/api/auth/swiggy/connect-demo", { method: "POST" });
      const data = await res.json();
      if (data && data.authenticated) {
        setSwiggyStatus(data);
        window.dispatchEvent(new Event("swiggy-updated"));
        router.refresh();
      }
    } catch (e) {
      window.location.href = "/api/auth/swiggy/login?redirect=true";
    }
  };

  useEffect(() => {
    const isSwiggyConnectedParam = typeof window !== "undefined" && window.location.search.includes("swiggy_connected");
    if (isSwiggyConnectedParam) {
      fetch("/api/auth/swiggy/status?auto_connect=true")
        .then((r) => r.json())
        .then((swiggy) => {
          if (swiggy) setSwiggyStatus(swiggy);
          window.dispatchEvent(new Event("swiggy-updated"));
        })
        .catch(() => {});
    }

    fetchHeaderData();
    window.addEventListener("cart-updated", fetchHeaderData);
    window.addEventListener("swiggy-updated", fetchHeaderData);
    window.addEventListener("household-updated", fetchHeaderData);
    window.addEventListener("budget-updated", fetchHeaderData);

    return () => {
      window.removeEventListener("cart-updated", fetchHeaderData);
      window.removeEventListener("swiggy-updated", fetchHeaderData);
      window.removeEventListener("household-updated", fetchHeaderData);
      window.removeEventListener("budget-updated", fetchHeaderData);
    };
  }, [pathname]);

  // Click outside to close search suggestions
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleInputChange = (val: string) => {
    setSearchQuery(val);
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
        const catParam = searchCategory !== "All" ? `&category=${encodeURIComponent(searchCategory)}` : "";
        const res = await fetch(`/api/search?q=${encodeURIComponent(val.trim())}&limit=5${catParam}`);
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data);
        }
      } catch (err) {
        console.error("Search suggestion fetch failed:", err);
      } finally {
        setSearchLoading(false);
      }
    }, 200);
  };

  const navigateToSearch = (query: string) => {
    setShowSuggestions(false);
    setSearchQuery(query);
    const params = new URLSearchParams({ q: query.trim() });
    if (searchCategory !== "All") params.set("category", searchCategory);
    router.push(`/search?${params.toString()}`);
  };

  const handleDisconnectSwiggy = async () => {
    await fetch("/api/auth/swiggy/disconnect", { method: "POST" });
    fetchHeaderData();
    router.refresh();
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    if (searchQuery.trim()) {
      const params = new URLSearchParams({ q: searchQuery.trim() });
      if (searchCategory !== "All") params.set("category", searchCategory);
      router.push(`/search?${params.toString()}`);
    }
  };

  const handleReset = async () => {
    await fetch("/api/demo/reset", { method: "POST" });
    router.push("/");
    router.refresh();
  };


  const secondaryNavLinks = [
    { href: "/", label: "Today" },
    { href: "/pantry", label: "Pantry" },
    { href: "/orders", label: "Orders" },
    { href: "/budget", label: "Budget" },
    { href: "/rules", label: "Rules" },
    { href: "/store", label: "Store" },
    { href: "/autopilot", label: "Autopilot" },
    { href: "/nova-cart", label: "NOVA Cart" },
    { href: "/activity", label: "Activity" },
    { href: "/price-watch", label: "Price Watch" },
    { href: "/memory", label: "Memory" },
  ];

  return (
    <>
      {/* PRIMARY HEADER */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#131921] text-white">
        <div className="max-w-[1500px] mx-auto px-3 h-14 flex items-center gap-2">
          {/* NOVA Logo */}
          <Link
            href="/"
            className="flex items-center gap-0.5 shrink-0 px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all"
          >
            <span className="text-[#FF9900] font-black text-2xl leading-none">N</span>
            <span className="text-white font-black text-2xl leading-none">OVA</span>
          </Link>

          {/* Delivery Location */}
          <div className="hidden md:flex flex-col shrink-0 px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all cursor-pointer min-w-[80px]">
            <span className="text-[11px] text-neutral-300 leading-none">Delivering to</span>
            <div className="flex items-center gap-1">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-white shrink-0">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
              <span className="text-xs font-bold text-white truncate max-w-[130px]">
                {swiggyStatus.active_address?.addressTag || swiggyStatus.active_address?.label || swiggyStatus.active_address?.addressCategory || (swiggyStatus.authenticated ? "Swiggy Home" : "Connect Swiggy")}
              </span>
            </div>
          </div>

          {/* Search Bar Container */}
          <div ref={searchContainerRef} className="flex-1 relative">
            <form onSubmit={handleSearch} className="flex h-10 rounded-sm overflow-hidden shadow-sm">
              {/* Category Selector */}
              <select
                value={searchCategory}
                onChange={(e) => setSearchCategory(e.target.value)}
                className="bg-neutral-200 text-neutral-700 text-xs font-medium px-2 border-r border-neutral-300 outline-none hover:bg-neutral-300 transition-colors hidden sm:block shrink-0 cursor-pointer"
                style={{ minWidth: "80px", maxWidth: "120px" }}
              >
                <option value="All">All</option>
                {categories.slice(0, 20).map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>

              {/* Text Input */}
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => handleInputChange(e.target.value)}
                onFocus={() => {
                  if (suggestions) setShowSuggestions(true);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Escape") setShowSuggestions(false);
                }}
                placeholder="Search NOVA for pantry staples, meals, products..."
                className="flex-1 text-neutral-900 px-3 text-sm outline-none bg-white placeholder:text-neutral-400"
                id="nova-search-input"
                autoComplete="off"
              />

              {/* Search Button */}
              <button
                type="submit"
                className="bg-[#FF9900] hover:bg-[#e68900] px-4 flex items-center justify-center transition-colors shrink-0 cursor-pointer"
                aria-label="Search"
              >
                {searchLoading ? (
                  <div className="w-4 h-4 border-2 border-neutral-900 border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#131921" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                  </svg>
                )}
              </button>
            </form>

            {/* Interactive Suggestions Dropdown */}
            {showSuggestions && suggestions && (
              <div className="absolute left-0 right-0 top-full mt-1.5 bg-white text-neutral-900 rounded-xl shadow-2xl border border-neutral-200 overflow-hidden z-50 text-left">
                {/* 1. Household Context Preview */}
                {suggestions.household_context && (
                  <div
                    onClick={() => navigateToSearch(suggestions.household_context.item_name || searchQuery)}
                    className="p-3 bg-amber-50/70 border-b border-amber-100/80 hover:bg-amber-100/60 cursor-pointer transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900">
                        <Package className="w-3.5 h-3.5 text-amber-700" />
                        <span>Household & Pantry Status</span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        suggestions.household_context.urgency === "URGENT"
                          ? "bg-red-100 text-red-700"
                          : suggestions.household_context.urgency === "UPCOMING"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-emerald-100 text-emerald-800"
                      }`}>
                        {suggestions.household_context.status}
                      </span>
                    </div>
                    <div className="text-sm font-bold text-neutral-900">
                      {suggestions.household_context.item_name}
                    </div>
                    <div className="text-xs text-neutral-600 mt-0.5">
                      ~{suggestions.household_context.quantity} {suggestions.household_context.unit} remaining ({suggestions.household_context.days_remaining} days of supply) · <span className="text-amber-800 font-medium">{suggestions.household_context.suggested_action}</span>
                    </div>
                  </div>
                )}

                {/* 2. Suggested Plans / Recipes */}
                {suggestions.plans && suggestions.plans.length > 0 && (
                  <div className="p-2.5 border-b border-neutral-100">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 px-2 mb-1.5 flex items-center gap-1">
                      <UtensilsCrossed className="w-3 h-3 text-[#FF9900]" />
                      Household Meal Plans
                    </div>
                    {suggestions.plans.map((p) => (
                      <div
                        key={p.plan_id}
                        onClick={() => navigateToSearch(p.meal || p.title)}
                        className="p-2 rounded-lg hover:bg-neutral-50 cursor-pointer flex items-center justify-between transition-colors"
                      >
                        <div>
                          <div className="text-xs font-bold text-neutral-900">{p.title}</div>
                          <div className="text-[11px] text-neutral-500">{p.description}</div>
                        </div>
                        <ArrowRight className="w-3.5 h-3.5 text-neutral-400" />
                      </div>
                    ))}
                  </div>
                )}

                {/* 3. Matching Products */}
                {suggestions.products && suggestions.products.length > 0 && (
                  <div className="p-2.5">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-neutral-400 px-2 mb-1.5 flex items-center gap-1">
                      <Search className="w-3 h-3" />
                      Available Products
                    </div>
                    {suggestions.products.slice(0, 4).map((prod: any) => (
                      <div
                        key={prod.id || prod.productId}
                        onClick={() => navigateToSearch(prod.name)}
                        className="p-2 rounded-lg hover:bg-neutral-50 cursor-pointer flex items-center justify-between transition-colors"
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          {prod.imageUrl && (
                            <img
                              src={prod.imageUrl}
                              alt=""
                              className="w-7 h-7 object-contain rounded bg-neutral-50 shrink-0"
                            />
                          )}
                          <div className="truncate">
                            <div className="text-xs font-semibold text-neutral-900 truncate">
                              {prod.name}
                            </div>
                            <div className="text-[11px] text-neutral-500">
                              {prod.brand ? `${prod.brand} · ` : ""}{prod.pack_size || prod.unit || ""}
                            </div>
                          </div>
                        </div>
                        <div className="text-xs font-bold text-neutral-900 shrink-0 pl-2">
                          ₹{prod.price}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Bottom Bar: Full Search */}
                <div
                  onClick={() => navigateToSearch(searchQuery)}
                  className="p-2.5 bg-neutral-50 border-t border-neutral-100 hover:bg-neutral-100 text-xs font-semibold text-neutral-700 flex items-center justify-between cursor-pointer"
                >
                  <span>See all results for &ldquo;<span className="text-[#FF9900]">{searchQuery}</span>&rdquo;</span>
                  <span className="text-[11px] text-neutral-400 font-normal">Press Enter</span>
                </div>
              </div>
            )}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-1 shrink-0">
            {/* Account */}
            <Link
              href="/store"
              className="flex flex-col px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all"
            >
              <span className="text-[11px] text-neutral-300 leading-none">Hello, Household</span>
              <span className="text-sm font-bold text-white leading-tight flex items-center gap-0.5">
                Account & Lists
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </span>
            </Link>

            {/* Orders */}
            <Link
              href="/orders"
              className="flex flex-col px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all hidden sm:flex"
            >
              <span className="text-[11px] text-neutral-300 leading-none">Returns</span>
              <span className="text-sm font-bold text-white leading-tight">& Orders</span>
            </Link>

            {/* Budget indicator (Clickable to Edit) */}
            {budgetRemaining !== null && (
              <button
                type="button"
                onClick={() => setBudgetModalOpen(true)}
                title="Click to edit household budget & safety limits"
                className="hidden lg:flex flex-col px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all cursor-pointer text-left group"
              >
                <span className="text-[11px] text-neutral-300 leading-none flex items-center gap-1 group-hover:text-amber-300">
                  Budget left
                  <SlidersHorizontal className="w-2.5 h-2.5 text-[#FF9900]" />
                </span>
                <span className="text-sm font-bold text-[#FF9900] leading-tight">
                  ₹{budgetRemaining.toLocaleString("en-IN")}
                </span>
              </button>
            )}

            {/* NOVA Copilot Quick Trigger */}
            <a
              href="#hero-copilot"
              onClick={(e) => {
                const el = document.getElementById("hero-copilot");
                if (el) {
                  e.preventDefault();
                  el.scrollIntoView({ behavior: "smooth" });
                  el.classList.add("ring-4", "ring-[#FF9900]/50");
                  setTimeout(() => el.classList.remove("ring-4", "ring-[#FF9900]/50"), 1500);
                }
              }}
              className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-400/50 hover:border-amber-400 hover:bg-amber-500/30 text-white transition-all shadow-xs cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#FF9900] animate-pulse" />
              <div className="flex flex-col text-left">
                <span className="text-[9px] text-amber-300 leading-none font-bold uppercase tracking-wider">AI Layer</span>
                <span className="text-xs font-bold text-white leading-tight">NOVA Copilot</span>
              </div>
            </a>

            {/* Cart */}
            <Link
              href="/cart"
              className="flex items-end gap-1 px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all"
              id="nav-cart-link"
            >
              <div className="relative">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                  <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>
                  <line x1="3" y1="6" x2="21" y2="6"/>
                  <path d="M16 10a4 4 0 0 1-8 0"/>
                </svg>
                {cartCount > 0 && (
                  <span className="absolute -top-1 left-3.5 w-5 h-5 bg-[#FF9900] text-[#131921] text-[11px] font-black rounded-full flex items-center justify-center leading-none">
                    {cartCount > 9 ? "9+" : cartCount}
                  </span>
                )}
              </div>
              <span className="text-sm font-bold text-white pb-0.5 hidden sm:block">Cart</span>
            </Link>
          </div>
        </div>
      </header>

      {/* SECONDARY NAV BAR */}
      <div className="fixed top-14 left-0 right-0 z-40 bg-[#232F3E] text-white">
        <div className="max-w-[1500px] mx-auto px-3 h-9 flex items-center gap-0 overflow-x-auto hide-scrollbar">
          {/* All Departments */}
          <Link
            href="/catalog"
            className="flex items-center gap-1.5 px-3 h-9 text-xs font-semibold text-white hover:outline hover:outline-1 hover:outline-white/50 rounded shrink-0 whitespace-nowrap transition-all"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
            All Departments
          </Link>

          {/* Separator */}
          <div className="h-5 w-px bg-white/20 mx-1 shrink-0" />

          {secondaryNavLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-3 h-9 text-xs font-medium flex items-center whitespace-nowrap transition-all rounded hover:outline hover:outline-1 hover:outline-white/50 shrink-0 ${
                pathname === link.href ? "font-bold text-white outline outline-1 outline-white/50" : "text-white/90"
              }`}
            >
              {link.label}
            </Link>
          ))}

          {/* Swiggy Instamart Status / Connect Button */}
          <div className="ml-auto flex items-center gap-2 shrink-0">
            {swiggyStatus.authenticated ? (
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-emerald-950/80 border border-emerald-500/40 rounded text-emerald-300 text-xs font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="hidden sm:inline">Swiggy Instamart:</span> Connected
                  {swiggyStatus.active_address && (
                    <span className="text-[11px] text-emerald-200/80 border-l border-emerald-500/40 pl-1.5 hidden md:inline truncate max-w-[160px]">
                      Delivery: {swiggyStatus.active_address.addressTag || swiggyStatus.active_address.label || swiggyStatus.active_address.addressCategory || "Active"}
                    </span>
                  )}
                </span>
                <button
                  onClick={handleDisconnectSwiggy}
                  className="text-xs text-neutral-400 hover:text-white px-2 py-1 transition-colors"
                  title="Disconnect Swiggy session"
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-amber-950/80 border border-amber-500/40 rounded text-amber-300 text-xs font-semibold">
                  <span className="w-2 h-2 rounded-full bg-amber-400" />
                  <span className="hidden sm:inline">Demo Commerce — Active</span>
                  <span className="sm:hidden">Demo</span>
                </span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={handleConnectSwiggy}
                    className="flex items-center gap-1.5 px-3 py-1 bg-[#FC8019] hover:bg-[#e07014] text-white text-xs font-bold rounded shadow-sm transition-all cursor-pointer"
                    title="Connect Swiggy Instamart"
                  >
                    <span className="w-2 h-2 rounded-full bg-white/80 animate-ping" />
                    Connect Swiggy Instamart
                  </button>
                  <a
                    href="/api/auth/swiggy/login?redirect=true"
                    className="text-[10px] text-neutral-400 hover:text-white underline hidden xl:inline"
                    title="Authenticate via official Swiggy OAuth 2.1 OTP flow"
                  >
                    OAuth
                  </a>
                </div>
              </div>
            )}

            {/* Reset Demo button */}
            <button
              onClick={handleReset}
              className="text-xs text-neutral-400 hover:text-white px-3 h-9 flex items-center whitespace-nowrap transition-colors"
            >
              Reset Demo
            </button>
          </div>
        </div>
      </div>

      {/* Spacer: 14px primary + 9px secondary = 56px + 36px = 92px */}
      <div className="h-[92px]" />

      {/* Header Budget Editor Modal */}
      <BudgetModal
        isOpen={budgetModalOpen}
        onClose={() => setBudgetModalOpen(false)}
      />
    </>
  );
}
