"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [remindersCount, setRemindersCount] = useState(0);
  const [budgetRemaining, setBudgetRemaining] = useState<number | null>(null);

  useEffect(() => {
    // Load reminders count and budget remaining for the header indicators
    Promise.all([
      fetch("/api/reminders").then(r => r.json()).catch(() => ({ count: 0 })),
      fetch("/api/budget").then(r => r.json()).catch(() => ({ remaining: 0 })),
    ]).then(([rem, bud]) => {
      setRemindersCount(rem?.count || 0);
      setBudgetRemaining(bud?.remaining || null);
    });
  }, [pathname]);

  const handleReset = async () => {
    await fetch("/api/demo/reset", { method: "POST" });
    router.push("/store");
    router.refresh();
  };

  const navLinks = [
    { href: "/store", label: "Home" },
    { href: "/catalog", label: "Shop" },
    { href: "/pantry", label: "Pantry" },
    { href: "/nova-cart", label: "NOVA Cart" },
    { href: "/autopilot", label: "Autopilot" },
    { href: "/orders", label: "Orders" },
    { href: "/activity", label: "Activity" },
    { href: "/price-watch", label: "Price Watch" },
    { href: "/reminders", label: "Reminders" },
    { href: "/memory", label: "Memory" },
    { href: "/budget", label: "Budget" },
    { href: "/rules", label: "Rules" },
  ];

  const isActive = (href: string) =>
    pathname === href || (href !== "/store" && pathname?.startsWith(href));

  return (
    <>
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-md border-b border-neutral-200 z-50">
        <div className="max-w-[1400px] mx-auto px-4 md:px-6 h-14 flex items-center justify-between gap-4">
          {/* Logo */}
          <Link
            href="/store"
            className="font-black text-lg tracking-tight text-neutral-900 shrink-0 flex items-center gap-2"
          >
            <span className="text-[#FF9900]">N</span>OVA
          </Link>

          {/* Primary Nav */}
          <div className="hidden xl:flex items-center gap-1 flex-1 ml-4">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                  isActive(link.href)
                    ? "bg-neutral-900 text-white"
                    : "text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2 shrink-0">
            {/* Amazon connection badge */}
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="w-1.5 h-1.5 rounded-full bg-orange-400"></div>
              <span className="text-xs font-semibold text-orange-700">Amazon · Demo</span>
            </div>

            {/* Budget indicator */}
            {budgetRemaining !== null && (
              <div className="hidden md:flex items-center gap-1 px-3 py-1.5 bg-neutral-50 border border-neutral-200 rounded-lg">
                <span className="text-xs text-neutral-500">Left:</span>
                <span className="text-xs font-bold text-neutral-900">₹{budgetRemaining.toLocaleString("en-IN")}</span>
              </div>
            )}

            {/* Reminders bell */}
            <Link href="/reminders" className="relative p-2 text-neutral-600 hover:text-neutral-900 transition-colors">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              {remindersCount > 0 && (
                <span className="absolute top-1 right-1 w-4 h-4 bg-[#FF9900] text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                  {remindersCount > 9 ? "9+" : remindersCount}
                </span>
              )}
            </Link>

            {/* Cart */}
            <Link href="/cart" className="p-2 text-neutral-600 hover:text-neutral-900 transition-colors">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
              </svg>
            </Link>

            {/* Demo reset */}
            <button
              onClick={handleReset}
              className="hidden sm:block text-xs font-medium text-neutral-500 hover:text-neutral-900 px-2.5 py-1.5 bg-neutral-100 hover:bg-neutral-200 rounded-lg transition-colors"
            >
              Reset Demo
            </button>
          </div>
        </div>

        {/* Mobile nav */}
        <div className="xl:hidden border-t border-neutral-100 flex gap-1 px-4 py-2 overflow-x-auto hide-scrollbar">
          {navLinks.slice(0, 5).map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                isActive(link.href)
                  ? "bg-neutral-900 text-white"
                  : "text-neutral-600 hover:text-neutral-900 bg-neutral-50"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>
      </nav>

      {/* Spacer for fixed navbar (desktop: 56px + mobile secondary: 40px = 96px) */}
      <div className="h-[96px] xl:h-14"></div>
    </>
  );
}
