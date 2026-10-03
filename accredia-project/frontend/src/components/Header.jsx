import React from 'react';
import { Sparkles, Moon, Sun, ShieldCheck, CheckCircle2, Building2 } from 'lucide-react';

export default function Header({ 
  title, 
  subtitle, 
  mode = 'Strict Citation Mode', 
  theme = 'light', 
  onToggleTheme 
}) {
  return (
    <header className="h-[72px] bg-[var(--header)] backdrop-blur-xl border-b border-[var(--border)] px-7 flex items-center justify-between sticky top-0 z-20">
      <div className="min-w-0">
        <h1 className="text-[15px] font-bold tracking-tight text-[var(--text-strong)] truncate">
          {title}
        </h1>
        <p className="text-xs text-[var(--text-muted)] mt-0.5 truncate">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Institution Badge */}
        <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-mono font-semibold border border-[var(--border)] bg-[var(--surface-2)] text-[var(--text-strong)]">
          <Building2 className="w-3 h-3 text-violet-500" />
          <span>VITEC · Hyderabad</span>
        </div>

        {/* Verification Status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-mono font-semibold border border-emerald-500/25 bg-emerald-500/10 text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" />
          PAGE-VERIFIED
        </div>

        {/* Retrieval Mode */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-mono font-semibold border border-purple-400/30 bg-purple-400/10 text-purple-400">
          <Sparkles className="w-3.5 h-3.5" />
          FAISS HYBRID RAG
        </div>

        {/* Dark/Light toggle */}
        <button
          onClick={onToggleTheme}
          title="Toggle dark/light mode"
          className="w-9 h-9 rounded-xl border border-[var(--border)] bg-[var(--surface)] hover:bg-[var(--surface-3)] flex items-center justify-center text-[var(--text-muted)] transition-all hover:-translate-y-0.5"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-violet-500" />}
        </button>

        {/* Accreditation Seal */}
        <div 
          title="NAAC Accreditation Verification Engine"
          className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500 to-pink-400 flex items-center justify-center text-white shadow-lg shadow-purple-500/15"
        >
          <ShieldCheck className="w-4 h-4" />
        </div>
      </div>
    </header>
  );
}
