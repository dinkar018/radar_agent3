import { Trash2 } from 'lucide-react';
import { Document } from '../types';
import { formatFileSize, formatDate } from '@/lib/utils';

interface Props {
  document: Document;
  onDelete: () => void;
}

export function KnowledgeBaseCard({ document, onDelete }: Props) {
  return (
    <div className="p-4 rounded-lg border border-gray-800 bg-gray-900 flex items-center justify-between group">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h3 className="font-medium text-gray-100">{document.name}</h3>
          <span className="px-2 py-0.5 rounded text-xs bg-gray-800 text-gray-300">
            {document.doc_type}
          </span>
        </div>
        <div className="text-sm text-gray-500 flex gap-4">
          <span>{formatFileSize(document.file_size)}</span>
          <span>{document.chunk_count} chunks</span>
          <span>{formatDate(document.upload_date)}</span>
        </div>
      </div>
      
      <button 
        onClick={() => {
          if (confirm('Are you sure you want to delete this document?')) {
            onDelete();
          }
        }}
        className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-950/30 rounded opacity-0 group-hover:opacity-100 transition-all"
      >
        <Trash2 className="w-5 h-5" />
      </button>
    </div>
  );
}
