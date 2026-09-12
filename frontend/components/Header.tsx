"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useRef } from "react";

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const [cartCount, setCartCount] = useState(0);
  const [budgetRemaining, setBudgetRemaining] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchCategory, setSearchCategory] = useState("All");
  const [categories, setCategories] = useState<string[]>([]);
  const [swiggyStatus, setSwiggyStatus] = useState<{
    authenticated: boolean;
    active_address?: any;
    active_address_id?: string;
    mode?: string;
  }>({ authenticated: false });
  const searchInputRef = useRef<HTMLInputElement>(null);

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

  useEffect(() => {
    fetchHeaderData();
    window.addEventListener("cart-updated", fetchHeaderData);
    return () => window.removeEventListener("cart-updated", fetchHeaderData);
  }, [pathname]);

  const handleDisconnectSwiggy = async () => {
    await fetch("/api/auth/swiggy/disconnect", { method: "POST" });
    fetchHeaderData();
    router.refresh();
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      const params = new URLSearchParams({ q: searchQuery.trim() });
      if (searchCategory !== "All") params.set("category", searchCategory);
      router.push(`/search?${params.toString()}`);
    }
  };

  const handleReset = async () => {
    await fetch("/api/demo/reset", { method: "POST" });
    router.push("/store");
    router.refresh();
  };

  const secondaryNavLinks = [
    { href: "/store", label: "NOVA Home" },
    { href: "/catalog?category=Rice", label: "Rice & Grains" },
    { href: "/catalog?category=Snacks", label: "Snacks" },
    { href: "/catalog?category=Beverages", label: "Beverages" },
    { href: "/catalog?category=Detergent", label: "Household" },
    { href: "/catalog?category=Tea", label: "Tea & Coffee" },
    { href: "/autopilot", label: "Autopilot" },
    { href: "/budget", label: "Budget" },
  ];

  return (
    <>
      {/* PRIMARY HEADER */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-[#131921] text-white">
        <div className="max-w-[1500px] mx-auto px-3 h-14 flex items-center gap-2">
          {/* NOVA Logo */}
          <Link
            href="/store"
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
                {swiggyStatus.active_address?.label || swiggyStatus.active_address?.addressCategory || (swiggyStatus.authenticated ? "Swiggy Home" : "Connect Swiggy")}
              </span>
            </div>
          </div>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex-1 flex h-10 rounded-sm overflow-hidden shadow-sm">
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
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search NOVA for products, brands and more..."
              className="flex-1 text-neutral-900 px-3 text-sm outline-none bg-white placeholder:text-neutral-400"
              id="nova-search-input"
            />

            {/* Search Button */}
            <button
              type="submit"
              className="bg-[#FF9900] hover:bg-[#e68900] px-4 flex items-center justify-center transition-colors shrink-0"
              aria-label="Search"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#131921" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
            </button>
          </form>

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

            {/* Budget indicator */}
            {budgetRemaining !== null && (
              <div className="hidden lg:flex flex-col px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all cursor-pointer">
                <span className="text-[11px] text-neutral-300 leading-none">Budget left</span>
                <span className="text-sm font-bold text-[#FF9900] leading-tight">
                  ₹{budgetRemaining.toLocaleString("en-IN")}
                </span>
              </div>
            )}

            {/* NOVA Autopilot */}
            <Link
              href="/autopilot"
              className="hidden lg:flex flex-col px-2 py-1 rounded hover:outline hover:outline-1 hover:outline-white/50 transition-all"
            >
              <span className="text-[11px] text-neutral-300 leading-none">NOVA</span>
              <span className="text-sm font-bold text-white leading-tight">Autopilot</span>
            </Link>

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
                    <span className="text-[11px] text-emerald-200/80 border-l border-emerald-500/40 pl-1.5 hidden md:inline truncate max-w-[120px]">
                      {swiggyStatus.active_address.label || swiggyStatus.active_address.addressCategory || "Delivery Set"}
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
              <a
                href="/api/auth/swiggy/login?redirect=true"
                className="flex items-center gap-1.5 px-3 py-1 bg-[#FC8019] hover:bg-[#e07014] text-white text-xs font-bold rounded shadow-sm transition-all"
                title="Authenticate with your Swiggy phone + OTP via official OAuth 2.1"
              >
                <span className="w-2 h-2 rounded-full bg-white/80 animate-ping" />
                Connect Swiggy Instamart
              </a>
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
    </>
  );
}
