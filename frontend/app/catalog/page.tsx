"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import ProductCard from '@/components/ProductCard';

interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  currency: string;
  pack_size: string;
  image: string;
}

export default function CatalogPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [skip, setSkip] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  
  const LIMIT = 20;

  const loadProducts = useCallback(async (currentSkip: number) => {
    try {
      setLoading(true);
      const res = await fetch(`/api/products?skip=${currentSkip}&limit=${LIMIT}`);
      const data = await res.json();
      if (data.length < LIMIT) {
        setHasMore(false);
      }
      setProducts(prev => currentSkip === 0 ? data : [...prev, ...data]);
    } catch (err) {
      console.error("Failed to load products", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProducts(0);
  }, [loadProducts]);

  const observer = useRef<IntersectionObserver | null>(null);
  const lastElementRef = useCallback((node: HTMLDivElement) => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setSkip(prev => {
          const nextSkip = prev + LIMIT;
          loadProducts(nextSkip);
          return nextSkip;
        });
      }
    });
    
    if (node) observer.current.observe(node);
  }, [loading, hasMore, loadProducts]);

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-neutral-900">NOVA Demo Catalog</h1>
          <p className="text-neutral-500 mt-2">Browse our simulated commerce environment.</p>
        </header>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {products.map((product, i) => {
            if (products.length === i + 1) {
              return (
                <div ref={lastElementRef} key={product.id}>
                  <ProductCard product={product} />
                </div>
              );
            } else {
              return <ProductCard key={product.id} product={product} />;
            }
          })}
        </div>

        {loading && (
          <div className="flex justify-center mt-8 text-neutral-400">
            Loading products...
          </div>
        )}
        
        {!hasMore && (
          <div className="flex justify-center mt-8 text-neutral-400 text-sm">
            End of catalog
          </div>
        )}
      </div>
    </div>
  );
}
