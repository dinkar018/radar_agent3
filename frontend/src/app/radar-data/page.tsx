'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { FileUpload } from '@/components/FileUpload';
import { Radio, Trash2, Database, Play, CheckCircle } from 'lucide-react';
import { formatFileSize, formatDate } from '@/lib/utils';
import Link from 'next/link';

export default function RadarDataPage() {
  const queryClient = useQueryClient();
  const [description, setDescription] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const { data: dataFiles, isLoading } = useQuery({
    queryKey: ['datafiles'],
    queryFn: () => api.listDataFiles(),
  });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      if (description) {
        formData.append('description', description);
      }
      return api.uploadDataFile(formData);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['datafiles'] });
      setDescription('');
      setUploadSuccess(`Successfully uploaded ${data.name}!`);
      setTimeout(() => setUploadSuccess(''), 4000);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteDataFile(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datafiles'] });
    },
  });

  return (
    <div className="max-w-6xl space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Radio className="w-8 h-8 text-blue-500" />
            Radar Captured Data
          </h1>
          <p className="text-gray-400 mt-1">
            Manage your pre-given synthetic datasets and upload your own radar captured data (.npy, .bin, .mat, .csv).
          </p>
        </div>
        <Link
          href="/experiments/new"
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md transition-colors text-sm font-medium"
        >
          <Play className="w-4 h-4" />
          Run Experiment with Data
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Section */}
        <div className="lg:col-span-1 space-y-4">
          <div className="p-6 border border-gray-800 rounded-xl bg-gray-900/50 space-y-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-400" />
              Upload Radar Data
            </h2>
            <p className="text-sm text-gray-400">
              Upload captured raw ADC chirps or synthetic SAR data. Supported formats include NumPy (.npy), binary (.bin), MATLAB (.mat), or CSV.
            </p>

            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1">
                Dataset Description (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Lab scan with 3 metallic cylinders"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-md p-2.5 text-sm mb-4 text-gray-100 placeholder-gray-500"
              />
            </div>

            <FileUpload
              label="Drop .npy, .bin, or .mat data"
              accept={{
                'application/x-numpy': ['.npy'],
                'application/octet-stream': ['.bin', '.dat', '.raw'],
                'text/csv': ['.csv'],
                'application/x-matlab': ['.mat'],
              }}
              onUpload={(file) => uploadMutation.mutate(file)}
              isLoading={uploadMutation.isPending}
            />

            {uploadSuccess && (
              <div className="flex items-center gap-2 text-green-400 text-sm bg-green-950/40 border border-green-800/60 p-3 rounded-md">
                <CheckCircle className="w-4 h-4 shrink-0" />
                <span>{uploadSuccess}</span>
              </div>
            )}
          </div>

          <div className="p-4 border border-blue-900/40 rounded-xl bg-blue-950/20 text-xs text-blue-300 space-y-2">
            <div className="font-semibold text-blue-200">Radar Data Contract</div>
            <p>
              For TI IWR1843BOOST SAR, NumPy arrays typically have shape <code className="bg-blue-900/50 px-1 py-0.5 rounded">(range_bins, cross_range, 256)</code> representing 256 ADC samples per chirp across cross-range scan positions.
            </p>
          </div>
        </div>

        {/* Datasets List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold">Available Datasets ({dataFiles?.length || 0})</h2>

          {isLoading ? (
            <div className="text-gray-500 py-8 text-center">Loading datasets...</div>
          ) : !dataFiles?.length ? (
            <div className="p-8 border border-gray-800 rounded-xl bg-gray-900/30 text-center text-gray-500">
              No radar datasets found. Upload your first data file using the form.
            </div>
          ) : (
            <div className="space-y-3">
              {dataFiles.map((file) => (
                <div
                  key={file.id}
                  className="p-5 border border-gray-800 rounded-xl bg-gray-900/50 hover:border-gray-700 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-semibold text-gray-100">{file.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        file.name.includes('sar_data')
                          ? 'bg-purple-900/40 text-purple-300 border border-purple-800/50'
                          : 'bg-emerald-900/40 text-emerald-300 border border-emerald-800/50'
                      }`}>
                        {file.name.includes('sar_data') ? 'Pre-given Synthetic' : 'User Uploaded'}
                      </span>
                      {file.shape && (
                        <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-cyan-300 font-mono">
                          Shape: ({file.shape.join(', ')})
                        </span>
                      )}
                      {file.dtype && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-400 font-mono">
                          {file.dtype}
                        </span>
                      )}
                    </div>
                    {file.description && (
                      <p className="text-sm text-gray-400">{file.description}</p>
                    )}
                    <div className="flex items-center gap-4 text-xs text-gray-500 pt-1">
                      <span>Size: {formatFileSize(file.file_size)}</span>
                      {file.upload_date && <span>Added: {formatDate(file.upload_date)}</span>}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end md:self-auto">
                    <Link
                      href={`/experiments/new?data=${file.id}`}
                      className="text-xs bg-gray-800 hover:bg-gray-700 text-gray-200 px-3 py-1.5 rounded transition-colors"
                    >
                      Use in Experiment
                    </Link>
                    <button
                      onClick={() => {
                        if (confirm(`Delete ${file.name}?`)) {
                          deleteMutation.mutate(file.id);
                        }
                      }}
                      className="text-gray-500 hover:text-red-400 p-1.5 rounded transition-colors"
                      title="Delete dataset"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
