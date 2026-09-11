"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const router = useRouter();

  const handleReset = async () => {
    await fetch('/api/demo/reset', { method: 'POST' });
    router.push('/');
    router.refresh();
  };

  return (
    <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-neutral-200 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <Link href="/store" className="font-extrabold text-xl tracking-tight mr-2 text-neutral-900">
            HOUSEHOLD AUTOPILOT
          </Link>
          <div className="hidden lg:flex gap-6">
            <Link href="/store" className="text-neutral-600 hover:text-neutral-900 text-sm font-medium transition-colors">Home</Link>
            <Link href="/household" className="text-neutral-600 hover:text-neutral-900 text-sm font-medium transition-colors">Household</Link>
            <Link href="/pantry" className="text-neutral-600 hover:text-neutral-900 text-sm font-medium transition-colors">Inventory</Link>
            <Link href="/orders" className="text-neutral-600 hover:text-neutral-900 text-sm font-medium transition-colors">Orders</Link>
            <Link href="/budget" className="text-neutral-600 hover:text-neutral-900 text-sm font-medium transition-colors">Budget</Link>
            <Link href="/approvals" className="text-neutral-600 hover:text-neutral-900 text-sm font-medium transition-colors">Approvals</Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/cart" className="text-neutral-600 hover:text-neutral-900 p-2 relative">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="9" cy="21" r="1"></circle>
              <circle cx="20" cy="21" r="1"></circle>
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
            </svg>
          </Link>
          <button 
            onClick={handleReset}
            className="text-xs font-medium text-neutral-600 hover:text-neutral-900 px-3 py-1.5 bg-neutral-100 rounded-md transition-colors"
          >
            Demo Reset
          </button>
          <Link 
            href="/login"
            className="text-xs font-medium text-red-600 hover:text-red-700 px-3 py-1.5 bg-red-50 rounded-md transition-colors"
          >
            Log Out
          </Link>
        </div>
      </div>
    </nav>
  );
}
