import React from 'react';
import { FileText, ExternalLink, Network, CheckCircle2, ShieldAlert, Award, Calendar } from 'lucide-react';

export default function EvidenceCard({ evidence, onViewSource, onShowGraph }) {
  const isSuperseded = evidence.status === "superseded";

  const getBadgeColor = (type) => {
    switch (type) {
      case 'Direct Evidence': return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case 'Supporting Evidence': return 'bg-violet-500/15 text-violet-400 border-violet-500/30';
      case 'Contradictory Evidence': return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      default: return 'bg-slate-500/15 text-[var(--text-muted)] border-slate-500/30';
    }
  };

  return (
    <div className={`nexus-card rounded-2xl p-4 transition-all hover:border-violet-400/40 relative flex flex-col justify-between ${
      isSuperseded ? 'border-amber-500/40 bg-amber-950/10' : 'border-[var(--border)]'
    }`}>
      {/* Top row */}
      <div>
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs font-bold text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded-md border border-violet-500/20">
              {evidence.document_id}
            </span>
            {evidence.page && (
              <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> Page {evidence.page}
              </span>
            )}
            {evidence.academic_year && (
              <span className="text-[10px] font-mono text-[var(--text-dim)] flex items-center gap-1">
                <Calendar className="w-3 h-3" /> {evidence.academic_year}
              </span>
            )}
            {isSuperseded && (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-bold">
                SUPERSEDED DRAFT
              </span>
            )}
          </div>

          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border shrink-0 ${getBadgeColor(evidence.evidence_type)}`}>
            {evidence.evidence_type}
          </span>
        </div>

        <h4 className="text-sm font-semibold text-[var(--text-strong)] mt-2 leading-snug line-clamp-2">
          {evidence.title}
        </h4>

        {/* Criterion & Department */}
        <div className="mt-1.5 flex items-center gap-2 text-[11px] text-[var(--text-muted)] font-mono">
          <span className="text-violet-400 font-medium">{evidence.department}</span>
          {evidence.criterion && (
            <>
              <span>•</span>
              <span className="text-amber-400">{evidence.criterion}</span>
            </>
          )}
        </div>

        {/* Excerpt */}
        <div className="mt-3">
          <p className="text-xs text-[var(--text-muted)] leading-relaxed italic line-clamp-3 bg-[var(--bg-deep)] p-2.5 rounded-xl border border-[var(--border)]">
            "{evidence.excerpt}"
          </p>
        </div>
      </div>

      {/* Footer / Actions */}
      <div className="mt-4 pt-3 border-t border-[var(--border)] flex items-center justify-between">
        <div className="flex items-center gap-2 text-[11px] font-mono text-[var(--text-dim)]">
          <span>Rel: <strong className="text-[var(--text-strong)]">{evidence.relevance}</strong></span>
          <span>•</span>
          <span>Strength: <strong className="text-emerald-400">{evidence.strength}</strong></span>
        </div>

        <div className="flex items-center gap-2">
          {onViewSource && (
            <button
              onClick={() => onViewSource(evidence)}
              className="text-xs font-semibold text-violet-400 hover:text-white px-2.5 py-1 rounded-xl bg-violet-500/10 hover:bg-violet-500/30 border border-violet-500/20 flex items-center gap-1.5 transition-all font-mono"
            >
              <ExternalLink className="w-3 h-3" />
              Source PDF
            </button>
          )}
          {onShowGraph && (
            <button
              onClick={() => onShowGraph(evidence.document_id)}
              className="text-xs font-medium text-[var(--text-muted)] hover:text-[var(--text-strong)] px-2 py-1 rounded-xl bg-[var(--surface-2)] border border-[var(--border)] flex items-center gap-1 transition-colors"
            >
              <Network className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
