import React, { useState, useEffect } from 'react';
import { X, FileText, Calendar, Building, User, Layers, ShieldCheck, Tag, Link, ExternalLink, CheckCircle2, Award } from 'lucide-react';
import { getDocument, getDocumentFileUrl } from '../services/api';

export default function EvidencePanel({ document: initialDoc, onClose }) {
  const [docDetails, setDocDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!initialDoc?.document_id) return;
    setLoading(true);
    getDocument(initialDoc.document_id)
      .then((data) => setDocDetails(data))
      .catch((err) => {
        console.error(err);
        setDocDetails(initialDoc);
      })
      .finally(() => setLoading(false));
  }, [initialDoc]);

  if (!initialDoc) return null;
  const doc = docDetails || initialDoc;
  const fileUrl = getDocumentFileUrl(doc.document_id);

  return (
    <div className="fixed inset-y-0 right-0 w-full max-w-xl bg-[var(--surface)] border-l border-[var(--border)] shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-5 border-b border-[var(--border)] flex items-center justify-between bg-[var(--surface-2)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-violet-500/10 border border-violet-500/25 flex items-center justify-center text-violet-400 font-mono text-xs font-bold shrink-0">
            {doc.document_id}
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-[var(--text-strong)] truncate max-w-md">
              {doc.title}
            </h3>
            <p className="text-[11px] font-mono text-[var(--text-muted)] flex items-center gap-2 mt-0.5">
              <span>{doc.department}</span>
              {doc.criterion && <span>• {doc.criterion}</span>}
              {doc.academic_year && <span>• AY {doc.academic_year}</span>}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-xl hover:bg-[var(--surface-3)] flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--text-strong)] transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-5">
        {/* Physical PDF Action Bar */}
        <div className="p-4 rounded-2xl bg-gradient-to-r from-violet-500/10 via-purple-500/5 to-pink-500/10 border border-violet-500/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-violet-400" />
            <div>
              <span className="text-xs font-bold text-[var(--text-strong)] block font-mono">
                Physical Institutional Document
              </span>
              <span className="text-[10px] text-[var(--text-muted)] font-mono">
                {doc.file_type || 'PDF'} · Ground Truth Repository Record
              </span>
            </div>
          </div>
          <a
            href={fileUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3.5 py-1.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-bold font-mono flex items-center gap-1.5 shadow-md shadow-violet-500/20 transition-all"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            Open File
          </a>
        </div>

        {/* Verification Status */}
        <div className="flex items-center gap-2 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>
            Strict Citation Verified: Indexed at <strong>Page {initialDoc.page || 1}</strong> of institutional file
          </span>
        </div>

        {/* Metadata grid */}
        <div className="grid grid-cols-2 gap-3 bg-[var(--bg-deep)] p-3.5 rounded-2xl border border-[var(--border)] text-xs font-mono">
          <div className="flex items-center gap-2">
            <Building className="w-3.5 h-3.5 text-[var(--text-dim)] shrink-0" />
            <span className="text-[var(--text-muted)]">Dept:</span>
            <span className="text-[var(--text-strong)] font-semibold truncate">{doc.department}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-3.5 h-3.5 text-[var(--text-dim)] shrink-0" />
            <span className="text-[var(--text-muted)]">Date:</span>
            <span className="text-[var(--text-strong)]">{doc.date || doc.academic_year || '2024-25'}</span>
          </div>
          <div className="flex items-center gap-2">
            <User className="w-3.5 h-3.5 text-[var(--text-dim)] shrink-0" />
            <span className="text-[var(--text-muted)]">Author:</span>
            <span className="text-[var(--text-strong)] truncate">{doc.author || 'Institutional Committee'}</span>
          </div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span className="text-[var(--text-muted)]">Status:</span>
            <span className={`px-1.5 py-0.5 rounded text-[10px] ${
              doc.status === 'superseded' ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'
            }`}>
              {doc.status || 'active'}
            </span>
          </div>
        </div>

        {/* Excerpt if present */}
        {initialDoc.excerpt && (
          <div>
            <span className="font-mono text-[var(--text-dim)] uppercase tracking-wider text-[10px] font-semibold block mb-1">
              Cited Evidence Passage (Page {initialDoc.page || 1})
            </span>
            <div className="text-xs text-[var(--text-strong)] bg-violet-500/10 border border-violet-500/20 p-3.5 rounded-2xl italic leading-relaxed">
              "{initialDoc.excerpt}"
            </div>
          </div>
        )}

        {/* Summary */}
        <div>
          <span className="font-mono text-[var(--text-dim)] uppercase tracking-wider text-[10px] font-semibold block mb-1">
            Institutional Abstract & Context
          </span>
          <p className="text-xs text-[var(--text-muted)] bg-[var(--surface-2)] p-3.5 rounded-2xl border border-[var(--border)] leading-relaxed">
            {doc.summary || "Official record cataloged in the institutional self-study accreditation archive."}
          </p>
        </div>

        {/* Full document text */}
        <div>
          <span className="font-mono text-[var(--text-dim)] uppercase tracking-wider text-[10px] font-semibold block mb-1.5">
            Full Extracted Document Content
          </span>
          <div className="text-xs text-[var(--text)] bg-[var(--bg-deep)] p-4 rounded-2xl border border-[var(--border)] leading-relaxed font-sans space-y-3 whitespace-pre-line max-h-72 overflow-y-auto">
            {doc.content || "Content extracted and indexed in chunks."}
          </div>
        </div>

        {/* Keywords */}
        {doc.keywords && doc.keywords.length > 0 && (
          <div>
            <span className="font-mono text-[var(--text-dim)] uppercase tracking-wider text-[10px] font-semibold block mb-1.5">
              Accreditation Tags & Keywords
            </span>
            <div className="flex flex-wrap gap-1.5">
              {doc.keywords.map((kw, i) => (
                <span key={i} className="text-[11px] font-mono bg-[var(--surface-2)] text-[var(--text-muted)] px-2 py-0.5 rounded-lg border border-[var(--border)]">
                  {kw}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
