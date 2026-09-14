"use client";

import Image from 'next/image';
import { useState, useEffect, useRef } from 'react';

type ImageSize = 'sm' | 'md' | 'lg' | 'xl';

interface ProductImageProps {
  src?: string | null;
  alt: string;
  category?: string;
  id?: string;
  size?: ImageSize;
  product?: {
    id?: string;
    name?: string;
    title?: string;
    imageUrl?: string | null;
    image?: string | null;
    images?: string[];
    category?: string;
    brand?: string;
    quantity?: string;
    unit?: string;
    pack_size?: string;
    barcode?: string;
    [key: string]: any;
  } | null;
  /** Source of the resolved image URL - for console logging only */
  imageSource?: string | null;
  className?: string;
  sizes?: string;
  fill?: boolean;
  width?: number;
  height?: number;
  priority?: boolean;
  onErrorFallback?: () => void;
}

/**
 * @deprecated Hardcoded fallback assets are removed per Household Autopilot spec.
 * Returns empty string so callers never receive synthetic or local fake assets.
 */
export function getProductFallbackImage(_name?: string, _category?: string): string {
  return "";
}

const sizeClasses: Record<ImageSize, string> = {
  sm: 'w-[52px] h-[52px]',
  md: 'w-[72px] h-[72px]',
  lg: 'w-[96px] h-[96px]',
  xl: 'w-[150px] h-[150px]',
};

const dimensionMap: Record<ImageSize, number> = {
  sm: 52,
  md: 72,
  lg: 96,
  xl: 180,
};

/** Returns an SVG path + colour appropriate for the product category. */
function getCategoryIcon(category?: string): { path: string; color: string } {
  const cat = (category || '').toLowerCase();

  if (cat.includes('milk') || cat.includes('dairy') || cat.includes('ghee') || cat.includes('butter') || cat.includes('cheese')) {
    return {
      color: '#60a5fa',
      path: 'M6 2h12l2 5H4L6 2zM4 9a1 1 0 00-1 1v9a2 2 0 002 2h14a2 2 0 002-2v-9a1 1 0 00-1-1H4z',
    };
  }
  if (cat.includes('oil') || cat.includes('ghee')) {
    return {
      color: '#f59e0b',
      path: 'M12 2C8 2 4 6 4 10c0 4 2.5 7 6 8.5V20h4v-1.5C17.5 17 20 14 20 10c0-4-4-8-8-8z',
    };
  }
  if (cat.includes('atta') || cat.includes('flour') || cat.includes('rice') || cat.includes('dal') || cat.includes('grain') || cat.includes('pulse')) {
    return {
      color: '#d97706',
      path: 'M20 7H4a1 1 0 00-1 1v1a1 1 0 001 1h1l1 10h12l1-10h1a1 1 0 001-1V8a1 1 0 00-1-1zm-8 11a3 3 0 110-6 3 3 0 010 6z',
    };
  }
  if (cat.includes('tea') || cat.includes('coffee') || cat.includes('beverage') || cat.includes('drink') || cat.includes('juice')) {
    return {
      color: '#8b5cf6',
      path: 'M17 3H7l-2 9h14L17 3zM5 14v5a2 2 0 002 2h10a2 2 0 002-2v-5H5z',
    };
  }
  if (cat.includes('detergent') || cat.includes('cleaning') || cat.includes('dishwash') || cat.includes('floor') || cat.includes('toilet') || cat.includes('soap')) {
    return {
      color: '#06b6d4',
      path: 'M12 2a7 7 0 00-7 7c0 2.6 1.4 4.9 3.5 6.2V20h7v-4.8C17.6 13.9 19 11.6 19 9a7 7 0 00-7-7z',
    };
  }
  if (cat.includes('shampoo') || cat.includes('personal') || cat.includes('toothpaste') || cat.includes('handwash')) {
    return {
      color: '#ec4899',
      path: 'M8 2h8l1 3H7L8 2zm-3 5h14v12a2 2 0 01-2 2H7a2 2 0 01-2-2V7z',
    };
  }
  if (cat.includes('snack') || cat.includes('biscuit') || cat.includes('cookie') || cat.includes('chocolate') || cat.includes('namkeen')) {
    return {
      color: '#f97316',
      path: 'M4 7a1 1 0 011-1h14a1 1 0 011 1v2H4V7zm0 4h16v8a2 2 0 01-2 2H6a2 2 0 01-2-2v-8z',
    };
  }
  if (cat.includes('noodle') || cat.includes('pasta')) {
    return {
      color: '#84cc16',
      path: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z',
    };
  }
  if (cat.includes('salt') || cat.includes('sugar') || cat.includes('spice')) {
    return {
      color: '#a3a3a3',
      path: 'M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z',
    };
  }

  // Generic product icon
  return {
    color: '#9ca3af',
    path: 'M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z M9 22V12h6v10',
  };
}

