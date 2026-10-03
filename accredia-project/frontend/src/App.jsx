import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Investigate from './pages/Investigate';
import InvestigationDetail from './pages/InvestigationDetail';
import Evidence from './pages/Evidence';
import CriteriaCoverage from './pages/CriteriaCoverage';
import EvidenceGaps from './pages/EvidenceGaps';
import KnowledgeGraph from './pages/KnowledgeGraph';
import Audit from './pages/Audit';
import { healthCheck } from './services/api';

function AppLayout() {
  const location = useLocation();
  const [mode, setMode] = useState('Strict Citation Mode');
  const [theme, setTheme] = useState(() => localStorage.getItem('accredia-theme') || 'dark');

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('accredia-theme', theme);
  }, [theme]);

  useEffect(() => {
    healthCheck().then(data => data?.mode && setMode(data.mode)).catch(() => {});
  }, []);

  const getPageTitle = (pathname) => {
    if (pathname === '/') return { 
      title: 'Accreditation Command Center', 
      subtitle: 'Real-time evidence discovery and audit readiness for Vidyapath Institute of Technology (VITEC).' 
    };
    if (pathname === '/investigate') return { 
      title: 'Accreditation Evidence Assistant', 
      subtitle: 'Turn complex accreditation questions into page-verified evidence citations.' 
    };
    if (pathname.startsWith('/investigations/')) return { 
      title: 'Evidence Audit Dossier', 
      subtitle: 'Forensic audit and document verification details.' 
    };
    if (pathname === '/evidence') return { 
      title: 'Institutional Document Library', 
      subtitle: 'Searchable repository of 51 official college records, committee minutes, and audit reports.' 
    };
    if (pathname === '/coverage') return { 
      title: 'NAAC Criteria Compliance & Coverage', 
      subtitle: 'Evidence mapping and readiness progression across Criteria 1 through 7.' 
    };
    if (pathname === '/gaps') return { 
      title: 'Institutional Evidence Gaps', 
      subtitle: 'Deficiencies, missing records, and actionable remediation requirements.' 
    };
    if (pathname === '/graph') return { 
      title: 'Accreditation Knowledge Graph', 
      subtitle: 'Explore hierarchical relationships between Criteria, Departments, Documents, and Findings.' 
    };
    if (pathname === '/audit') return { 
      title: 'System Audit & Verification Trail', 
      subtitle: 'Trace every retrieval query, similarity score, and citation verification step.' 
    };
    return { 
      title: 'ACCREDIA', 
      subtitle: 'AI-Powered Accreditation Evidence Assistant' 
    };
  };

  const { title, subtitle } = getPageTitle(location.pathname);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--bg)] text-[var(--text)]">
      <Sidebar mode={mode} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header 
          title={title} 
          subtitle={subtitle} 
          mode={mode} 
          theme={theme} 
          onToggleTheme={() => setTheme(t => t === 'light' ? 'dark' : 'light')} 
        />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/investigate" element={<Investigate />} />
            <Route path="/investigations" element={<Dashboard />} />
            <Route path="/investigations/:id" element={<InvestigationDetail />} />
            <Route path="/evidence" element={<Evidence />} />
            <Route path="/coverage" element={<CriteriaCoverage />} />
            <Route path="/gaps" element={<EvidenceGaps />} />
            <Route path="/graph" element={<KnowledgeGraph />} />
            <Route path="/audit" element={<Audit />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
