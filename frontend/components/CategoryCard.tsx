import Link from 'next/link';

interface CategoryCardProps {
  name: string;
  image: string;
  href: string;
}

export default function CategoryCard({ name, image, href }: CategoryCardProps) {
  return (
    <Link href={href} className="group flex flex-col items-center gap-3">
      <div className="relative w-24 h-24 md:w-32 md:h-32 rounded-full overflow-hidden bg-neutral-50 border border-neutral-100 shadow-sm group-hover:shadow-md group-hover:border-neutral-200 transition-all">
        <img 
          src={image} 
          alt={name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.currentTarget.src = '/assets/fallbacks/snacks.png';
          }}
        />
      </div>
      <span className="text-xs md:text-sm font-semibold text-neutral-700 text-center group-hover:text-neutral-900 transition-colors uppercase tracking-wider">
        {name}
      </span>
    </Link>
  );
}
