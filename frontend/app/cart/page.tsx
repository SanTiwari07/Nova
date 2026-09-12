"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ProductImage from "@/components/ProductImage";

interface CartItem {
  id: string;
  name: string;
  brand: string;
  price: number;
  currency?: string;
  pack_size?: string;
  image?: string | null;
  imageUrl?: string | null;
  category?: string;
}

export default function CartPage() {
  const router = useRouter();
  const [cart, setCart] = useState<{ cart_id?: string; items: CartItem[] }>({ items: [] });
  const [budget, setBudget] = useState<{ monthly: number; spent: number; remaining: number; auto_limit: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);
  const [orderComplete, setOrderComplete] = useState<any>(null);

  const fetchCartAndBudget = async () => {
    try {
      const [cartRes, budgetRes] = await Promise.all([
        fetch("/api/cart").then((r) => r.json()).catch(() => ({ items: [] })),
        fetch("/api/budget").then((r) => r.json()).catch(() => null),
      ]);
      setCart(cartRes || { items: [] });
      setBudget(budgetRes);
    } catch (err) {
      console.error("Failed to load cart", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCartAndBudget();
  }, []);

  const handleRemoveItem = async (productId: string) => {
    try {
      await fetch("/api/cart/remove", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId }),
      });
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("cart-updated"));
      }
      fetchCartAndBudget();
    } catch (err) {
      console.error("Failed to remove item", err);
    }
  };

  const handleCheckout = async () => {
    if (checkingOut || cart.items.length === 0) return;
    setCheckingOut(true);
    try {
      const res = await fetch("/api/checkout", { method: "POST" });
      const order = await res.json();
      if (order && !order.error) {
        setOrderComplete(order);
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("cart-updated"));
        }
      }
    } catch (err) {
      console.error("Checkout failed", err);
    } finally {
      setCheckingOut(false);
    }
  };

  const items = cart.items || [];
  const subtotal = items.reduce((sum, item) => sum + (item.price || 0), 0);
  const budgetRemaining = budget?.remaining ?? 1580;
  const budgetAfter = Math.max(0, budgetRemaining - subtotal);
  const isWithinBudget = subtotal <= budgetRemaining;

  if (loading) {
    return (
      <div className="min-h-screen bg-[#EAEDED] py-10 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium text-neutral-600">Loading your shopping cart...</p>
        </div>
      </div>
    );
  }

  if (orderComplete) {
    return (
      <div className="min-h-screen bg-[#EAEDED] py-8">
        <div className="max-w-3xl mx-auto px-4">
          <div className="bg-white p-8 rounded-sm border border-neutral-200 shadow-sm text-center">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <h1 className="text-2xl font-black text-neutral-900 mb-2">Order Confirmed!</h1>
            <p className="text-sm text-neutral-600 mb-2">
              Order #{orderComplete.id} placed with Amazon (Simulated demo integration).
            </p>
            <p className="text-xs text-neutral-400 mb-6">
              NOVA Household Autopilot updated your pantry stock and deducted ₹{orderComplete.total?.toLocaleString("en-IN")} from your monthly budget.
            </p>

            <div className="bg-neutral-50 p-4 rounded border border-neutral-200 text-left max-w-md mx-auto mb-6 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-neutral-500">Total Items:</span>
                <span className="font-bold text-neutral-900">{orderComplete.items?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Total Amount:</span>
                <span className="font-bold text-neutral-900">₹{orderComplete.total?.toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-neutral-500">Delivery Status:</span>
                <span className="font-semibold text-green-700">Scheduled for Tomorrow by 11 AM</span>
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <Link
                href="/orders"
                className="px-6 py-2.5 bg-neutral-900 text-white rounded text-xs font-semibold hover:bg-neutral-800"
              >
                View Orders
              </Link>
              <Link
                href="/store"
                className="px-6 py-2.5 bg-[#FFD814] hover:bg-[#F7CA00] text-neutral-900 rounded text-xs font-semibold"
              >
                Continue Shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#EAEDED] py-6">
      <div className="max-w-[1500px] mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-5 items-start">
          {/* Main Cart Items Column */}
          <div className="bg-white p-6 rounded-sm border border-neutral-200 shadow-xs">
            <div className="flex items-baseline justify-between border-b border-neutral-200 pb-3 mb-4">
              <div>
                <h1 className="text-2xl font-bold text-neutral-900">Shopping Cart</h1>
                <p className="text-xs text-[#007185] hover:underline cursor-pointer">
                  Deselect all items
                </p>
              </div>
              <span className="text-xs font-semibold text-neutral-500 hidden sm:block">Price</span>
            </div>

            {items.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-lg font-bold text-neutral-900 mb-2">Your NOVA Cart is empty</p>
                <p className="text-xs text-neutral-500 mb-6">
                  Check out today&apos;s deals or browse recommendations based on your household consumption.
                </p>
                <div className="flex justify-center gap-3">
                  <Link
                    href="/catalog"
                    className="px-6 py-2.5 bg-[#FFD814] hover:bg-[#F7CA00] text-xs font-semibold rounded-full text-neutral-900"
                  >
                    Browse Products
                  </Link>
                  <Link
                    href="/autopilot"
                    className="px-6 py-2.5 bg-neutral-100 hover:bg-neutral-200 text-xs font-semibold rounded-full text-neutral-800 border border-neutral-300"
                  >
                    Open Autopilot
                  </Link>
                </div>
              </div>
            ) : (
              <div>
                <div className="divide-y divide-neutral-200">
                  {items.map((item, idx) => (
                    <div key={`${item.id}-${idx}`} className="py-4 flex flex-col sm:flex-row gap-4 items-start">
                      {/* Thumbnail */}
                      <Link
                        href={`/catalog/${item.id}`}
                        className="relative w-24 h-24 shrink-0 bg-white border border-neutral-100 rounded overflow-hidden"
                      >
                        <ProductImage
                          src={item.imageUrl || item.image}
                          alt={item.name}
                          category={item.category}
                          product={item}
                          fill
                          sizes="96px"
                          className="object-contain p-1"
                        />
                      </Link>

                      {/* Info */}
                      <div className="flex-1">
                        <Link
                          href={`/catalog/${item.id}`}
                          className="text-sm font-medium text-neutral-900 hover:text-[#C45500] line-clamp-2 leading-snug"
                        >
                          {item.name}
                        </Link>
                        {item.pack_size && (
                          <p className="text-xs text-neutral-500 mt-0.5">{item.pack_size}</p>
                        )}
                        <p className="text-xs font-semibold text-green-700 mt-1">In stock</p>
                        <p className="text-[11px] text-neutral-500">Eligible for FREE Shipping</p>

                        <div className="mt-2 flex items-center gap-3 text-xs">
                          <button
                            onClick={() => handleRemoveItem(item.id)}
                            className="text-[#007185] hover:text-[#C45500] hover:underline"
                          >
                            Delete
                          </button>
                          <span className="text-neutral-300">|</span>
                          <span className="text-neutral-500 text-[11px]">
                            ⚡ Monitored by Household Autopilot
                          </span>
                        </div>
                      </div>

                      {/* Price */}
                      <div className="text-right shrink-0">
                        <p className="text-base font-bold text-neutral-900">
                          ₹{item.price?.toLocaleString("en-IN")}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Subtotal bottom */}
                <div className="border-t border-neutral-200 pt-4 text-right">
                  <p className="text-base text-neutral-800">
                    Subtotal ({items.length} item{items.length !== 1 ? "s" : ""}):{" "}
                    <span className="font-bold text-neutral-900 text-lg">
                      ₹{subtotal.toLocaleString("en-IN")}
                    </span>
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Right Summary Box */}
          {items.length > 0 && (
            <div className="space-y-4">
              <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
                <div className="flex items-center gap-1.5 text-xs text-green-700 font-semibold mb-3">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  Your order qualifies for FREE Delivery.
                </div>

                <div className="text-sm mb-4">
                  Subtotal ({items.length} item{items.length !== 1 ? "s" : ""}):{" "}
                  <span className="font-bold text-neutral-900 text-lg">
                    ₹{subtotal.toLocaleString("en-IN")}
                  </span>
                </div>

                <button
                  onClick={handleCheckout}
                  disabled={checkingOut}
                  className="w-full py-2.5 px-4 bg-[#FFD814] hover:bg-[#F7CA00] active:bg-[#F0B800] text-xs font-semibold rounded-full text-neutral-900 shadow-xs transition-colors mb-2 disabled:opacity-50"
                >
                  {checkingOut ? "Placing Simulated Order..." : "Proceed to Buy (Simulated)"}
                </button>

                <p className="text-[10px] text-neutral-400 text-center leading-relaxed">
                  Demo checkout. Simulated purchase via Amazon mock adapter.
                </p>
              </div>

              {/* Household Budget & Autopilot Impact Box */}
              <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs text-xs">
                <h3 className="font-bold text-neutral-900 text-sm mb-2 flex items-center gap-1.5">
                  <span className="text-[#FF9900]">⚡</span> Household Budget Impact
                </h3>
                <div className="space-y-2 text-neutral-600 mb-3">
                  <div className="flex justify-between">
                    <span>Monthly Household Budget:</span>
                    <span className="font-semibold text-neutral-900">
                      ₹{(budget?.monthly || 5000).toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Current Remaining:</span>
                    <span className="font-semibold text-neutral-900">
                      ₹{budgetRemaining.toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>This Order:</span>
                    <span className="font-semibold text-neutral-900">
                      -₹{subtotal.toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="flex justify-between pt-2 border-t border-neutral-100 font-bold">
                    <span>Remaining After Order:</span>
                    <span className={isWithinBudget ? "text-green-700" : "text-[#CC0C39]"}>
                      ₹{budgetAfter.toLocaleString("en-IN")}
                    </span>
                  </div>
                </div>

                <div
                  className={`p-2 rounded text-[11px] font-medium flex items-center gap-1.5 ${
                    isWithinBudget ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"
                  }`}
                >
                  {isWithinBudget ? (
                    <>
                      <span>✓</span> Order is within your monthly household limit.
                    </>
                  ) : (
                    <>
                      <span>⚠</span> Order exceeds your monthly limit. Approval required.
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
