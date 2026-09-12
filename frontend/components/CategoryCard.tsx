import Link from "next/link";

interface CategoryCardProps {
  name: string;
  categoryKey?: string;
  image?: string;
  href: string;
}

export default function CategoryCard({ name, categoryKey, image, href }: CategoryCardProps) {
  const key = (categoryKey || name).toLowerCase();

  const renderCategoryIcon = () => {
    if (key.includes("milk") || key.includes("dairy")) {
      return (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M7 2h10v3H7zM5 8h14v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V8zM8 12h8" />
        </svg>
      );
    }
    if (key.includes("noodle") || key.includes("maggi") || key.includes("snack") || key.includes("biscuit")) {
      return (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#D97706" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 21a9 9 0 0 0 9-9H3a9 9 0 0 0 9 9zM6 12V5M10 12V3M14 12V3M18 12V5" />
        </svg>
      );
    }
    if (key.includes("oil") || key.includes("ghee")) {
      return (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
        </svg>
      );
    }
    if (key.includes("rice") || key.includes("atta") || key.includes("flour") || key.includes("dal") || key.includes("grain")) {
      return (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 2v20M18 2v20M12 2v20M2 12h20" />
          <circle cx="12" cy="12" r="9" />
        </svg>
      );
    }
    if (key.includes("clean") || key.includes("detergent") || key.includes("bath") || key.includes("wash")) {
      return (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0284C7" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
      );
    }
    if (key.includes("tea") || key.includes("coffee") || key.includes("beverage") || key.includes("drink")) {
      return (
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#92400E" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8h1a4 4 0 0 1 0 8h-1M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8zM6 1v3M10 1v3M14 1v3" />
        </svg>
      );
    }
    return (
      <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#4B5563" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
      </svg>
    );
  };

  const hasRealImage = image && !image.includes("fallbacks") && !image.includes("assets/products");

  return (
    <Link href={href} className="group flex flex-col items-center gap-2">
      <div className="w-20 h-20 md:w-24 md:h-24 rounded-2xl bg-white border border-neutral-200 shadow-xs flex items-center justify-center group-hover:border-[#FF9900] group-hover:shadow-sm transition-all">
        {hasRealImage ? (
          <img
            src={image}
            alt={name}
            className="w-full h-full object-cover rounded-2xl group-hover:scale-105 transition-transform"
          />
        ) : (
          renderCategoryIcon()
        )}
      </div>
      <span className="text-xs font-semibold text-neutral-700 text-center group-hover:text-neutral-900 transition-colors">
        {name}
      </span>
    </Link>
  );
}
