"use client";

import Image from 'next/image';
import { useState, useEffect } from 'react';

interface ProductImageProps {
  src?: string | null;
  alt: string;
  category?: string;
  id?: string;
  product?: {
    id?: string;
    name?: string;
    title?: string;
    imageUrl?: string | null;
    image?: string | null;
    images?: string[];
    category?: string;
    [key: string]: any;
  } | null;
  /** Source of the resolved image URL — for console logging only */
  imageSource?: string | null;
  className?: string;
  sizes?: string;
  fill?: boolean;
  width?: number;
  height?: number;
  priority?: boolean;
}

export default function ProductImage({
  src,
  alt,
  category,
  id,
  product,
  imageSource,
  className = '',
  sizes,
  fill,
  width,
  height,
  priority = false,
}: ProductImageProps) {
  // Resolve candidate image URL from direct src or product object
  const candidateSrc =
    src ||
    product?.imageUrl ||
    product?.image ||
    product?.images?.[0] ||
    null;

  // Validate the URL — must be a real HTTPS/HTTP/relative URL, not fabricated
  const isValidUrl =
    typeof candidateSrc === 'string' &&
    candidateSrc.trim().length > 0 &&
    (candidateSrc.startsWith('http://') ||
      candidateSrc.startsWith('https://') ||
      candidateSrc.startsWith('/'));

  const [hasError, setHasError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    setHasError(false);
    setIsLoaded(false);
  }, [candidateSrc]);

  // If no authentic image URL exists or load failed, render neutral UI placeholder.
  // NEVER use emoji here. NEVER use AI-generated art here.
  if (!isValidUrl || hasError) {
    return (
      <div
        className={`flex flex-col items-center justify-center w-full h-full bg-neutral-50/80 text-neutral-400 p-2 sm:p-4 border border-neutral-100 rounded select-none overflow-hidden ${className}`}
        aria-label="Image unavailable"
      >
        <svg
          className="w-6 h-6 sm:w-7 sm:h-7 text-neutral-300 stroke-[1.5] mb-0.5 shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"
          />
        </svg>
        <span className="text-[10px] sm:text-[11px] font-medium tracking-tight text-neutral-400 truncate max-w-full">
          Image unavailable
        </span>
      </div>
    );
  }

  const commonProps = {
    src: candidateSrc!,
    alt: alt || 'Product image',
    className: `object-contain transition-opacity duration-200 ${
      isLoaded ? 'opacity-100' : 'opacity-0'
    } ${className}`,
    onLoad: () => setIsLoaded(true),
    onError: () => {
      console.warn(`[Commerce Image Load Error] Could not load image`, {
        id: id || product?.id,
        alt: alt || product?.name || product?.title,
        source: imageSource || 'unknown',
        url: candidateSrc,
      });
      setHasError(true);
    },
    priority,
    sizes,
  };

  return (
    <div className="relative w-full h-full flex items-center justify-center bg-white overflow-hidden rounded">
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 bg-neutral-100 animate-pulse" />
      )}

      {fill ? (
        <Image {...commonProps} fill sizes={sizes || '100vw'} />
      ) : (
        <Image
          {...commonProps}
          width={width || 400}
          height={height || 400}
        />
      )}
    </div>
  );
}
