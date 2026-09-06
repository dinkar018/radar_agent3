import Link from 'next/link';
import { Experiment } from '../types';
import { formatDate, cn } from '@/lib/utils';

export function ExperimentCard({ experiment }: { experiment: Experiment }) {
  const statusColors = {
    pending: 'bg-gray-800 text-gray-300',
    running: 'bg-blue-900/50 text-blue-400',
    completed: 'bg-green-900/50 text-green-400',
    failed: 'bg-red-900/50 text-red-400'
  };

  return (
    <Link 
      href={`/experiments/${experiment.id}`}
      className="block p-5 rounded-lg border border-gray-800 bg-gray-900 hover:border-gray-600 transition-colors"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-medium text-gray-100">
            Experiment {experiment.id.substring(0, 8)}
          </h3>
          <p className="text-sm text-gray-400 mt-1">
            Paper ID: {experiment.paper_id}
          </p>
        </div>
        <span className={cn("px-2.5 py-1 rounded-full text-xs font-medium", statusColors[experiment.status])}>
          {experiment.status}
        </span>
      </div>
      
      <div className="flex justify-between text-xs text-gray-500">
        <span>Created: {formatDate(experiment.created_at)}</span>
        <span>Iterations: {experiment.iteration_count}</span>
      </div>
    </Link>
  );
}
