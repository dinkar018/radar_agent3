'use client';
import { useState, useEffect, Suspense } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { FileUpload } from '@/components/FileUpload';
import { Upload, FileText, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';
import { formatFileSize } from '@/lib/utils';

function NewExperimentContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  const [paperId, setPaperId] = useState('');
  const [selectedData, setSelectedData] = useState<string[]>([]);
  const [instructions, setInstructions] = useState('');

  // Toggles for inline uploaders
  const [showDataUpload, setShowDataUpload] = useState(false);
  const [showPaperUpload, setShowPaperUpload] = useState(false);
  const [dataUploadSuccess, setDataUploadSuccess] = useState('');
  const [paperUploadSuccess, setPaperUploadSuccess] = useState('');

  const { data: docs } = useQuery({ queryKey: ['documents'], queryFn: () => api.listDocuments() });
  const { data: dataFiles } = useQuery({ queryKey: ['datafiles'], queryFn: () => api.listDataFiles() });

  const papers = docs?.filter((d) => d.doc_type === 'paper' || d.doc_type === 'journal') || [];

  // Check if URL has ?data=<id>
  useEffect(() => {
    const preselectedDataId = searchParams.get('data');
    if (preselectedDataId && !selectedData.includes(preselectedDataId)) {
      setSelectedData([preselectedDataId]);
    }
  }, [searchParams]);

  // Upload radar data inline
  const uploadDataMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', 'User uploaded radar data for experiment');
      return api.uploadDataFile(formData);
    },
    onSuccess: (newFile) => {
      queryClient.invalidateQueries({ queryKey: ['datafiles'] });
      setSelectedData((prev) => [...prev, newFile.id]);
      setDataUploadSuccess(`Uploaded and selected ${newFile.name}!`);
      setShowDataUpload(false);
      setTimeout(() => setDataUploadSuccess(''), 4000);
    },
  });

  // Upload research paper inline
  const uploadPaperMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', 'paper');
      return api.uploadDocument(formData);
    },
    onSuccess: (newDoc) => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setPaperId(newDoc.id);
      setPaperUploadSuccess(`Uploaded and selected ${newDoc.name}!`);
      setShowPaperUpload(false);
      setTimeout(() => setPaperUploadSuccess(''), 4000);
    },
  });

  const createMutation = useMutation({
    mutationFn: () =>
      api.createExperiment({
        paper_id: paperId,
        data_file_ids: selectedData,
        user_instructions: instructions,
      }),
    onSuccess: (data) => {
      router.push(`/experiments/${data.id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!paperId || selectedData.length === 0) {
      return alert('Please select at least one research paper and one radar data file.');
    }
    createMutation.mutate();
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Configure New Experiment</h1>
        <p className="text-gray-400 mt-1">
          Select a research paper, choose or upload radar captured data, and let the agent implement the algorithm.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 bg-gray-900/50 p-6 rounded-xl border border-gray-800">
        {/* Step 1: Paper Selection / Upload */}
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <label className="font-semibold text-gray-200">1. Select or Upload Research Paper</label>
            <button
              type="button"
              onClick={() => setShowPaperUpload(!showPaperUpload)}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              {showPaperUpload ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              {showPaperUpload ? 'Hide Paper Uploader' : '+ Upload New Paper (PDF)'}
            </button>
          </div>

          {showPaperUpload && (
            <div className="p-4 border border-dashed border-gray-700 rounded-lg bg-gray-800/40 space-y-2">
              <p className="text-xs text-gray-400">
                Upload a research paper or journal PDF. It will be parsed and indexed for the agent.
              </p>
              <FileUpload
                label="Drop research paper PDF"
                accept={{ 'application/pdf': ['.pdf'], 'text/plain': ['.txt', '.md'] }}
                onUpload={(file) => uploadPaperMutation.mutate(file)}
                isLoading={uploadPaperMutation.isPending}
              />
            </div>
          )}

          {paperUploadSuccess && (
            <div className="flex items-center gap-2 text-green-400 text-xs bg-green-950/40 border border-green-800/50 p-2.5 rounded-md">
              <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
              <span>{paperUploadSuccess}</span>
            </div>
          )}

          <select
            value={paperId}
            onChange={(e) => setPaperId(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-md p-3 text-sm text-gray-100"
            required
          >
            <option value="">-- Choose an existing paper from Knowledge Base --</option>
            {papers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.chunk_count} chunks indexed)
              </option>
            ))}
          </select>
        </div>

        {/* Step 2: Radar Data Selection / Upload */}
        <div className="space-y-3 pt-2">
          <div className="flex justify-between items-center">
            <label className="font-semibold text-gray-200">2. Select Radar Captured Data</label>
            <button
              type="button"
              onClick={() => setShowDataUpload(!showDataUpload)}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
            >
              {showDataUpload ? <ChevronUp className="w-3.5 h-3.5" /> : <Upload className="w-3.5 h-3.5" />}
              {showDataUpload ? 'Hide Data Uploader' : '+ Upload Your Own Radar Data (.npy)'}
            </button>
          </div>

          {showDataUpload && (
            <div className="p-4 border border-dashed border-cyan-800/60 rounded-lg bg-cyan-950/20 space-y-2">
              <p className="text-xs text-cyan-300">
                Upload your captured radar data. NumPy arrays (.npy) with ADC fast-time chirps are automatically analyzed for shape.
              </p>
              <FileUpload
                label="Drop .npy, .bin, .mat, or .csv radar data file"
                accept={{
                  'application/x-numpy': ['.npy'],
                  'application/octet-stream': ['.bin', '.dat', '.raw'],
                  'text/csv': ['.csv'],
                  'application/x-matlab': ['.mat'],
                }}
                onUpload={(file) => uploadDataMutation.mutate(file)}
                isLoading={uploadDataMutation.isPending}
              />
            </div>
          )}

          {dataUploadSuccess && (
            <div className="flex items-center gap-2 text-green-400 text-xs bg-green-950/40 border border-green-800/50 p-2.5 rounded-md">
              <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
              <span>{dataUploadSuccess}</span>
            </div>
          )}

          <div className="space-y-2 max-h-56 overflow-y-auto p-3 border border-gray-700 rounded-md bg-gray-800/50">
            {dataFiles?.map((f) => (
              <label
                key={f.id}
                className="flex items-start gap-3 p-2 rounded hover:bg-gray-700/40 transition-colors cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedData.includes(f.id)}
                  onChange={(e) => {
                    if (e.target.checked) setSelectedData([...selectedData, f.id]);
                    else setSelectedData(selectedData.filter((id) => id !== f.id));
                  }}
                  className="rounded border-gray-600 bg-gray-700 mt-1"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-medium text-gray-200">{f.name}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.2 rounded font-medium ${
                        f.name.includes('sar_data')
                          ? 'bg-purple-900/40 text-purple-300'
                          : 'bg-emerald-900/40 text-emerald-300'
                      }`}
                    >
                      {f.name.includes('sar_data') ? 'Synthetic' : 'User Captured'}
                    </span>
                    {f.shape && (
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-gray-800 text-cyan-300 font-mono">
                        ({f.shape.join(', ')})
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5 flex gap-3">
                    <span>Size: {formatFileSize(f.file_size)}</span>
                    {f.description && <span className="text-gray-500 italic truncate">{f.description}</span>}
                  </div>
                </div>
              </label>
            ))}
            {!dataFiles?.length && (
              <p className="text-gray-500 text-sm py-2 text-center">
                No radar data files available yet. Click above to upload your data!
              </p>
            )}
          </div>
        </div>

        {/* Step 3: Instructions */}
        <div className="space-y-2 pt-2">
          <label className="block font-semibold text-gray-200">3. Optional Instructions for Agent</label>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-md p-3 min-h-[90px] text-sm text-gray-100 placeholder-gray-500"
            placeholder="e.g., Focus on 2D Range Migration Algorithm, apply Hann window before range FFT, and generate a 2D intensity reflectivity plot in dB."
          />
        </div>

        <button
          type="submit"
          disabled={createMutation.isPending || !paperId || selectedData.length === 0}
          className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md font-medium transition-colors text-white shadow-lg"
        >
          {createMutation.isPending ? 'Starting LangGraph Agent...' : 'Start Experiment with Selected Data'}
        </button>
      </form>
    </div>
  );
}

export default function NewExperiment() {
  return (
    <Suspense fallback={<div className="p-8 text-gray-400">Loading...</div>}>
      <NewExperimentContent />
    </Suspense>
  );
}
