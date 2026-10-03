import React, { useMemo } from 'react';
import { ReactFlow, Background, Controls, MiniMap, Handle, Position } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { 
  Network, 
  FileText, 
  ShieldCheck, 
  Tag, 
  Search, 
  Award, 
  Building, 
  BookOpen, 
  AlertTriangle,
  CheckCircle2,
  Sparkles
} from 'lucide-react';

const typeConfig = {
  criterion: {
    gradient: 'from-amber-500 via-orange-500 to-yellow-400',
    border: 'border-amber-400/60',
    glow: 'shadow-[0_0_25px_rgba(245,158,11,0.25)]',
    badge: 'bg-amber-500/20 text-amber-300 border-amber-400/40',
    tag: 'NAAC CRITERION',
    icon: Award
  },
  subcriterion: {
    gradient: 'from-blue-600 via-indigo-500 to-cyan-400',
    border: 'border-cyan-400/60',
    glow: 'shadow-[0_0_25px_rgba(6,182,212,0.25)]',
    badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-400/40',
    tag: 'KEY INDICATOR',
    icon: BookOpen
  },
  department: {
    gradient: 'from-teal-500 via-emerald-500 to-green-400',
    border: 'border-emerald-400/60',
    glow: 'shadow-[0_0_25px_rgba(16,185,129,0.25)]',
    badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-400/40',
    tag: 'DEPARTMENT',
    icon: Building
  },
  document: {
    gradient: 'from-violet-600 via-purple-500 to-pink-500',
    border: 'border-violet-400/60',
    glow: 'shadow-[0_0_25px_rgba(168,85,247,0.25)]',
    badge: 'bg-purple-500/20 text-purple-300 border-purple-400/40',
    tag: 'OFFICIAL RECORD',
    icon: FileText
  },
  page: {
    gradient: 'from-pink-500 via-rose-500 to-fuchsia-400',
    border: 'border-pink-400/60',
    glow: 'shadow-[0_0_25px_rgba(244,63,94,0.30)]',
    badge: 'bg-pink-500/20 text-pink-300 border-pink-400/40',
    tag: 'VERIFIED PAGE',
    icon: CheckCircle2
  },
  finding: {
    gradient: 'from-emerald-500 via-teal-400 to-cyan-400',
    border: 'border-emerald-300/80',
    glow: 'shadow-[0_0_30px_rgba(16,185,129,0.35)]',
    badge: 'bg-emerald-500/25 text-emerald-200 border-emerald-400/50',
    tag: 'GROUNDED FINDING',
    icon: ShieldCheck
  },
  root_cause: {
    gradient: 'from-emerald-500 via-teal-400 to-green-300',
    border: 'border-emerald-300/80',
    glow: 'shadow-[0_0_30px_rgba(16,185,129,0.35)]',
    badge: 'bg-emerald-500/25 text-emerald-200 border-emerald-400/50',
    tag: 'ACCREDITATION CONCLUSION',
    icon: ShieldCheck
  },
  contradiction: {
    gradient: 'from-rose-600 via-pink-600 to-amber-500',
    border: 'border-rose-400/70',
    glow: 'shadow-[0_0_25px_rgba(225,29,72,0.35)]',
    badge: 'bg-rose-500/20 text-rose-300 border-rose-400/40',
    tag: 'CONFLICT AUDITED',
    icon: AlertTriangle
  },
  question: {
    gradient: 'from-fuchsia-600 via-purple-600 to-violet-500',
    border: 'border-purple-400/60',
    glow: 'shadow-[0_0_25px_rgba(192,38,211,0.25)]',
    badge: 'bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-400/40',
    tag: 'AUDIT INQUIRY',
    icon: Search
  }
};

