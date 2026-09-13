"use client";

import { useState, useEffect } from "react";
import { Sparkles, X, Bot, ChevronUp, Layers, Terminal } from "lucide-react";
import CommandBox from "@/components/CommandBox";

export default function FloatingCopilotDrawer() {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  return (
    <>
      {/* Floating Action Button */}
      {!isOpen && (
        <div className="fixed bottom-6 right-6 z-40 group">
          <button
            type="button"
            onClick={() => setIsOpen(true)}
            aria-label="Open NOVA Autonomous Copilot"
            className="flex items-center gap-2.5 px-4 py-3 rounded-full bg-[#131921] hover:bg-[#232F3E] text-white shadow-xl border-2 border-amber-400 hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer"
          >
            <div className="relative flex items-center justify-center">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse absolute -top-1 -right-1 ring-2 ring-[#131921]" />
              <Sparkles className="w-4 h-4 text-[#FF9900]" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-[10px] uppercase tracking-wider font-extrabold text-[#FF9900] leading-none">
                AI Copilot
              </span>
              <span className="text-xs font-bold text-white leading-tight">
                Ask NOVA
              </span>
            </div>
          </button>
        </div>
      )}

      {/* Slide-over Drawer Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Slide-over Drawer Panel */}
      <div
        className={`fixed top-0 right-0 bottom-0 w-full sm:w-[480px] md:w-[540px] bg-[#FCFBF9] z-50 shadow-2xl border-l border-neutral-200 flex flex-col transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Drawer Header */}
        <div className="px-5 py-4 bg-[#131921] text-white flex items-center justify-between border-b border-amber-500/30">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-400/20 border border-amber-400/40 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-[#FF9900]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">NOVA Copilot</span>
                <span className="text-[9px] bg-amber-400/20 text-amber-300 border border-amber-400/40 px-1.5 py-0.5 rounded font-mono uppercase">
                  AWS Strands
                </span>
              </div>
              <p className="text-[11px] text-neutral-400">
                Autonomous Household Decision Engine
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setIsOpen(false)}
            className="p-1.5 rounded-lg text-neutral-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
            aria-label="Close Copilot drawer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5">
          <CommandBox id="drawer-copilot" />
        </div>
      </div>
    </>
  );
}
