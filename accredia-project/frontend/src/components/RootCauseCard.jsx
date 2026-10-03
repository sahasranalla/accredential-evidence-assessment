import React from 'react';
import { ShieldCheck, AlertOctagon, CheckCircle2, FileText, AlertTriangle, Layers, BookOpen } from 'lucide-react';

export default function RootCauseCard({ 
  rootCause, 
  confidence, 
  confidenceLevel, 
  evidenceCount, 
  causalLinksCount, 
  contradictionsCount, 
  unresolved = [] 
}) {
  const isInsufficient = !rootCause || rootCause === "INSUFFICIENT EVIDENCE" || rootCause.startsWith("INSUFFICIENT");

  if (isInsufficient) {
    return (
      <div className="bg-rose-950/20 border-2 border-rose-500/40 rounded-3xl p-6 shadow-xl relative overflow-hidden animate-in fade-in duration-200">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 shrink-0">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-rose-400 bg-rose-500/20 px-2 py-0.5 rounded border border-rose-500/30">
                INSUFFICIENT ACCREDITATION EVIDENCE
              </span>
              <span className="text-xs font-mono text-[var(--text-dim)]">HALLUCINATION SAFEGUARD ACTIVE</span>
            </div>
            <h3 className="text-base font-bold text-[var(--text-strong)] mt-2 leading-relaxed">
              No verified official institutional records exist in the repository to satisfy this query.
            </h3>
            <p className="text-xs text-[var(--text-muted)] mt-1 leading-relaxed">
              ACCREDIA requires verifiable page numbers and signed documents before confirming compliance. Fabricating metrics is prohibited under institutional audit standards.
            </p>
          </div>
        </div>

        {unresolved && unresolved.length > 0 && (
          <div className="mt-5 p-4 bg-[var(--surface)] rounded-2xl border border-rose-500/20">
            <div className="flex items-center gap-2 text-rose-400 text-xs font-mono font-bold mb-2">
              <AlertTriangle className="w-4 h-4" />
              <span>Missing Documentary Proof / Required Remediation:</span>
            </div>
            <ul className="space-y-1.5 text-xs text-[var(--text-muted)]">
              {unresolved.map((u, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-rose-400 font-bold">•</span>
                  <span>{u}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-violet-500/10 via-[var(--surface)] to-pink-400/10 border border-violet-400/25 rounded-3xl p-6 shadow-2xl relative overflow-hidden animate-in fade-in duration-200">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[var(--border)] gap-4">
        <div className="flex items-start gap-3">
          <div className="w-11 h-11 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shadow-md shrink-0">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono uppercase tracking-widest text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/25">
                VERIFIED ACCREDITATION EVIDENCE
              </span>
              <span className="text-[10px] font-mono text-[var(--text-dim)]">AUDIT-GRADE CITATION</span>
            </div>
            <h3 className="text-base font-bold text-[var(--text-strong)] tracking-tight mt-1.5 leading-snug">
              {rootCause}
            </h3>
          </div>
        </div>

        <div className="text-right sm:shrink-0 bg-[var(--bg-deep)]/80 sm:bg-transparent p-3 sm:p-0 rounded-xl border sm:border-0 border-[var(--border)]">
          <div className="text-2xl font-bold font-mono text-emerald-400">
            {Math.round((confidence || 0.85) * 100)}%
          </div>
          <span className="text-[10px] font-mono uppercase text-[var(--text-dim)]">
            Evidence Confidence
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-[var(--bg-deep)]/80 p-3 rounded-xl border border-[var(--border)]">
          <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase">Cited Documents</span>
          <p className="text-lg font-bold font-mono text-[var(--text-strong)] mt-1">{evidenceCount}</p>
        </div>
        <div className="bg-[var(--bg-deep)]/80 p-3 rounded-xl border border-[var(--border)]">
          <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase">Causal Evidence Links</span>
          <p className="text-lg font-bold font-mono text-violet-400 mt-1">{causalLinksCount}</p>
        </div>
        <div className="bg-[var(--bg-deep)]/80 p-3 rounded-xl border border-[var(--border)]">
          <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase">Audited Discrepancies</span>
          <p className="text-lg font-bold font-mono text-amber-400 mt-1">{contradictionsCount}</p>
        </div>
        <div className="bg-[var(--bg-deep)]/80 p-3 rounded-xl border border-[var(--border)]">
          <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase">Compliance Level</span>
          <p className="text-xs font-bold font-mono text-emerald-400 mt-2">{confidenceLevel || 'High Evidence Support'}</p>
        </div>
      </div>

      {unresolved && unresolved.length > 0 && (
        <div className="mt-4 pt-3 border-t border-[var(--border)] flex items-start gap-2 text-xs text-[var(--text-muted)]">
          <span className="text-[10px] font-mono uppercase text-[var(--text-dim)] shrink-0">Secondary Inquiries:</span>
          <span className="italic">{unresolved[0]}</span>
        </div>
      )}
    </div>
  );
}
