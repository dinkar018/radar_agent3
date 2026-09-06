'use client';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { ExperimentCard } from '@/components/ExperimentCard';
import Link from 'next/link';

export default function Dashboard() {
  const { data: docs } = useQuery({ queryKey: ['documents'], queryFn: () => api.listDocuments() });
  const { data: exps } = useQuery({ queryKey: ['experiments'], queryFn: () => api.listExperiments() });
  const { data: dataFiles } = useQuery({ queryKey: ['datafiles'], queryFn: () => api.listDataFiles() });

  return (
    <div className="space-y-8 max-w-5xl">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/knowledge-base" className="p-6 rounded-xl border border-gray-800 bg-gray-900/50 hover:border-gray-700 transition-colors block">
          <h3 className="text-gray-400 font-medium">KB Documents</h3>
          <p className="text-3xl font-bold mt-2 text-gray-100">{docs?.length || 0}</p>
          <span className="text-xs text-blue-400 mt-2 block">View knowledge base →</span>
        </Link>
        <Link href="/radar-data" className="p-6 rounded-xl border border-gray-800 bg-gray-900/50 hover:border-gray-700 transition-colors block">
          <h3 className="text-gray-400 font-medium">Radar Data Files</h3>
          <p className="text-3xl font-bold mt-2 text-cyan-400">{dataFiles?.length || 0}</p>
          <span className="text-xs text-cyan-400 mt-2 block">Manage & upload datasets →</span>
        </Link>
        <Link href="/experiments" className="p-6 rounded-xl border border-gray-800 bg-gray-900/50 hover:border-gray-700 transition-colors block">
          <h3 className="text-gray-400 font-medium">Experiments Run</h3>
          <p className="text-3xl font-bold mt-2 text-emerald-400">{exps?.length || 0}</p>
          <span className="text-xs text-emerald-400 mt-2 block">View execution history →</span>
        </Link>
      </div>

      <div className="flex gap-4 flex-wrap">
        <Link href="/experiments/new" className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors text-sm shadow">
          + New Experiment
        </Link>
        <Link href="/radar-data" className="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-200 font-medium rounded-md transition-colors text-sm border border-gray-700">
          Upload Radar Data
        </Link>
        <Link href="/knowledge-base" className="px-5 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-200 font-medium rounded-md transition-colors text-sm border border-gray-700">
          Knowledge Base
        </Link>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Experiments</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {exps?.slice(0, 5).map(exp => (
            <ExperimentCard key={exp.id} experiment={exp} />
          ))}
          {!exps?.length && <p className="text-gray-500">No experiments found.</p>}
        </div>
      </div>
    </div>
  );
}
