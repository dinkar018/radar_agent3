'use client';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { CodeViewer } from '@/components/CodeViewer';
import { ExecutionLog } from '@/components/ExecutionLog';
import { ResultsViewer } from '@/components/ResultsViewer';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function ExperimentDetail() {
  const routeParams = useParams();
  const id = (routeParams?.id as string) || '';

  const { data: exp, refetch } = useQuery({ 
    queryKey: ['experiment', id], 
    queryFn: () => api.getExperiment(id),
    enabled: Boolean(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return (status === 'running' || status === 'pending') ? 2000 : false;
    }
  });

  const { messages, isConnected } = useWebSocket(id);

  if (!exp) return <div className="p-8">Loading...</div>;

  let resultFiles: string[] = [];
  if (exp.result_files) {
    try {
      const parsed = JSON.parse(exp.result_files);
      resultFiles = Array.isArray(parsed) ? parsed : [parsed];
    } catch {
      resultFiles = exp.result_files.split(',').map((s: string) => s.trim()).filter(Boolean);
    }
  }

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Experiment Details</h1>
          <p className="text-gray-400 mt-2">ID: {exp.id}</p>
        </div>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-2">
            WS: <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          </span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            exp.status === 'completed' ? 'bg-green-900/50 text-green-400' :
            exp.status === 'running' ? 'bg-blue-900/50 text-blue-400' :
            exp.status === 'failed' ? 'bg-red-900/50 text-red-400' :
            'bg-gray-800 text-gray-300'
          }`}>
            {exp.status.toUpperCase()}
          </span>
        </div>
      </div>

      {exp.generated_code && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Generated Code</h2>
          <CodeViewer code={exp.generated_code} />
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold mb-4">Live Execution Log</h2>
        <ExecutionLog messages={messages} />
      </div>

      {(resultFiles.length > 0 || exp.execution_output) && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Results</h2>
          <ResultsViewer resultFiles={resultFiles} executionOutput={exp.execution_output || ''} />
        </div>
      )}

      {exp.status !== 'running' && exp.status !== 'pending' && (
        <button 
          onClick={() => {
            api.rerunExperiment(exp.id).then(() => refetch());
          }}
          className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-md transition-colors"
        >
          Re-run Experiment
        </button>
      )}
    </div>
  );
}
