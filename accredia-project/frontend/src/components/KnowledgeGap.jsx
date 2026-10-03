import React from 'react';
import { CheckCircle2, HelpCircle, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function KnowledgeGap({ established = [], stillNeeded = [] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* WHAT ACCREDIA HAS VERIFIED */}
      <div className="nexus-card rounded-2xl p-5 border-emerald-500/20 bg-gradient-to-br from-emerald-500/5 to-transparent">
        <div className="flex items-center justify-between pb-3 border-b border-[var(--border)]">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-semibold text-[var(--text-strong)] uppercase tracking-wider font-mono">
              Established Accreditation Facts
            </h4>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold">
            {established.length} Grounded Facts
          </span>
        </div>

        <ul className="mt-3.5 space-y-2">
          {established.length === 0 ? (
            <li className="text-xs text-[var(--text-dim)] italic">No established facts yet.</li>
          ) : (
            established.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-[var(--text-muted)] leading-relaxed">
                <span className="text-emerald-400 font-bold mt-0.5 shrink-0">✓</span>
                <span>{item}</span>
              </li>
            ))
          )}
        </ul>
      </div>

      {/* WHAT ACCREDIA STILL NEEDS */}
      <div className="nexus-card rounded-2xl p-5 border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-transparent">
        <div className="flex items-center justify-between pb-3 border-b border-[var(--border)]">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs font-semibold text-[var(--text-strong)] uppercase tracking-wider font-mono">
              Institutional Evidence Gaps
            </h4>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 font-bold">
            {stillNeeded.length} Deficiencies
          </span>
        </div>

        <ul className="mt-3.5 space-y-2">
          {stillNeeded.length === 0 ? (
            <li className="text-xs text-emerald-400 font-medium flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              All evidentiary requirements verified across archives.
            </li>
          ) : (
            stillNeeded.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2.5 text-xs text-amber-300/90 leading-relaxed">
                <span className="text-amber-400 font-bold mt-0.5 shrink-0">⚠</span>
                <span>{item}</span>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}
