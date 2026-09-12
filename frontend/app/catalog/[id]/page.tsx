"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import ProductImage from "@/components/ProductImage";
import { Search, CheckCircle2, Star } from "lucide-react";

interface Product {
  id: string;
  name: string;
  brand?: string | null;
  category: string;
  subcategory?: string;
  description?: string;
  image?: string | null;
  imageUrl?: string | null;
  price: number;
  mrp?: number | null;
  currency?: string;
  unit?: string | null;
  pack_size?: string | null;
  availability?: string | boolean;
  rating?: number;
  review_count?: number;
  tags?: string[];
  preferred?: boolean;
}

function StarRating({ rating, count }: { rating: number; count?: number }) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center gap-0.5">
        {Array.from({ length: full }).map((_, i) => (
          <svg key={`f${i}`} className="text-[#FF9900]" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" />
          </svg>
        ))}
        {half && (
          <svg className="text-[#FF9900]" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" opacity="0.5" />
          </svg>
        )}
        {Array.from({ length: empty }).map((_, i) => (
          <svg key={`e${i}`} className="text-neutral-300" width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26" />
          </svg>
        ))}
      </div>
      <span className="text-sm text-[#0066c0] font-medium cursor-pointer hover:text-[#CC0C39] hover:underline">
        {rating.toFixed(1)}
      </span>
      {count !== undefined && (
        <span className="text-sm text-[#0066c0] cursor-pointer hover:underline">
          ({count.toLocaleString("en-IN")} ratings)
        </span>
      )}
    </div>
  );
}

