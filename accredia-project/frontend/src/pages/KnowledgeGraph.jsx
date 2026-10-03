import React, { useEffect, useState } from 'react';
import { getInvestigations, getGraph, getMasterGraph, getDocument } from '../services/api';
import EvidenceGraph from '../components/EvidenceGraph';
import EvidencePanel from '../components/EvidencePanel';
import { Network, Layers, Sparkles, Filter } from 'lucide-react';

export default function KnowledgeGraph() {
  const [investigations, setInvestigations] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState('master');
  const [currentGraph, setCurrentGraph] = useState(null);
  const [inspectedDoc, setInspectedDoc] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [invs, masterG] = await Promise.all([
          getInvestigations().catch(() => []),
          getMasterGraph().catch(() => null)
        ]);

        setInvestigations(invs || []);
        if (masterG) {
          setCurrentGraph(masterG);
          setSelectedCaseId('master');
        } else if (invs && invs.length > 0) {
          const firstId = invs[0].investigation_id;
          setSelectedCaseId(firstId);
          const g = await getGraph(firstId);
          setCurrentGraph(g);
        }
      } catch (err) {
        console.error('Failed to load knowledge graph:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleSelectCase = async (caseId) => {
    setSelectedCaseId(caseId);
    setLoading(true);
    setInspectedDoc(null);

    try {
      if (caseId === 'master') {
        const mg = await getMasterGraph();
        setCurrentGraph(mg);
      } else {
        const g = await getGraph(caseId);
        setCurrentGraph(g);
      }
    } catch (err) {
      console.error('Failed to switch graph case:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNode = async (data) => {
    const docId = data?.document_id || data?.id;
    if (!docId || !docId.startsWith('DOC-')) return;

    try {
      const doc = await getDocument(docId);
      setInspectedDoc(doc);
    } catch (err) {
      console.error('Failed to load document details:', err);
      setInspectedDoc({
        document_id: docId,
        title: data?.title || data?.label || 'Institutional Document',
        department: data?.department || 'Academic Department',
        criterion: data?.criterion || 'Accreditation Metric',
        page: data?.page || 1,
        content: 'Record passage indexed in institutional accreditation repository.'
      });
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300">
      {/* Header & Case Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-[10px] font-mono font-bold uppercase tracking-[.18em] text-violet-400">
            <Network className="w-3.5 h-3.5" />
            Accreditation Topology
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--text-strong)] mt-1">
            Dynamic Accreditation Evidence Graph
          </h1>
          <p className="text-xs text-[var(--text-muted)] mt-1">
            Interactive multi-tier graph linking Institutional Criteria $\rightarrow$ Departments $\rightarrow$ Official Documents $\rightarrow$ Physical Page Citations.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="text-xs font-mono font-bold text-[var(--text-muted)] shrink-0">
            Select View:
          </span>
          <select
            value={selectedCaseId}
            onChange={(e) => handleSelectCase(e.target.value)}
            className="bg-[var(--surface)] border border-[var(--border)] text-xs text-[var(--text-strong)] font-mono rounded-xl px-3 py-2 focus:outline-none focus:border-violet-500 shadow-sm max-w-xs truncate"
          >
            <option value="master">
              🌐 Master Institutional Graph (All 7 Criteria)
            </option>
            {investigations.map((inv) => (
              <option key={inv.investigation_id} value={inv.investigation_id}>
                🔍 {inv.investigation_id}: {inv.question.substring(0, 36)}...
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Graph Canvas Container */}
      <div className="rounded-3xl border border-[var(--border)] overflow-hidden shadow-2xl relative bg-[var(--bg)]">
        {loading ? (
          <div className="h-[600px] flex items-center justify-center font-mono text-xs text-[var(--text-muted)] gap-3">
            <div className="w-5 h-5 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
            <span>Rendering Hierarchical Evidence Tree...</span>
          </div>
        ) : (
          <EvidenceGraph
            graph={currentGraph}
            onSelectNode={handleSelectNode}
          />
        )}
      </div>

      {/* Slide-over document viewer */}
      {inspectedDoc && (
        <EvidencePanel
          document={inspectedDoc}
          onClose={() => setInspectedDoc(null)}
        />
      )}
    </div>
  );
}
