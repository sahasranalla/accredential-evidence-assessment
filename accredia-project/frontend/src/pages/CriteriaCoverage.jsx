import React, { useEffect, useState } from 'react';
import { getCriteriaCoverage } from '../services/api';
import { Award, CheckCircle, AlertCircle, BookOpen, Layers, BarChart2, ChevronRight, FileText } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function CriteriaCoverage() {
  const [coverage, setCoverage] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCriterion, setSelectedCriterion] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getCriteriaCoverage();
        setCoverage(data);
        if (data.length > 0) setSelectedCriterion(data[0]);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const totalEvidence = coverage.reduce((acc, c) => acc + (c.evidence_count || 0), 0);
  const avgCoverage = coverage.length
    ? Math.round(coverage.reduce((acc, c) => acc + (c.coverage_percentage || 0), 0) / coverage.length)
    : 0;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono font-bold uppercase tracking-[.18em] text-violet-500">
            <Award className="w-3.5 h-3.5" />
            Accreditation Intelligence
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--text-strong)] mt-1">
            Criteria Compliance & Evidence Coverage
          </h1>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            Vidyapath Institute of Technology (VITEC) · Real-time institutional readiness across NAAC Criteria 1–7.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="nexus-card rounded-2xl px-4 py-2 text-center border-violet-400/20">
            <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase">Overall Readiness</span>
            <div className="text-lg font-bold text-emerald-400 font-mono">{avgCoverage}%</div>
          </div>
          <div className="nexus-card rounded-2xl px-4 py-2 text-center border-violet-400/20">
            <span className="text-[10px] font-mono text-[var(--text-dim)] uppercase">Verified Chunks</span>
            <div className="text-lg font-bold text-violet-500 font-mono">{totalEvidence}</div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="nexus-card rounded-3xl p-6">
        <div className="flex items-center justify-between pb-3 border-b border-[var(--border)] mb-4">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-4 h-4 text-violet-500" />
            <h3 className="text-xs font-semibold text-[var(--text-strong)] uppercase tracking-wider font-mono">
              Evidence Depth by Accreditation Criterion
            </h3>
          </div>
          <span className="text-[10px] font-mono text-[var(--text-dim)]">Target vs Current Indexed Chunks</span>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={coverage}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a1f3d" opacity={0.3} />
              <XAxis dataKey="criterion_id" stroke="#84758f" fontSize={11} tickLine={false} />
              <YAxis stroke="#84758f" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--surface)',
                  borderColor: 'var(--border)',
                  fontSize: '11px',
                  borderRadius: '12px'
                }}
              />
              <Bar dataKey="evidence_count" name="Discovered Chunks" fill="#a78bfa" radius={[6, 6, 0, 0]} />
              <Bar dataKey="target_evidence" name="Benchmark Target" fill="#d17bbd" radius={[6, 6, 0, 0]} opacity={0.5} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Criteria Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {coverage.map((c) => {
          const isSelected = selectedCriterion?.criterion_id === c.criterion_id;
          return (
            <div
              key={c.criterion_id}
              onClick={() => setSelectedCriterion(c)}
              className={`nexus-card rounded-2xl p-5 cursor-pointer transition-all hover:-translate-y-0.5 border ${
                isSelected ? 'border-violet-500 shadow-lg shadow-violet-500/15 ring-2 ring-violet-500/20' : 'hover:border-violet-400/40'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold font-mono px-2 py-0.5 rounded-lg bg-violet-500/15 text-violet-400 border border-violet-500/25">
                  {c.criterion_id}
                </span>
                <span className="text-[10px] font-mono text-[var(--text-dim)]">Weight: {c.weightage} pts</span>
              </div>

              <h4 className="text-sm font-bold text-[var(--text-strong)] mt-3 line-clamp-1">{c.name}</h4>
              <p className="text-xs text-[var(--text-muted)] mt-1 line-clamp-2">{c.description}</p>

              {/* Progress */}
              <div className="mt-4 space-y-1.5">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="text-[var(--text-dim)]">Coverage Score</span>
                  <span className="font-bold text-emerald-400">{c.coverage_percentage}%</span>
                </div>
                <div className="h-2 rounded-full bg-[var(--bg-deep)] overflow-hidden border border-[var(--border)]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-violet-500 to-pink-400 transition-all duration-500"
                    style={{ width: `${Math.min(100, c.coverage_percentage)}%` }}
                  />
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-[var(--border)] flex items-center justify-between text-[11px] text-[var(--text-dim)] font-mono">
                <span>{c.evidence_count} evidence chunks</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${
                  c.status === 'Robust Coverage'
                    ? 'bg-emerald-500/15 text-emerald-400'
                    : 'bg-amber-500/15 text-amber-400'
                }`}>
                  {c.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Detail */}
      {selectedCriterion && (
        <div className="nexus-card rounded-3xl p-6 border-violet-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-violet-500/20 to-pink-400/20 border border-violet-400/20 flex items-center justify-center text-violet-500 font-mono font-bold">
              {selectedCriterion.criterion_id.replace('Criterion ', 'C')}
            </div>
            <div>
              <h3 className="text-base font-bold text-[var(--text-strong)]">
                {selectedCriterion.criterion_id}: {selectedCriterion.name}
              </h3>
              <p className="text-xs text-[var(--text-muted)]">{selectedCriterion.description}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="bg-[var(--bg-deep)] p-4 rounded-xl border border-[var(--border)]">
              <span className="text-[10px] font-mono uppercase text-[var(--text-dim)]">Assessment Metric Weight</span>
              <p className="text-xl font-bold font-mono text-[var(--text-strong)] mt-1">{selectedCriterion.weightage} / 1000</p>
            </div>
            <div className="bg-[var(--bg-deep)] p-4 rounded-xl border border-[var(--border)]">
              <span className="text-[10px] font-mono uppercase text-[var(--text-dim)]">Discovered Evidence Chunks</span>
              <p className="text-xl font-bold font-mono text-violet-400 mt-1">{selectedCriterion.evidence_count} Record Chunks</p>
            </div>
            <div className="bg-[var(--bg-deep)] p-4 rounded-xl border border-[var(--border)]">
              <span className="text-[10px] font-mono uppercase text-[var(--text-dim)]">Criterion Health Status</span>
              <p className="text-xl font-bold font-mono text-emerald-400 mt-1">{selectedCriterion.status}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
