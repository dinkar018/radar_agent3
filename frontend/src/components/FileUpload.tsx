'use client';
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  onUpload: (file: File) => void;
  accept?: Record<string, string[]>;
  label: string;
  isLoading?: boolean;
}

export function FileUpload({ onUpload, accept, label, isLoading }: Props) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } = useDropzone({ 
    onDrop, 
    accept,
    multiple: false
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
        isDragActive ? "border-blue-500 bg-blue-500/10" : "border-gray-700 hover:border-gray-500 hover:bg-gray-800/50",
        isLoading && "opacity-50 cursor-not-allowed"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-2">
        <UploadCloud className="w-10 h-10 text-gray-400" />
        <p className="text-gray-300 font-medium">{label}</p>
        <p className="text-sm text-gray-500">Drag & drop or click to select</p>
      </div>
      {acceptedFiles[0] && (
        <div className="mt-4 text-sm text-blue-400">
          Selected: {acceptedFiles[0].name}
        </div>
      )}
    </div>
  );
}