function CustomNodeShell({ data, type }) {
  const config = typeConfig[type] || typeConfig.document;
  const Icon = config.icon;

  return (
    <div
      className={`relative min-w-[200px] max-w-[270px] rounded-2xl border-2 ${config.border} bg-[var(--surface)] p-[1.5px] ${config.glow} transition-all duration-300 hover:scale-105 select-none`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-white !border-2 !border-purple-500 !w-2.5 !h-2.5 shadow-sm"
      />
      
      {/* Node Header Banner */}
      <div className={`rounded-t-[14px] bg-gradient-to-r ${config.gradient} px-3 py-1.5 flex items-center justify-between`}>
        <div className="flex items-center gap-1.5 text-white font-mono text-[9px] font-extrabold uppercase tracking-wider">
          <Icon className="w-3.5 h-3.5 shrink-0" />
          <span>{config.tag}</span>
        </div>
        {data.page && (
          <span className="text-[9px] font-mono font-black px-1.5 py-0.2 rounded bg-black/40 text-white">
            PG {data.page}
          </span>
        )}
      </div>

      {/* Node Body */}
      <div className="rounded-b-[14px] bg-[var(--surface)] p-3 backdrop-blur-xl">
        <div className="text-[12px] font-extrabold text-[var(--text-strong)] leading-snug line-clamp-2">
          {data.title || data.label || data.name || data.question}
        </div>
        
        {/* Metadata subline */}
        <div className="mt-2 flex items-center gap-1.5 flex-wrap text-[10px] font-mono">
          {data.department && (
            <span className="px-1.5 py-0.5 rounded bg-[var(--bg-deep)] text-[var(--text-muted)] border border-[var(--border)] font-semibold">
              {data.department}
            </span>
          )}
          {data.criterion && (
            <span className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 font-semibold">
              {data.criterion}
            </span>
          )}
          {data.date && (
            <span className="text-[var(--text-dim)]">
              {data.date}
            </span>
          )}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-white !border-2 !border-purple-500 !w-2.5 !h-2.5 shadow-sm"
      />
    </div>
  );
}

function QuestionNode({ data }) { return <CustomNodeShell data={data} type="question" />; }
function CriterionNode({ data }) { return <CustomNodeShell data={data} type="criterion" />; }
function SubcriterionNode({ data }) { return <CustomNodeShell data={data} type="subcriterion" />; }
function DepartmentNode({ data }) { return <CustomNodeShell data={data} type="department" />; }
function DocumentNode({ data }) { return <CustomNodeShell data={data} type="document" />; }
function PageNode({ data }) { return <CustomNodeShell data={data} type="page" />; }
function FindingNode({ data }) { return <CustomNodeShell data={data} type="finding" />; }
function ContradictionNode({ data }) { return <CustomNodeShell data={data} type="contradiction" />; }
function RootCauseNode({ data }) { return <CustomNodeShell data={data} type="root_cause" />; }

export default function EvidenceGraph({ graph, onSelectNode }) {
  const nodeTypes = useMemo(() => ({
    question: QuestionNode,
    criterion: CriterionNode,
    subcriterion: SubcriterionNode,
    department: DepartmentNode,
    document: DocumentNode,
    page: PageNode,
    finding: FindingNode,
    contradiction: ContradictionNode,
    root_cause: RootCauseNode
  }), []);

  if (!graph?.nodes?.length) {
    return (
      <div className="h-[580px] nexus-card rounded-3xl flex flex-col items-center justify-center text-[var(--text-dim)] p-8 text-center relative overflow-hidden border border-violet-500/20">
        <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-violet-500/20 to-pink-500/20 border border-violet-500/30 flex items-center justify-center mb-4 shadow-xl shadow-purple-500/10">
          <Network className="w-8 h-8 text-violet-400 animate-pulse" />
        </div>
        <h4 className="text-sm font-bold text-[var(--text-strong)] font-mono uppercase tracking-wider">
          Accreditation Evidence Tree
        </h4>
        <p className="text-xs text-[var(--text-muted)] mt-1.5 max-w-sm">
          Run an evidence search to generate a multi-tier connected graph mapping Criteria to Departments, Documents, and Physical Page Citations.
        </p>
      </div>
    );
  }

  // Hierarchical tier calculation for clean layered visual layout
  const tierMap = {
    criterion: 0,
    question: 0,
    subcriterion: 1,
    department: 1,
    document: 2,
    contradiction: 2,
    page: 3,
    finding: 3,
    root_cause: 3
  };

  // Group nodes by tier
  const tierCounts = { 0: 0, 1: 0, 2: 0, 3: 0 };
  const tierIndices = {};

  graph.nodes.forEach((node) => {
    const tier = tierMap[node.type] ?? 2;
    tierIndices[node.id] = tierCounts[tier];
    tierCounts[tier] += 1;
  });

  const rfNodes = graph.nodes.map((node) => {
    const tier = tierMap[node.type] ?? 2;
    const indexInTier = tierIndices[node.id] || 0;
    const totalInTier = tierCounts[tier] || 1;
    
    // Center horizontally per tier
    const xPos = 60 + indexInTier * 270;
    const yPos = 40 + tier * 180;

    return {
      id: node.id,
      type: node.type || 'document',
      position: node.position || { x: xPos, y: yPos },
      data: { ...node.data, label: node.label, document_id: node.id }
    };
  });

  const rfEdges = graph.edges.map((edge) => {
    const isContradiction = edge.relationship === 'contradicts';
    const isCitation = edge.relationship === 'cites' || edge.relationship === 'on_page';
    const isCriterion = edge.relationship === 'satisfies' || edge.relationship === 'classifies';

    return {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.relationship.replaceAll('_', ' ').toUpperCase(),
      animated: true,
      style: {
        stroke: isContradiction ? '#f43f5e' : (isCitation ? '#10b981' : (isCriterion ? '#f59e0b' : '#a78bfa')),
        strokeWidth: isCitation || isContradiction ? 2.8 : 2.0
      },
      labelStyle: { 
        fill: isContradiction ? '#f43f5e' : '#e2d9f3', 
        fontSize: 10, 
        fontFamily: 'monospace', 
        fontWeight: 'bold' 
      },
      labelBgStyle: { 
        fill: '#1a1424', 
        fillOpacity: 0.95, 
        stroke: '#4a3363', 
        strokeWidth: 1, 
        rx: 4, 
        ry: 4 
      }
    };
  });

  return (
    <div className="h-[600px] rounded-3xl overflow-hidden relative nexus-card border border-violet-500/30 shadow-2xl">
      {/* Top Banner Control Overlay */}
      <div className="absolute top-4 left-4 z-10 rounded-2xl border border-violet-400/30 bg-[var(--surface)]/90 backdrop-blur-xl px-4 py-2.5 flex items-center gap-3 shadow-xl">
        <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#10b981]" />
        <Network className="w-4 h-4 text-violet-400" />
        <div>
          <span className="text-[11px] font-black tracking-wider text-[var(--text-strong)] font-mono block">
            HIERARCHICAL ACCREDITATION EVIDENCE GRAPH
          </span>
          <span className="text-[9px] font-mono text-[var(--text-dim)]">
            {graph.nodes.length} Nodes · {graph.edges.length} Verified Directed Links
          </span>
        </div>
      </div>

      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelectNode?.(node.data)}
        fitView
        fitViewOptions={{ padding: 0.22 }}
        minZoom={0.25}
        maxZoom={1.8}
      >
        <Background gap={24} size={1.2} color="rgba(168, 85, 247, 0.15)" />
        <MiniMap
          pannable
          zoomable
          nodeStrokeWidth={3}
          nodeColor={(n) => {
            if (n.type === 'criterion') return '#f59e0b';
            if (n.type === 'subcriterion') return '#06b6d4';
            if (n.type === 'department') return '#10b981';
            if (n.type === 'page') return '#f43f5e';
            if (n.type === 'root_cause' || n.type === 'finding') return '#10b981';
            if (n.type === 'contradiction') return '#e11d48';
            return '#a855f7';
          }}
          className="!bg-[var(--surface)] !border-2 !border-[var(--border)] !rounded-2xl"
        />
        <Controls className="!bg-[var(--surface)] !border !border-[var(--border)] !rounded-2xl shadow-xl" />
      </ReactFlow>
    </div>
  );
}
