'use client';
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function NewExperiment() {
  const router = useRouter();
  const [paperId, setPaperId] = useState('');
  const [selectedData, setSelectedData] = useState<string[]>([]);
  const [instructions, setInstructions] = useState('');

  const { data: docs } = useQuery({ queryKey: ['documents'], queryFn: () => api.listDocuments() });
  const { data: dataFiles } = useQuery({ queryKey: ['datafiles'], queryFn: () => api.listDataFiles() });

  const papers = docs?.filter((d) => d.doc_type === 'paper') || [];

  const createMutation = useMutation({
    mutationFn: () => api.createExperiment({ 
      paper_id: paperId, 
      data_file_ids: selectedData, 
      user_instructions: instructions 
    }),
    onSuccess: (data) => {
      router.push(`/experiments/${data.id}`);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!paperId || selectedData.length === 0) return alert('Select paper and data files');
    createMutation.mutate();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold tracking-tight">New Experiment</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6 bg-gray-900/50 p-6 rounded-xl border border-gray-800">
        <div>
          <label className="block mb-2 font-medium">1. Select Research Paper</label>
          <select 
            value={paperId} 
            onChange={e => setPaperId(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-md p-3"
            required
          >
            <option value="">-- Choose a paper --</option>
            {papers.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>

        <div>
          <label className="block mb-2 font-medium">2. Select Data Files</label>
          <div className="space-y-2 max-h-48 overflow-y-auto p-4 border border-gray-700 rounded-md bg-gray-800/50">
            {dataFiles?.map(f => (
              <label key={f.id} className="flex items-center gap-3">
                <input 
                  type="checkbox"
                  checked={selectedData.includes(f.id)}
                  onChange={(e) => {
                    if (e.target.checked) setSelectedData([...selectedData, f.id]);
                    else setSelectedData(selectedData.filter(id => id !== f.id));
                  }}
                  className="rounded border-gray-600 bg-gray-700"
                />
                <span>{f.name}</span>
              </label>
            ))}
            {!dataFiles?.length && <p className="text-gray-500 text-sm">No data files available.</p>}
          </div>
        </div>

        <div>
          <label className="block mb-2 font-medium">3. Optional Instructions</label>
          <textarea 
            value={instructions}
            onChange={e => setInstructions(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-md p-3 min-h-[100px]"
            placeholder="E.g., Focus on reproducing figure 3 using the alternative dataset..."
          />
        </div>

        <button 
          type="submit"
          disabled={createMutation.isPending || !paperId || selectedData.length === 0}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md font-medium transition-colors"
        >
          {createMutation.isPending ? 'Starting...' : 'Start Experiment'}
        </button>
      </form>
    </div>
  );
}
