import React from 'react';
import { Check, Loader2, Search, Network, FileCheck2, Sparkles, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function InvestigationProgress({ activeStep = 1, totalSteps = 7 }) {
  const stages = [
    ['Criterion Analysis', Search],
    ['Hybrid Vector Search', Search],
    ['Passage Scoring', FileCheck2],
    ['Page Verification', ShieldCheck],
    ['Graph Assembly', Network],
    ['Gap & Conflict Audit', AlertTriangle],
    ['Dossier Synthesis', Sparkles]
  ];

  return (
    <div className="nexus-card rounded-3xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[.16em] text-violet-500 font-mono">
            Accreditation Verification Pipeline
          </div>
          <div className="text-xs text-[var(--text-muted)] mt-0.5">
            ACCREDIA is cross-referencing institutional archives, checking page bounds, and assembling evidence.
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400 border border-violet-500/25 font-bold">
          STAGE {Math.min(activeStep, 7)} / 7
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2">
        {stages.map(([label, Icon], i) => {
          const n = i + 1;
          const done = n < activeStep;
          const current = n === activeStep;

          return (
            <div
              key={label}
              className={`relative rounded-2xl p-3 border transition-all ${
                done
                  ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
                  : current
                  ? 'bg-gradient-to-br from-violet-500/15 to-pink-400/10 border-violet-400/40 text-[var(--text-strong)] shadow-lg shadow-violet-500/10'
                  : 'bg-[var(--surface-2)] border-[var(--border)] text-[var(--text-dim)]'
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-lg flex items-center justify-center bg-[var(--surface)] border border-[var(--border)] shrink-0">
                  {done ? (
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                  ) : current ? (
                    <Loader2 className="w-3.5 h-3.5 text-violet-400 animate-spin" />
                  ) : (
                    <Icon className="w-3.5 h-3.5 text-[var(--text-dim)]" />
                  )}
                </span>
                <span className="text-[9px] font-semibold leading-tight font-mono">{label}</span>
              </div>
              {current && (
                <div className="absolute bottom-0 left-3 right-3 h-0.5 rounded-full bg-gradient-to-r from-violet-500 to-pink-400 animate-pulse" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