export default function ProductImage({
  src,
  alt,
  category,
  id,
  size,
  product,
  imageSource,
  className = '',
  sizes,
  fill,
  width,
  height,
  priority = false,
  onErrorFallback,
}: ProductImageProps) {
  const [hasError, setHasError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [resolvedFallback, setResolvedFallback] = useState<string | null>(null);
  const [resolvingFallback, setResolvingFallback] = useState(false);

  // Track every URL that has already failed to prevent infinite retry loops
  const failedUrls = useRef<Set<string>>(new Set());

  // Resolve candidate image URL from direct src or product object
  const candidateSrc =
    resolvedFallback ||
    src ||
    product?.imageUrl ||
    product?.image ||
    product?.images?.[0] ||
    null;

  // Validate the URL — must be a genuine HTTP/HTTPS remote URL or root-relative path
  const isValidUrl =
    typeof candidateSrc === 'string' &&
    candidateSrc.trim().length > 0 &&
    (candidateSrc.startsWith('http://') ||
      candidateSrc.startsWith('https://') ||
      candidateSrc.startsWith('/'));

  // Reset state when the source URL changes
  useEffect(() => {
    setHasError(false);
    setIsLoaded(false);
    setResolvedFallback(null);
    failedUrls.current.clear();
  }, [src, product?.imageUrl, product?.image]);

  // If the initial URL is invalid/missing, try to resolve it server-side immediately
  useEffect(() => {
    if (!isValidUrl && !resolvingFallback && !resolvedFallback && !hasError) {
      handleError();
    }
  }, [isValidUrl, resolvingFallback, resolvedFallback, hasError]);

  const handleError = () => {
    const currentUrl = candidateSrc;
    console.warn('[ProductImage] Failed to load image', {
      id: id || product?.id,
      name: alt || product?.name || product?.title,
      source: imageSource || 'unknown',
      url: currentUrl,
    });

    // Guard: if this URL already failed, don't try again
    if (currentUrl && failedUrls.current.has(currentUrl)) {
      setHasError(true);
      return;
    }
    if (currentUrl) {
      failedUrls.current.add(currentUrl);
    }

    // Attempt one server-side fallback resolution if we haven't already
    if (!resolvedFallback && !resolvingFallback) {
      const nameToResolve = product?.name || product?.title || alt;
      if (nameToResolve) {
        setResolvingFallback(true);
        fetch('/api/images/resolve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_key: id || product?.id || `fallback:${nameToResolve}`,
            name: nameToResolve,
            brand: product?.brand || null,
            quantity: product?.quantity || null,
            unit: product?.unit || null,
            pack_size: product?.pack_size || null,
            barcode: product?.barcode || null,
          }),
        })
          .then((r) => r.json())
          .then((data) => {
            const newUrl: string | null = data?.imageUrl ?? null;
            // Only use the fallback if it's a different URL from what already failed
            if (newUrl && !failedUrls.current.has(newUrl)) {
              setResolvedFallback(newUrl);
            } else {
              setHasError(true);
            }
          })
          .catch(() => setHasError(true))
          .finally(() => setResolvingFallback(false));
        return;
      }
    }

    setHasError(true);
    if (typeof onErrorFallback === 'function') {
      onErrorFallback();
    }
  };

  
  const sizeClass = size ? sizeClasses[size] : '';
  const containerClasses = sizeClass ? `${sizeClass} shrink-0` : 'w-full h-full';

  // Base dimensions if not fill
  const imgWidth = width || (size ? dimensionMap[size] : 400);
  const imgHeight = height || (size ? dimensionMap[size] : 400);

  // Determine effective category from props or product
  const effectiveCategory = category || product?.category || '';

  // ── Placeholder component ────────────────────────────────────────────────
  // Shown when: no valid URL exists, or image failed to load (after fallback exhausted)
  if ((!isValidUrl || hasError) && !resolvingFallback) {
    const { path, color } = getCategoryIcon(effectiveCategory);
    return (
      <div
        className={`flex flex-col items-center justify-center bg-[#F7F7F5] text-neutral-400 rounded-xl select-none overflow-hidden ${containerClasses} ${className}`}
        aria-label="Product image unavailable"
      >
        <svg
          className="shrink-0"
          style={{ width: '38%', height: '38%', maxWidth: 40, maxHeight: 40 }}
          fill="none"
          viewBox="0 0 24 24"
          stroke={color}
          strokeWidth={1.4}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d={path} />
        </svg>
      </div>
    );
  }

  // ── Loading skeleton (shown while the image is fetching a fallback) ──────
  if (resolvingFallback) {
    return (
      <div
        className={`flex items-center justify-center bg-neutral-100 animate-pulse rounded-xl ${containerClasses} ${className}`}
        aria-label="Loading product image"
      />
    );
  }

  const commonProps = {
    src: candidateSrc as string,
    alt: alt || 'Product image',
    className: `object-contain transition-opacity duration-200 ${
      isLoaded ? 'opacity-100' : 'opacity-0'
    }`,
    onLoad: () => setIsLoaded(true),
    onError: handleError,
    priority,
    sizes,
  };

  return (
    <div
      className={`relative flex items-center justify-center bg-[#F7F7F5] overflow-hidden rounded-xl ${containerClasses} ${className}`}
    >
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 bg-neutral-100 animate-pulse" />
      )}

      {fill || (!size && !width && !height) ? (
        <Image {...commonProps} fill sizes={sizes || '100vw'} />
      ) : (
        <Image {...commonProps} width={imgWidth} height={imgHeight} />
      )}
    </div>
  );
}