export default function ProductDetailPage({ params }: { params?: { id: string } }) {
  const routeParams = useParams();
  const productId = (routeParams?.id as string) || params?.id || "";
  const router = useRouter();

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [quantity, setQuantity] = useState(1);
  const [addedToCart, setAddedToCart] = useState(false);
  const [addingToCart, setAddingToCart] = useState(false);
  const [similarProducts, setSimilarProducts] = useState<Product[]>([]);
  const [novaInsight, setNovaInsight] = useState<string | null>(null);

  useEffect(() => {
    if (!productId) return;
    setLoading(true);
    setNotFound(false);
    setProduct(null);
    setNovaInsight(null);

    fetch(`/api/products/${productId}`)
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok || data?.error) {
          setNotFound(true);
          return null;
        }
        return data;
      })
      .then((data) => {
        if (!data) return;
        setProduct(data);

        // Load similar products
        fetch(`/api/products?limit=40`)
          .then((r) => r.json())
          .then((all: Product[]) => {
            const similar = all
              .filter((p) => p.category === data.category && p.id !== data.id)
              .slice(0, 6);
            setSimilarProducts(similar);
          })
          .catch(() => {});

        // Generate NOVA insight from pantry
        fetch("/api/pantry")
          .then((r) => r.json())
          .then((pantry: any[]) => {
            const match = (pantry || []).find(
              (item: any) =>
                item.name?.toLowerCase().includes(data.category?.toLowerCase()) ||
                data.category?.toLowerCase().includes(item.name?.toLowerCase())
            );
            if (match) {
              if (match.status === "LOW") {
                setNovaInsight(
                  `Your ${match.name} is running low (${match.quantity}${match.unit}). This is a good time to restock.`
                );
              } else if (match.status === "OK") {
                setNovaInsight(
                  `You currently have ${match.quantity}${match.unit} of ${match.name} — stock looks good.`
                );
              }
            }
          })
          .catch(() => {});
      })
      .catch(() => {
        setNotFound(true);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [productId]);

  const handleAddToCart = async () => {
    if (addingToCart) return;
    setAddingToCart(true);
    try {
      await fetch("/api/cart/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId }),
      });
      setAddedToCart(true);
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("cart-updated"));
      }
      setTimeout(() => setAddedToCart(false), 3000);
    } catch {
      // silently fail
    } finally {
      setAddingToCart(false);
    }
  };

  const handleBuyNow = async () => {
    await handleAddToCart();
    router.push("/cart");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f3f3f3]">
        <div className="max-w-[1400px] mx-auto px-4 py-6">
          <div className="h-4 bg-neutral-200 rounded w-64 mb-6 animate-pulse" />
          <div className="bg-white rounded-sm border border-neutral-200 p-6">
            <div className="grid grid-cols-1 md:grid-cols-[40%_60%] gap-8">
              <div className="aspect-square bg-neutral-100 animate-pulse rounded-sm" />
              <div className="space-y-4 pt-4">
                <div className="h-5 bg-neutral-100 animate-pulse rounded w-48" />
                <div className="h-7 bg-neutral-100 animate-pulse rounded w-full" />
                <div className="h-7 bg-neutral-100 animate-pulse rounded w-3/4" />
                <div className="h-4 bg-neutral-100 animate-pulse rounded w-32 mt-2" />
                <div className="h-10 bg-neutral-100 animate-pulse rounded w-40 mt-4" />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (notFound || !product) {
    return (
      <div className="min-h-screen bg-[#f3f3f3] flex items-center justify-center">
        <div className="text-center bg-white p-12 rounded-sm border border-neutral-200 max-w-md mx-4">
          <Search className="w-12 h-12 text-neutral-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-neutral-900 mb-2">Product not found</h1>
          <p className="text-neutral-500 mb-6 text-sm">
            We couldn&apos;t find the product you&apos;re looking for. It may have been removed or the link may be incorrect.
          </p>
          <Link
            href="/catalog"
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#FFD814] text-neutral-900 font-semibold rounded-full hover:bg-[#F7CA00] transition-colors border border-[#F2C200]"
          >
            Browse All Products
          </Link>
        </div>
      </div>
    );
  }

  const mrp = Math.round(product.price * 1.18);
  const discount = Math.round(((mrp - product.price) / mrp) * 100);
  const inStock = product.availability !== "OUT_OF_STOCK";

  return (
    <div className="min-h-screen bg-[#f3f3f3]">
      <div className="max-w-[1400px] mx-auto px-4 py-4">
        {/* Breadcrumb */}
        <nav className="text-xs text-neutral-500 mb-3 flex items-center gap-1 flex-wrap">
          <Link href="/store" className="hover:text-[#0066c0] hover:underline">Home</Link>
          <span>›</span>
          <Link href="/catalog" className="hover:text-[#0066c0] hover:underline">All Departments</Link>
          <span>›</span>
          <Link
            href={`/catalog?category=${encodeURIComponent(product.category)}`}
            className="hover:text-[#0066c0] hover:underline"
          >
            {product.category}
          </Link>
          <span>›</span>
          <span className="text-neutral-700 font-medium line-clamp-1 max-w-[300px]">{product.name}</span>
        </nav>

        {/* Main Product Area */}
        <div className="bg-white border border-neutral-200 rounded-sm p-4 md:p-6 mb-4">
          <div className="grid grid-cols-1 md:grid-cols-[38%_37%_25%] gap-6 lg:gap-8">
            {/* Image */}
            <div className="flex flex-col items-center gap-3">
              <div className="relative w-full max-w-sm mx-auto aspect-square border border-neutral-200 rounded-sm overflow-hidden bg-white p-4">
                <ProductImage
                  src={product.imageUrl || product.image}
                  alt={product.name}
                  category={product.category}
                  product={product}
                  fill
                  sizes="(max-width: 768px) 90vw, 38vw"
                />
              </div>
              {/* Thumbnail strip */}
              <div className="flex gap-2 justify-center">
                <div className="w-14 h-14 border-2 border-[#FC8019] rounded-sm overflow-hidden bg-white cursor-pointer p-1">
                  <ProductImage
                    src={product.imageUrl || product.image}
                    alt={product.name}
                    category={product.category}
                    product={product}
                    width={52}
                    height={52}
                  />
                </div>
              </div>
            </div>

            {/* Product Info */}
            <div className="flex flex-col gap-3">
              <div>
                <p className="text-sm text-[#0066c0] cursor-pointer hover:underline mb-1">
                  Brand: <span className="font-medium">{product.brand}</span>
                </p>
                <h1 className="text-lg md:text-xl font-medium text-neutral-900 leading-snug mb-3">
                  {product.name}
                </h1>

                {product.rating !== undefined && (
                  <div className="mb-3 pb-3 border-b border-neutral-100">
                    <StarRating rating={product.rating} count={product.review_count} />
                  </div>
                )}

                {/* Price block */}
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm text-neutral-500">M.R.P.:</span>
                    <span className="text-sm text-neutral-400 line-through">
                      ₹{mrp.toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm text-neutral-500">Price:</span>
                    <span className="text-3xl font-medium text-neutral-900">
                      ₹<span className="font-light">{Math.floor(product.price).toLocaleString("en-IN")}</span>
                      <span className="text-lg">.{String(Math.round((product.price % 1) * 100)).padStart(2, "0")}</span>
                    </span>
                  </div>
                  <p className="text-xs text-green-700 mt-1 font-medium">
                    You save: ₹{(mrp - product.price).toLocaleString("en-IN")} ({discount}%)
                  </p>
                  <p className="text-xs text-neutral-500">Inclusive of all taxes</p>
                </div>

                {/* Delivery */}
                <div className="border border-neutral-200 rounded-sm p-3 mb-4 text-sm space-y-1.5">
                  <div className="flex items-start gap-2">
                    <svg className="text-neutral-500 mt-0.5 shrink-0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
                    <p><span className="font-medium text-neutral-900">FREE delivery</span> by Tomorrow</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg className="text-neutral-500 mt-0.5 shrink-0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                    <p>Deliver to <span className="text-[#0066c0] font-medium cursor-pointer hover:underline">Your household — Mumbai 400001</span></p>
                  </div>
                </div>

                {/* Product details */}
                <div className="space-y-2 text-sm border-t border-neutral-100 pt-3">
                  <h3 className="font-medium text-neutral-900 mb-2">Product details</h3>
                  <div className="grid grid-cols-[120px_1fr] gap-1">
                    <span className="text-neutral-500">Pack Size</span>
                    <span className="text-neutral-800">{product.pack_size}</span>
                  </div>
                  <div className="grid grid-cols-[120px_1fr] gap-1">
                    <span className="text-neutral-500">Category</span>
                    <span className="text-neutral-800">{product.category}</span>
                  </div>
                  {product.subcategory && (
                    <div className="grid grid-cols-[120px_1fr] gap-1">
                      <span className="text-neutral-500">Type</span>
                      <span className="text-neutral-800">{product.subcategory}</span>
                    </div>
                  )}
                  <div className="grid grid-cols-[120px_1fr] gap-1">
                    <span className="text-neutral-500">Availability</span>
                    <span className={inStock ? "text-green-700" : "text-red-600"}>
                      {inStock ? "In Stock" : "Currently Unavailable"}
                    </span>
                  </div>
                </div>

                {product.description && (
                  <div className="mt-4 pt-3 border-t border-neutral-100">
                    <h3 className="font-medium text-neutral-900 mb-2">About this item</h3>
                    <p className="text-sm text-neutral-600 leading-relaxed">{product.description}</p>
                  </div>
                )}
              </div>

              {/* NOVA Insight */}
              {novaInsight && (
                <div className="border border-[#FF9900]/40 bg-orange-50 rounded-sm p-3">
                  <div className="flex items-start gap-2.5">
                    <div className="w-5 h-5 rounded-full bg-[#FF9900] flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-white text-[10px] font-bold">N</span>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-[#FF9900] uppercase tracking-wide mb-0.5">
                        NOVA Household Insight
                      </p>
                      <p className="text-xs text-neutral-700 leading-relaxed">{novaInsight}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Buy Box */}
            <div className="border border-neutral-300 rounded-sm p-4 space-y-3 h-fit">
              <div>
                <span className="text-2xl font-medium text-neutral-900">
                  ₹{product.price.toLocaleString("en-IN")}
                </span>
                <div className="text-xs text-green-700 font-medium mt-0.5">
                  You save ₹{(mrp - product.price).toLocaleString("en-IN")} ({discount}%)
                </div>
                <p className="text-xs text-neutral-500">Inclusive of all taxes</p>
              </div>

              <div className="text-sm border-t border-neutral-100 pt-3">
                <p>
                  <span className="font-medium text-neutral-900">FREE delivery</span> by Tomorrow
                </p>
                <p className="text-neutral-500 text-xs mt-0.5">Order within 2 hrs 30 mins</p>
              </div>

              <div className="text-sm">
                <p className="text-neutral-600">
                  Deliver to{" "}
                  <span className="font-medium text-neutral-900">Mumbai 400001</span>
                </p>
              </div>

              <div className="text-sm">
                {inStock ? (
                  <p className="text-green-700 font-medium">In stock</p>
                ) : (
                  <p className="text-red-600 font-medium">Currently unavailable</p>
                )}
              </div>

              {inStock && (
                <>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-neutral-600">Qty:</label>
                    <select
                      value={quantity}
                      onChange={(e) => setQuantity(Number(e.target.value))}
                      className="border border-neutral-300 rounded-full px-3 py-1 text-sm bg-neutral-50 focus:outline-none focus:border-[#FF9900]"
                    >
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={handleAddToCart}
                    disabled={addingToCart}
                    id="add-to-cart-btn"
                    className={`w-full py-2 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
                      addedToCart
                        ? "bg-green-100 text-green-700 border border-green-200"
                        : "bg-[#FFD814] text-neutral-900 hover:bg-[#F7CA00] border border-[#F2C200]"
                    } disabled:opacity-60`}
                  >
                    {addedToCart ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" /> Added to Cart
                      </>
                    ) : addingToCart ? (
                      "Adding..."
                    ) : (
                      "Add to Cart"
                    )}
                  </button>

                  <button
                    onClick={handleBuyNow}
                    id="buy-now-btn"
                    className="w-full py-2 rounded-full text-sm font-medium bg-[#FF9900] text-white hover:bg-[#e68900] transition-colors border border-[#e68900]"
                  >
                    Buy Now
                  </button>
                </>
              )}

              <div className="border-t border-neutral-100 pt-3 space-y-1 text-xs text-neutral-500">
                <p>Ships from and sold by <span className="text-[#0066c0]">NOVA Commerce</span></p>
                <p className="text-amber-700 bg-amber-50 rounded p-1.5 mt-1">
                  Demo mode &mdash; No real purchase will be made
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Similar Products */}
        {similarProducts.length > 0 && (
          <div className="bg-white border border-neutral-200 rounded-sm p-4 md:p-6">
            <h2 className="text-lg font-medium text-neutral-900 mb-4">
              Customers also bought in <span className="font-bold">{product.category}</span>
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {similarProducts.map((p) => {
                const pMrp = Math.round(p.price * 1.18);
                const pDisc = Math.round(((pMrp - p.price) / pMrp) * 100);
                return (
                  <Link
                    key={p.id}
                    href={`/catalog/${p.id}`}
                    className="group flex flex-col border border-neutral-200 rounded-sm overflow-hidden hover:shadow-md transition-all hover:border-[#FF9900]"
                  >
                    <div className="relative aspect-square bg-white overflow-hidden p-2">
                      <ProductImage
                        src={p.imageUrl || p.image}
                        alt={p.name}
                        category={p.category}
                        product={p}
                        fill
                        sizes="(max-width: 640px) 50vw, (max-width: 1024px) 25vw, 16vw"
                      />
                    </div>
                    <div className="p-2 flex flex-col flex-grow border-t border-neutral-100">
                      <p className="text-[10px] text-neutral-400 font-semibold mb-0.5 uppercase tracking-wide">
                        {p.brand}
                      </p>
                      <p className="text-xs font-medium text-neutral-800 line-clamp-2 leading-tight mb-1 group-hover:text-[#0066c0]">
                        {p.name}
                      </p>
                      {p.rating !== undefined && (
                        <div className="flex items-center gap-0.5 mb-1">
                          <span className="text-xs font-bold text-amber-600 flex items-center gap-1">
                            <Star className="w-3 h-3 fill-amber-500 text-amber-500" />
                            {p.rating.toFixed(1)}
                          </span>
                        </div>
                      )}
                      <div className="mt-auto">
                        <p className="text-sm font-bold text-neutral-900">
                          ₹{p.price.toLocaleString("en-IN")}
                        </p>
                        <p className="text-xs text-red-600 font-medium">{pDisc}% off</p>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
