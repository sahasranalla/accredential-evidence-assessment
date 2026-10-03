import React, { useState } from 'react';
import { Search, Sparkles, ArrowRight, Lightbulb, GraduationCap } from 'lucide-react';

export default function InvestigationInput({ onInvestigate, isLoading = false }) {
  const [question, setQuestion] = useState('');

  const sampleQueries = [
    {
      label: 'C2: Student-Faculty Ratio',
      text: 'Show student-to-faculty ratio for AY 2024-25 in CSE Department with signed committee minutes.'
    },
    {
      label: 'C3: Research Grants & Seed Funding',
      text: 'What are the seed research grants sanctioned in AY 2024-25 and list of journal publications?'
    },
    {
      label: 'C6: IQAC Meeting Minutes & ATR',
      text: 'Provide evidence of IQAC meetings and action taken reports conducted in 2024-25.'
    },
    {
      label: 'C4: Library ILMS & Automation',
      text: 'Show library expenditure and ILMS automation details for 2023-24 and 2024-25.'
    },
    {
      label: 'C5: Student Placements & Median Package',
      text: 'What are the student placement records and median salary for 2024-25 graduates?'
    },
    {
      label: 'Conflict: AI Workshop Participants',
      text: 'Verify participant count discrepancy between CSE AI Workshop reports.'
    },
    {
      label: 'Gap: Solar Logs 2021-22 (Insufficient)',
      text: 'Provide audited greenhouse gas emissions and solar panel generation logs for 2021-22.'
    }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onInvestigate(question.trim());
    }
  };

  return (
    <div className="nexus-card rounded-3xl p-6 md:p-7 relative overflow-hidden nexus-glow">
      <div className="absolute -top-20 -right-16 w-48 h-48 rounded-full bg-violet-400/10 blur-3xl pointer-events-none" />
      
      <div className="flex items-start gap-3 relative">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-violet-500/20 to-pink-400/20 border border-violet-400/20 flex items-center justify-center shrink-0">
          <GraduationCap className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-[var(--text-strong)]">
            Accreditation Evidence Search
          </h2>
          <p className="text-xs text-[var(--text-muted)] mt-1 max-w-3xl">
            Ask any question across NAAC Criteria 1–7. ACCREDIA scans 51 institutional documents, verifies physical PDF page citations, audits discrepancies, and constructs a grounded evidence dossier.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 relative">
        <Search className="w-5 h-5 text-[var(--text-dim)] absolute left-4 top-4 pointer-events-none" />
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
          placeholder="Ask about faculty ratios, research grants, IQAC minutes, library spending, placement statistics..."
          className="w-full bg-[var(--bg-deep)] border border-[var(--border)] focus:border-violet-400 rounded-2xl pl-12 pr-44 py-4 text-sm text-[var(--text)] placeholder-[var(--text-dim)] focus:outline-none focus:ring-4 focus:ring-violet-500/10 transition-all"
        />
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="absolute right-2 top-2 px-4 py-2.5 bg-gradient-to-r from-violet-600 via-purple-500 to-pink-400 hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed text-white text-[10px] font-bold rounded-xl flex items-center gap-2 shadow-lg shadow-violet-500/20 transition-all font-mono tracking-wider"
        >
          {isLoading ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              VERIFYING
            </>
          ) : (
            <>
              VERIFY EVIDENCE <ArrowRight className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </form>

      <div className="mt-5 flex items-start gap-2">
        <Lightbulb className="w-3.5 h-3.5 text-pink-400 mt-1 shrink-0" />
        <div className="flex flex-wrap gap-2">
          <span className="text-[10px] font-mono font-semibold text-[var(--text-dim)] mr-1 self-center">
            SAMPLE ACCREDITATION QUERIES:
          </span>
          {sampleQueries.map((item, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuestion(item.text);
                onInvestigate(item.text);
              }}
              title={item.text}
              className="text-[10px] bg-[var(--surface-2)] hover:bg-violet-500/10 text-[var(--text-muted)] hover:text-violet-400 px-2.5 py-1.5 rounded-xl border border-[var(--border)] hover:border-violet-400/30 transition-all text-left font-mono"
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
