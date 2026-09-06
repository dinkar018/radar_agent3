'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { FileUpload } from '@/components/FileUpload';
import { KnowledgeBaseCard } from '@/components/KnowledgeBaseCard';

export default function KnowledgeBase() {
  const queryClient = useQueryClient();
  const [docType, setDocType] = useState('paper');
  const [search, setSearch] = useState('');

  const { data: docs } = useQuery({ queryKey: ['documents'], queryFn: () => api.listDocuments() });

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', docType);
      return api.uploadDocument(formData);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] })
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] })
  });

  const filteredDocs = docs?.filter(d => d.name.toLowerCase().includes(search.toLowerCase())) || [];

  return (
    <div className="max-w-5xl space-y-8">
      <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-4">
          <div className="p-4 border border-gray-800 rounded-lg bg-gray-900/50">
            <h2 className="font-semibold mb-4">Upload Document</h2>
            <select 
              value={docType}
              onChange={e => setDocType(e.target.value)}
              className="w-full mb-4 bg-gray-800 border border-gray-700 rounded-md p-2 text-sm"
            >
              <option value="paper">Research Paper</option>
              <option value="datasheet">Datasheet</option>
              <option value="setup">Setup Guide</option>
              <option value="config">Configuration</option>
            </select>
            <FileUpload 
              label="Upload PDF or TXT"
              accept={{ 'application/pdf': ['.pdf'], 'text/plain': ['.txt', '.md'] }}
              onUpload={(file) => uploadMutation.mutate(file)}
              isLoading={uploadMutation.isPending}
            />
          </div>
        </div>

        <div className="md:col-span-2 space-y-4">
          <input 
            type="text" 
            placeholder="Search documents..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-gray-900 border border-gray-800 rounded-md px-4 py-2"
          />
          
          <div className="space-y-3">
            {filteredDocs.map(doc => (
              <KnowledgeBaseCard 
                key={doc.id} 
                document={doc} 
                onDelete={() => deleteMutation.mutate(doc.id)} 
              />
            ))}
            {filteredDocs.length === 0 && (
              <p className="text-gray-500 text-center py-8">No documents found.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
