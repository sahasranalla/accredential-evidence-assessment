import React, { useEffect, useState } from 'react';
import { getDocuments, getDocumentFileUrl } from '../services/api';
import EvidencePanel from '../components/EvidencePanel';
import { Search, FileText, ExternalLink, Calendar, Building, Award, Filter, FileCheck, CheckCircle2 } from 'lucide-react';

export default function Evidence() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('All');
  const [selectedCriterion, setSelectedCriterion] = useState('All');
  const [selectedYear, setSelectedYear] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('All');
  const [inspectedDoc, setInspectedDoc] = useState(null);

  useEffect(() => {
    async function fetchDocs() {
      try {
        const data = await getDocuments();
        setDocs(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchDocs();
  }, []);

  const departments = [
    'All', 'CSE', 'ECE', 'EEE', 'MECH', 'CIVIL', 'AIML', 'IT', 
    'IQAC', 'EXAMINATION', 'ADMISSIONS', 'PLACEMENT', 'LIBRARY', 'ADMINISTRATION'
  ];

  const criteria = [
    'All', 'Criterion 1', 'Criterion 2', 'Criterion 3', 
    'Criterion 4', 'Criterion 5', 'Criterion 6', 'Criterion 7'
  ];

  const academicYears = ['All', '2024-25', '2023-24', '2022-23', '2025-26'];

  const filtered = docs.filter(d => {
    const matchDept = selectedDept === 'All' || d.department === selectedDept;
    const matchCriterion = selectedCriterion === 'All' || d.criterion === selectedCriterion;
    const matchYear = selectedYear === 'All' || d.academic_year === selectedYear;
    const matchStatus = selectedStatus === 'All' || d.status === selectedStatus;
    const matchSearch = !search || 
      (d.title && d.title.toLowerCase().includes(search.toLowerCase())) || 
      (d.summary && d.summary.toLowerCase().includes(search.toLowerCase())) ||
      (d.document_id && d.document_id.toLowerCase().includes(search.toLowerCase()));
    return matchDept && matchCriterion && matchYear && matchStatus && matchSearch;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono font-bold uppercase tracking-[.18em] text-violet-400">
            <FileCheck className="w-3.5 h-3.5" />
            Institutional Archives
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--text-strong)] mt-1">
            Official Document & Evidence Library
          </h1>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            51 official college records, committee minutes, and audit reports verified for Vidyapath Institute of Technology.
          </p>
        </div>

        <div className="text-right">
          <span className="text-xs font-mono text-[var(--text-dim)]">
            Showing <strong className="text-violet-400 font-bold">{filtered.length}</strong> of {docs.length} Documents
          </span>
        </div>
      </div>

      {/* Multi-Filter Bar */}
      <div className="nexus-card rounded-2xl p-4 space-y-3">
        <div className="flex flex-col lg:flex-row gap-3 items-center justify-between">
          {/* Search box */}
          <div className="relative w-full lg:w-96">
            <Search className="w-4 h-4 text-[var(--text-dim)] absolute left-3 top-3 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by title, keywords, metric, or Doc ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[var(--bg-deep)] border border-[var(--border)] rounded-xl pl-9 pr-3 py-2 text-xs text-[var(--text-strong)] placeholder-[var(--text-dim)] focus:outline-none focus:border-violet-500 font-sans"
            />
          </div>

          {/* Filter dropdowns */}
          <div className="flex flex-wrap items-center gap-2 w-full lg:w-auto">
            {/* Criterion */}
            <select
              value={selectedCriterion}
              onChange={(e) => setSelectedCriterion(e.target.value)}
              className="bg-[var(--bg-deep)] border border-[var(--border)] text-xs text-[var(--text)] rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500 font-mono"
            >
              {criteria.map(c => (
                <option key={c} value={c}>{c === 'All' ? 'All Criteria (1–7)' : c}</option>
              ))}
            </select>

            {/* Department */}
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="bg-[var(--bg-deep)] border border-[var(--border)] text-xs text-[var(--text)] rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500 font-mono"
            >
              {departments.map(d => (
                <option key={d} value={d}>{d === 'All' ? 'All Departments' : d}</option>
              ))}
            </select>

            {/* Academic Year */}
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="bg-[var(--bg-deep)] border border-[var(--border)] text-xs text-[var(--text)] rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500 font-mono"
            >
              {academicYears.map(y => (
                <option key={y} value={y}>{y === 'All' ? 'All Academic Years' : `AY ${y}`}</option>
              ))}
            </select>

            {/* Status */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-[var(--bg-deep)] border border-[var(--border)] text-xs text-[var(--text)] rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500 font-mono"
            >
              <option value="All">All Statuses</option>
              <option value="active">Active Official</option>
              <option value="superseded">Superseded Draft</option>
            </select>
          </div>
        </div>
      </div>

      {/* Document Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-[var(--text-muted)] font-mono flex items-center justify-center gap-2">
          <div className="w-4 h-4 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
          <span>Scanning institutional repository...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((d) => (
            <div
              key={d.document_id}
              className="nexus-card rounded-2xl p-4 transition-all hover:border-violet-400/50 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-1.5">
                    <span className="text-violet-400 font-bold bg-violet-500/10 px-2 py-0.5 rounded-md border border-violet-500/20">
                      {d.document_id}
                    </span>
                    <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                      {d.file_type || 'PDF'}
                    </span>
                  </div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                    d.status === 'superseded' 
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
                      : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                  }`}>
                    {d.status || 'active'}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-[var(--text-strong)] mt-2.5 line-clamp-1">
                  {d.title}
                </h3>
                <p className="text-xs text-[var(--text-muted)] mt-1 line-clamp-2 leading-relaxed">
                  {d.summary}
                </p>

                <div className="mt-3 flex items-center gap-2 flex-wrap text-[11px] font-mono">
                  <span className="text-violet-400 font-medium">{d.department}</span>
                  {d.criterion && (
                    <>
                      <span className="text-[var(--text-dim)]">•</span>
                      <span className="text-amber-400">{d.criterion}</span>
                    </>
                  )}
                  {d.academic_year && (
                    <>
                      <span className="text-[var(--text-dim)]">•</span>
                      <span className="text-[var(--text-dim)]">AY {d.academic_year}</span>
                    </>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="mt-4 pt-3 border-t border-[var(--border)] flex items-center justify-between text-xs font-mono">
                <button
                  onClick={() => setInspectedDoc(d)}
                  className="text-violet-400 hover:text-violet-300 font-semibold flex items-center gap-1"
                >
                  Inspect Passages →
                </button>
                <a
                  href={getDocumentFileUrl(d.document_id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] text-[var(--text-dim)] hover:text-white px-2 py-1 rounded-lg bg-[var(--surface-2)] hover:bg-violet-600 flex items-center gap-1 transition-all"
                >
                  <ExternalLink className="w-3 h-3" />
                  PDF File
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {inspectedDoc && (
        <EvidencePanel document={inspectedDoc} onClose={() => setInspectedDoc(null)} />
      )}
    </div>
  );
}
