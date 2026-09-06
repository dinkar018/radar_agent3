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
        <div className="p-6 rounded-xl border border-gray-800 bg-gray-900/50">
          <h3 className="text-gray-400 font-medium">KB Documents</h3>
          <p className="text-3xl font-bold mt-2">{docs?.length || 0}</p>
        </div>
        <div className="p-6 rounded-xl border border-gray-800 bg-gray-900/50">
          <h3 className="text-gray-400 font-medium">Experiments</h3>
          <p className="text-3xl font-bold mt-2">{exps?.length || 0}</p>
        </div>
        <div className="p-6 rounded-xl border border-gray-800 bg-gray-900/50">
          <h3 className="text-gray-400 font-medium">Data Files</h3>
          <p className="text-3xl font-bold mt-2">{dataFiles?.length || 0}</p>
        </div>
      </div>

      <div className="flex gap-4">
        <Link href="/knowledge-base" className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-md transition-colors">
          View KB
        </Link>
        <Link href="/experiments/new" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors">
          New Experiment
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
