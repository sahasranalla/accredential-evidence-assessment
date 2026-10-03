import React, { useEffect, useState } from 'react';
import { getEvidenceGaps } from '../services/api';
import { AlertTriangle, AlertOctagon, CheckCircle2, FileQuestion, ArrowRight, ShieldAlert, Sparkles, FileText, Check } from 'lucide-react';

export default function EvidenceGaps() {
  const [gaps, setGaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterPriority, setFilterPriority] = useState('All');

  useEffect(() => {
    async function load() {
      try {
        const data = await getEvidenceGaps();
        setGaps(data || []);
      } catch (err) {
        console.error("Failed to load evidence gaps:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const normalizedGaps = gaps.map((g) => ({
    id: g.gap_id || g.id || 'GAP-000',
    title: g.title || g.topic || 'Unspecified Evidence Deficiency',
    description: g.description || g.reason || 'This compliance area currently lacks sufficient documentation in the repository.',
    criterion: g.criterion || 'Accreditation Metric',
    subcriterion: g.subcriterion || g.department || 'Institutional Process',
    priority: (g.priority || g.severity || 'HIGH').toUpperCase(),
    missing_documents: g.suggested_documents || g.missing_documents || (g.missing_document ? [g.missing_document] : []),
    remediation: g.remediation_suggestion || g.remediation || "Request the designated Department Accreditation Coordinator to compile, stamp, and upload signed records to the IQAC archive."
  }));

  const filtered = normalizedGaps.filter(
    (g) => filterPriority === 'All' || g.priority === filterPriority.toUpperCase()
  );

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono font-bold uppercase tracking-[.18em] text-amber-400">
            <AlertTriangle className="w-3.5 h-3.5" />
            Accreditation Audit Readiness
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--text-strong)] mt-1">
            Institutional Evidence Gaps & Vulnerabilities
          </h1>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            Deficiencies, missing committee minutes, and unverified metrics identified across Vidyapath Institute of Technology archives.
          </p>
        </div>

        {/* Priority Filter Chips */}
        <div className="flex items-center gap-2 flex-wrap">
          {['All', 'HIGH', 'MEDIUM', 'LOW'].map((prio) => (
            <button
              key={prio}
              onClick={() => setFilterPriority(prio)}
              className={`text-xs font-mono font-bold px-3 py-1.5 rounded-xl border transition-all ${
                filterPriority === prio
                  ? 'bg-violet-600 text-white border-violet-500 shadow-lg shadow-violet-500/25'
                  : 'bg-[var(--surface)] text-[var(--text-muted)] border-[var(--border)] hover:bg-[var(--surface-3)]'
              }`}
            >
              {prio === 'All' ? 'All Gaps' : `${prio} PRIORITY`} (
              {prio === 'All' ? normalizedGaps.length : normalizedGaps.filter(g => g.priority === prio).length})
            </button>
          ))}
        </div>
      </div>

      {/* Summary Advisory Banner */}
      <div className="nexus-card rounded-3xl p-5 border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-[var(--surface)] to-transparent flex items-start gap-4 shadow-lg">
        <div className="w-11 h-11 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-[var(--text-strong)] font-mono">
            PEER TEAM AUDIT RISK ADVISORY
          </h3>
          <p className="text-xs text-[var(--text-muted)] mt-1 leading-relaxed">
            ACCREDIA has identified <strong className="text-amber-400 font-bold">{normalizedGaps.length} compliance gaps</strong> where verifiable proof is absent or incomplete in the institutional repository. Addressing these items before peer team inspection is critical to avoiding compliance deductions.
          </p>
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="p-12 text-center text-xs font-mono text-[var(--text-muted)] flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
          <span>Auditing institutional repositories for missing records...</span>
        </div>
      )}

      {/* Gaps List */}
      {!loading && (
        <div className="space-y-4">
          {filtered.map((gap) => {
            const isHigh = gap.priority === 'HIGH' || gap.priority === 'CRITICAL';
            return (
              <div
                key={gap.id}
                className={`nexus-card rounded-3xl p-6 border transition-all hover:border-amber-400/50 shadow-md ${
                  isHigh ? 'border-rose-500/30 bg-gradient-to-br from-rose-500/5 via-[var(--surface)] to-transparent' : 'border-[var(--border)]'
                }`}
              >
                {/* Top Row: Priority Badge + Criterion + Subcriterion + ID */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-[var(--border)]">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span
                      className={`text-[10px] font-mono font-black px-2.5 py-0.5 rounded-lg border ${
                        isHigh
                          ? 'bg-rose-500/20 text-rose-400 border-rose-500/30 shadow-sm'
                          : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {gap.priority} PRIORITY
                    </span>
                    <span className="text-xs font-mono font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-md border border-amber-500/20">
                      {gap.criterion}
                    </span>
                    <span className="text-xs font-mono text-[var(--text-dim)]">
                      {gap.subcriterion}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-[var(--text-dim)] font-bold">
                    {gap.id}
                  </span>
                </div>

                {/* Title & Detailed Reason */}
                <div className="mt-4">
                  <h3 className="text-base font-bold text-[var(--text-strong)] leading-snug">
                    {gap.title}
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-1.5 leading-relaxed bg-[var(--bg-deep)] p-3 rounded-xl border border-[var(--border)]">
                    <strong className="text-[var(--text-strong)] font-mono uppercase text-[10px] block mb-1">
                      Deficiency Context & Audit Analysis:
                    </strong>
                    {gap.description}
                  </p>
                </div>

                {/* Two Column Grid: Missing Documents & Actionable Remediation */}
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Missing Records List */}
                  <div className="bg-[var(--bg-deep)] p-4 rounded-2xl border border-rose-500/20">
                    <div className="flex items-center gap-2 text-[10px] font-mono uppercase text-rose-400 font-bold mb-2">
                      <FileQuestion className="w-3.5 h-3.5" />
                      <span>Required Missing Documentary Proof ({gap.missing_documents.length})</span>
                    </div>
                    <ul className="space-y-1.5 text-xs text-[var(--text-muted)]">
                      {gap.missing_documents.length > 0 ? (
                        gap.missing_documents.map((doc, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-rose-400 font-bold mt-0.5">•</span>
                            <span className="text-[var(--text-strong)] font-medium">{doc}</span>
                          </li>
                        ))
                      ) : (
                        <li className="italic text-[var(--text-dim)]">Specific document records uncataloged.</li>
                      )}
                    </ul>
                  </div>

                  {/* Remediation Plan */}
                  <div className="bg-[var(--bg-deep)] p-4 rounded-2xl border border-emerald-500/20">
                    <div className="flex items-center gap-2 text-[10px] font-mono uppercase text-emerald-400 font-bold mb-2">
                      <Check className="w-3.5 h-3.5" />
                      <span>Actionable Remediation Protocol</span>
                    </div>
                    <p className="text-xs text-[var(--text-muted)] leading-relaxed">
                      {gap.remediation}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
