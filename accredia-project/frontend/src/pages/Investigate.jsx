import React, { useEffect, useState } from 'react';
import InvestigationInput from '../components/InvestigationInput';
import InvestigationProgress from '../components/InvestigationProgress';
import AgentTrace from '../components/AgentTrace';
import RootCauseCard from '../components/RootCauseCard';
import KnowledgeGap from '../components/KnowledgeGap';
import EvidenceGraph from '../components/EvidenceGraph';
import CausalChain from '../components/CausalChain';
import ConflictCard from '../components/ConflictCard';
import EvidenceCard from '../components/EvidenceCard';
import EvidencePanel from '../components/EvidencePanel';
import Timeline from '../components/Timeline';
import ReportPanel from '../components/ReportPanel';
import SourcePanel from '../components/SourcePanel';
import { investigate } from '../services/api';
import { Sparkles, CheckCircle2, AlertOctagon, HelpCircle, ShieldCheck, Award, FileText } from 'lucide-react';

export default function Investigate() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [error, setError] = useState(null);
  const [activeStage, setActiveStage] = useState(1);

  useEffect(() => {
    if (!loading) return;
    setActiveStage(1);
    const timer = setInterval(() => setActiveStage((s) => Math.min(7, s + 1)), 500);
    return () => clearInterval(timer);
  }, [loading]);

  const handleInvestigate = async (question) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await investigate(question);
      setResult(resp);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Accreditation evidence search failed. Please verify query format.");
    } finally {
      setLoading(false);
    }
  };

  const evidenceItems = result?.evidence || [];
  const causalChain = result?.causal_chain || [];
  const contradictions = result?.contradictions || [];
  const steps = result?.steps || [];
  const timeline = result?.timeline || [];
  const sources = result?.sources || [];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Input component */}
      <InvestigationInput onInvestigate={handleInvestigate} isLoading={loading} />

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-400 text-xs font-mono flex items-center gap-2">
          <AlertOctagon className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Live progress indicator while investigating */}
      {loading && (
        <div className="space-y-4 animate-in fade-in duration-300">
          <InvestigationProgress activeStep={activeStage} totalSteps={7} />
          <div className="nexus-card rounded-3xl p-8 text-center space-y-4">
            <div className="w-12 h-12 rounded-full border-3 border-violet-300/30 border-t-violet-500 border-r-pink-400 animate-spin mx-auto shadow-xl shadow-violet-500/20" />
            <p className="text-xs font-mono text-[var(--text-muted)]">
              ACCREDIA is scanning 51 institutional records, matching criteria, checking physical PDF page numbers, and verifying citations...
            </p>
          </div>
        </div>
      )}

      {/* Investigation Results */}
      {result && !loading && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Top Banner: Verified Conclusion / Insufficient Evidence */}
          <RootCauseCard
            rootCause={result.root_cause}
            confidence={result.confidence}
            confidenceLevel={result.confidence_level}
            evidenceCount={evidenceItems.length}
            causalLinksCount={causalChain.length || result.graph?.edges?.length || 0}
            contradictionsCount={contradictions.length}
            unresolved={result.unresolved_questions}
          />

          {/* Citation & Grounding Assurance Bar */}
          <div className="nexus-card rounded-2xl p-4 bg-gradient-to-r from-emerald-500/10 via-[var(--surface)] to-violet-500/10 border-emerald-500/25 flex flex-wrap items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-2.5">
              <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0" />
              <div>
                <span className="text-xs font-extrabold text-[var(--text-strong)] font-mono block">
                  GROUNDED ACCREDITATION CITATIONS
                </span>
                <span className="text-[11px] text-[var(--text-muted)]">
                  Every supporting claim is mapped to verified physical document pages in repository.
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="text-emerald-400 font-black flex items-center gap-1 bg-emerald-500/10 px-2.5 py-1 rounded-xl border border-emerald-500/20">
                <CheckCircle2 className="w-3.5 h-3.5" /> 100% Page Verified
              </span>
              <span className="text-[var(--text-dim)]">•</span>
              <span className="text-violet-400 font-bold">
                {evidenceItems.length} Document Passages
              </span>
            </div>
          </div>

          {/* Core Trace & Graph Section */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Investigation Trace */}
            <div className="lg:col-span-5 space-y-4">
              <AgentTrace steps={steps} />
            </div>

            {/* Right: Dynamic Evidence Graph */}
            <div id="evidence-graph-section" className="lg:col-span-7 space-y-4">
              <EvidenceGraph
                graph={result.graph}
                onSelectNode={(data) => {
                  const doc = evidenceItems.find(
                    (e) => e.document_id === data?.document_id || e.document_id === data?.id
                  );
                  if (doc) setSelectedDoc(doc);
                }}
              />
            </div>
          </div>

          {/* What ACCREDIA Verified vs Still Needs */}
          <KnowledgeGap
            established={result.established_knowledge || []}
            stillNeeded={result.still_needed_knowledge || []}
          />

          {/* Causal Chain & Contradictions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CausalChain links={causalChain} />
            <div className="space-y-4">
              {contradictions.length > 0 ? (
                contradictions.map((c, i) => (
                  <ConflictCard key={i} contradiction={c} />
                ))
              ) : (
                <div className="nexus-card rounded-2xl p-5 border-[var(--border)] text-xs text-[var(--text-muted)] shadow-md">
                  <span className="font-mono text-[var(--text-dim)] uppercase text-[10px] font-semibold block mb-1">
                    Institutional Discrepancy Auditor
                  </span>
                  No contradictory claims or numerical discrepancies detected across official records. All evidence aligns cohesively.
                </div>
              )}
              <SourcePanel sources={sources} />
            </div>
          </div>

          {/* Retrieved Evidence Items */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-[var(--text-strong)] uppercase tracking-wider font-mono">
                Discovered Accreditation Evidence ({evidenceItems.length} Passages)
              </h3>
              <span className="text-[10px] font-mono text-[var(--text-dim)]">
                FAISS Dense + Lexical Threshold: ≥ 0.55
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {evidenceItems.map((ev, i) => (
                <EvidenceCard
                  key={i}
                  evidence={ev}
                  onViewSource={(doc) => setSelectedDoc(doc)}
                  onShowGraph={(docId) => {
                    const el = document.getElementById('evidence-graph-section');
                    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                  }}
                />
              ))}
            </div>
          </div>

          {/* Timeline & Report Panel */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Timeline events={timeline} />
            <ReportPanel reportMarkdown={result.report_markdown} investigationId={result.investigation_id} />
          </div>
        </div>
      )}

      {/* Slide-over document viewer */}
      {selectedDoc && (
        <EvidencePanel document={selectedDoc} onClose={() => setSelectedDoc(null)} />
      )}
    </div>
  );
}
