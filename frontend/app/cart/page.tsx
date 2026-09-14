"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ProductImage from "@/components/ProductImage";
import {
  Trash2,
  Plus,
  Minus,
  ShoppingBag,
  Zap,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

export interface CartItem {
  id: string;
  product_id?: string;
  productId?: string;
  variantId?: string;
  name: string;
  brand: string;
  price: number;
  mrp?: number | null;
  quantity: number;
  currency?: string;
  pack_size?: string;
  unit?: string;
  image?: string | null;
  imageUrl?: string | null;
  category?: string;
  retailer?: string;
}

export default function CartPage() {
  const router = useRouter();
  const [cart, setCart] = useState<{ cart_id?: string; items: CartItem[]; item_count?: number; subtotal?: number }>({
    items: [],
    item_count: 0,
    subtotal: 0,
  });
  const [budget, setBudget] = useState<{ monthly: number; spent: number; remaining: number; auto_limit: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkingOut, setCheckingOut] = useState(false);
  const [orderComplete, setOrderComplete] = useState<any>(null);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  const fetchCartAndBudget = useCallback(async () => {
    try {
      const [cartRes, budgetRes] = await Promise.all([
        fetch("/api/cart").then((r) => r.json()).catch(() => ({ items: [], item_count: 0, subtotal: 0 })),
        fetch("/api/budget").then((r) => r.json()).catch(() => null),
      ]);
      setCart(cartRes || { items: [], item_count: 0, subtotal: 0 });
      setBudget(budgetRes);
    } catch (err) {
      console.error("Failed to load cart", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCartAndBudget();
  }, [fetchCartAndBudget]);

  const handleUpdateQuantity = async (productId: string, newQty: number) => {
    try {
      if (newQty <= 0) {
        await handleRemoveItem(productId);
        return;
      }
      await fetch("/api/cart/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId, quantity: newQty }),
      });
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("cart-updated"));
      }
      fetchCartAndBudget();
    } catch (err) {
      console.error("Failed to update quantity", err);
    }
  };

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
    if (checkingOut || (cart.items || []).length === 0) return;
    setCheckingOut(true);
    setCheckoutError(null);
    try {
      const res = await fetch("/api/checkout", { method: "POST" });
      const data = await res.json();
      if (!res.ok || data.error) {
        setCheckoutError(data.detail || data.error || "Checkout failed. Please review your budget limits.");
      } else {
        setOrderComplete(data);
        if (typeof window !== "undefined") {
          window.dispatchEvent(new Event("cart-updated"));
        }
      }
    } catch (err: any) {
      console.error("Checkout failed", err);
      setCheckoutError(err.message || "Failed to execute checkout.");
    } finally {
      setCheckingOut(false);
    }
  };

  const items = cart.items || [];
  const subtotal = items.reduce((sum, item) => sum + (item.price || 0) * (item.quantity || 1), 0);
  const totalItems = items.reduce((sum, item) => sum + (item.quantity || 1), 0);
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
      <div className="min-h-screen bg-[#EAEDED] py-10">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white p-8 rounded-sm border border-neutral-200 shadow-sm text-center">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4 text-green-600">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-neutral-900 mb-2">Order Confirmed!</h1>
            <p className="text-xs text-neutral-500 mb-4">
              Order ID: <span className="font-mono font-bold text-neutral-700">{orderComplete.orderId || orderComplete.id}</span>
            </p>
            <p className="text-sm text-neutral-700 mb-6 max-w-md mx-auto">
              {orderComplete.message || "Your order has been placed via Swiggy Instamart and is scheduled for delivery in 10-15 minutes."}
            </p>

            <div className="bg-neutral-50 border border-neutral-200 rounded p-4 text-left text-xs mb-6 space-y-2">
              <div className="flex justify-between font-semibold">
                <span>Total Paid:</span>
                <span>₹{(orderComplete.total || subtotal).toLocaleString("en-IN")}</span>
              </div>
              <div className="flex justify-between text-neutral-600">
                <span>Estimated Delivery:</span>
                <span className="font-medium text-green-700">{orderComplete.eta || "10-15 mins"}</span>
              </div>
              <div className="flex justify-between text-neutral-600">
                <span>Source:</span>
                <span>{orderComplete.source || "SWIGGY_INSTAMART"}</span>
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <Link
                href="/store"
                className="px-6 py-2 bg-[#FFD814] hover:bg-[#F7CA00] text-neutral-900 text-xs font-semibold rounded-full shadow-xs"
              >
                Return to NOVA Home
              </Link>
              <Link
                href="/catalog"
                className="px-6 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-800 text-xs font-semibold rounded-full border border-neutral-300"
              >
                Browse Catalog
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#EAEDED] py-6">
      <div className="max-w-[1400px] mx-auto px-4">
        {/* Breadcrumbs */}
        <div className="text-xs text-neutral-500 mb-3 flex items-center gap-1.5">
          <Link href="/store" className="hover:text-[#C45500] hover:underline">
            Home
          </Link>
          <span>/</span>
          <span className="text-neutral-900 font-medium">Shopping Cart</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6 items-start">
          {/* Main Cart Items */}
          <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
            <div className="flex items-baseline justify-between border-b border-neutral-200 pb-3 mb-4">
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 tracking-tight">Shopping Cart</h1>
                <p className="text-xs text-neutral-500 mt-0.5">
                  Real items ready for instant fulfillment via Swiggy Instamart dark store.
                </p>
              </div>
              <span className="text-xs text-neutral-500 hidden sm:block">Price</span>
            </div>

            {items.length === 0 ? (
              <div className="py-14 text-center">
                <ShoppingBag className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
                <h2 className="text-lg font-bold text-neutral-800 mb-1">Your NOVA Cart is empty.</h2>
                <p className="text-xs text-neutral-500 mb-4">
                  Explore household staples, fresh milk, cooking oils, and daily essentials.
                </p>
                <Link
                  href="/catalog"
                  className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-[#FFD814] hover:bg-[#F7CA00] text-xs font-semibold rounded-full text-neutral-900 transition-colors shadow-xs"
                >
                  Browse Catalog
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-neutral-200">
                {items.map((item) => {
                  const itemKey = item.id || item.variantId || item.product_id;
                  const itemQty = item.quantity || 1;
                  const itemTotal = (item.price || 0) * itemQty;

                  return (
                    <div key={itemKey} className="py-4 flex gap-4 items-start">
                      {/* Thumbnail */}
                      <Link
                        href={`/catalog/${item.id || item.product_id}`}
                        className="relative w-24 h-24 shrink-0 bg-white border border-neutral-100 rounded overflow-hidden"
                      >
                        <ProductImage
                          src={item.imageUrl || item.image}
                          alt={item.name}
                          category={item.category}
                          product={item as any}
                          fill
                          sizes="96px"
                          className="object-contain p-1"
                        />
                      </Link>

                      {/* Info & Quantity Controls */}
                      <div className="flex-1">
                        <Link
                          href={`/catalog/${item.id || item.product_id}`}
                          className="text-sm font-semibold text-neutral-900 hover:text-[#C45500] line-clamp-2 leading-snug"
                        >
                          {item.name}
                        </Link>
                        {item.pack_size && (
                          <p className="text-xs text-neutral-500 mt-0.5">{item.pack_size}</p>
                        )}
                        <p className="text-xs font-semibold text-emerald-700 mt-1 flex items-center gap-1">
                          <ShieldCheck className="w-3 h-3" />
                          In stock (10-15 min delivery)
                        </p>

                        {/* Controls Row */}
                        <div className="mt-3 flex items-center gap-4 flex-wrap">
                          {/* Quantity Selector: Minus / Qty / Plus */}
                          <div className="flex items-center border border-neutral-300 rounded bg-neutral-50 shadow-2xs">
                            <button
                              onClick={() => handleUpdateQuantity(item.id || item.product_id!, itemQty - 1)}
                              className="px-2 py-1 text-neutral-600 hover:bg-neutral-200 hover:text-neutral-900 transition-colors"
                              title="Decrease quantity"
                              aria-label="Decrease quantity"
                            >
                              <Minus className="w-3 h-3" />
                            </button>
                            <span className="px-3 py-1 text-xs font-bold text-neutral-900 bg-white border-x border-neutral-300 min-w-[32px] text-center">
                              {itemQty}
                            </span>
                            <button
                              onClick={() => handleUpdateQuantity(item.id || item.product_id!, itemQty + 1)}
                              className="px-2 py-1 text-neutral-600 hover:bg-neutral-200 hover:text-neutral-900 transition-colors"
                              title="Increase quantity"
                              aria-label="Increase quantity"
                            >
                              <Plus className="w-3 h-3" />
                            </button>
                          </div>

                          <div className="h-4 w-px bg-neutral-200" />

                          {/* Remove button */}
                          <button
                            onClick={() => handleRemoveItem(item.id || item.product_id!)}
                            className="text-xs text-[#007185] hover:text-[#C45500] hover:underline flex items-center gap-1"
                          >
                            <Trash2 className="w-3 h-3" />
                            Delete
                          </button>

                          <span className="text-neutral-400 text-[11px] flex items-center gap-1">
                            <Zap className="w-3 h-3 text-[#FC8019]" />
                            Household Autopilot Tracked
                          </span>
                        </div>
                      </div>

                      {/* Price per item / total */}
                      <div className="text-right shrink-0">
                        <p className="text-base font-bold text-neutral-900">
                          ₹{itemTotal.toLocaleString("en-IN")}
                        </p>
                        {itemQty > 1 && (
                          <p className="text-[11px] text-neutral-500">
                            (₹{item.price?.toLocaleString("en-IN")} each)
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}

                {/* Subtotal bottom */}
                <div className="border-t border-neutral-200 pt-4 text-right">
                  <p className="text-base text-neutral-800">
                    Subtotal ({totalItems} item{totalItems !== 1 ? "s" : ""}):{" "}
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
                <div className="flex items-center gap-1.5 text-xs text-emerald-700 font-semibold mb-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Your order qualifies for FAST Delivery.
                </div>

                <div className="text-sm mb-4">
                  Subtotal ({totalItems} item{totalItems !== 1 ? "s" : ""}):{" "}
                  <span className="font-bold text-neutral-900 text-lg">
                    ₹{subtotal.toLocaleString("en-IN")}
                  </span>
                </div>

                {checkoutError && (
                  <div className="mb-3 p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-800 text-xs flex items-start gap-1.5">
                    <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                    <span>{checkoutError}</span>
                  </div>
                )}

                <button
                  onClick={handleCheckout}
                  disabled={checkingOut || !isWithinBudget}
                  className={`w-full py-2.5 px-4 text-xs font-bold rounded-full shadow-xs transition-colors mb-2 ${
                    !isWithinBudget
                      ? "bg-neutral-200 text-neutral-400 cursor-not-allowed"
                      : "bg-[#FFD814] hover:bg-[#F7CA00] active:bg-[#F0B800] text-neutral-900"
                  }`}
                >
                  {checkingOut
                    ? "Placing Order..."
                    : !isWithinBudget
                    ? "Exceeds Monthly Budget"
                    : "Proceed to Checkout"}
                </button>

                <p className="text-[10px] text-neutral-400 text-center leading-relaxed">
                  Real-time Swiggy Instamart checkout with deterministic budget enforcement.
                </p>
              </div>

              {/* Household Budget & Autopilot Impact Box */}
              <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs text-xs">
                <h3 className="font-bold text-neutral-900 text-sm mb-2 flex items-center gap-1.5">
                  <Zap className="w-4 h-4 text-[#FF9900]" />
                  Household Budget Impact
                </h3>
                <div className="space-y-2 text-neutral-600 mb-3">
                  <div className="flex justify-between">
                    <span>Monthly Household Budget:</span>
                    <span className="font-semibold text-neutral-900">
                      ₹{(budget?.monthly || 5500).toLocaleString("en-IN")}
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
                    <span className={isWithinBudget ? "text-emerald-700" : "text-rose-600"}>
                      ₹{budgetAfter.toLocaleString("en-IN")}
                    </span>
                  </div>
                </div>

                <div
                  className={`p-2.5 rounded text-[11px] font-medium flex items-center gap-1.5 ${
                    isWithinBudget ? "bg-emerald-50 text-emerald-800" : "bg-rose-50 text-rose-800"
                  }`}
                >
                  {isWithinBudget ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>Order is within your monthly household budget limit.</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                      <span>Order exceeds your monthly limit. Cannot proceed without adjustment.</span>
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
