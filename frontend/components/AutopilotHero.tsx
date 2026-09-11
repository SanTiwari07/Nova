import Image from 'next/image';
import Link from 'next/link';

interface AutopilotHeroProps {
  trackedItems: number;
  decisionsCount: number;
  budgetRemaining: number;
}

export default function AutopilotHero({ trackedItems, decisionsCount, budgetRemaining }: AutopilotHeroProps) {
  return (
    <div className="relative w-full h-[400px] rounded-3xl overflow-hidden mb-12 shadow-sm border border-neutral-200/50">
      <Image
        src="/assets/fallbacks/hero.png"
        alt="Household Autopilot Background"
        fill
        className="object-cover"
        priority
      />
      <div className="absolute inset-0 bg-gradient-to-r from-white/95 via-white/80 to-transparent"></div>
      
      <div className="absolute inset-0 p-12 flex flex-col justify-center max-w-xl">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs font-bold tracking-widest text-green-700 uppercase">AUTOPILOT ACTIVE</span>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-extrabold text-neutral-900 leading-tight mb-6">
          Your household is <br /> taken care of.
        </h1>
        
        <div className="flex flex-col gap-2 mb-8 text-neutral-700 font-medium">
          <p className="flex items-center gap-3">
             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
             {trackedItems} items monitored
          </p>
          <p className="flex items-center gap-3">
             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
             {decisionsCount} decision{decisionsCount !== 1 ? 's' : ''} needs attention
          </p>
          <p className="flex items-center gap-3">
             <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
             ₹{budgetRemaining} remaining budget
          </p>
        </div>
        
        <div>
          <Link href="#decisions" className="px-6 py-3 bg-neutral-900 text-white rounded-xl font-semibold shadow-md hover:bg-neutral-800 transition-colors">
            View Decisions
          </Link>
        </div>
      </div>
    </div>
  );
}
