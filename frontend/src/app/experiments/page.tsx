'use client';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { ExperimentCard } from '@/components/ExperimentCard';
import Link from 'next/link';
import { Plus } from 'lucide-react';

export default function Experiments() {
  const { data: exps, isLoading } = useQuery({ queryKey: ['experiments'], queryFn: () => api.listExperiments() });

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Experiments</h1>
        <Link 
          href="/experiments/new"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Experiment
        </Link>
      </div>

      {isLoading ? (
        <div className="text-gray-500">Loading...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {exps?.map(exp => (
            <ExperimentCard key={exp.id} experiment={exp} />
          ))}
          {!exps?.length && <p className="text-gray-500">No experiments found.</p>}
        </div>
      )}
    </div>
  );
}
