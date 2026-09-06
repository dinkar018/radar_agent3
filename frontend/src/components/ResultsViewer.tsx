'use client';

interface Props {
  resultFiles: string[];
  executionOutput: string;
}

export function ResultsViewer({ resultFiles, executionOutput }: Props) {
  const images = resultFiles.filter(f => f.endsWith('.png') || f.endsWith('.jpg'));

  return (
    <div className="space-y-6">
      {images.length > 0 && (
        <div>
          <h3 className="text-lg font-medium mb-3">Generated Images</h3>
          <div className="grid grid-cols-2 gap-4">
            {images.map((img, i) => (
              <div key={i} className="rounded-lg overflow-hidden border border-gray-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={`http://localhost:8000/api/results/${img}`} 
                  alt={`Result ${i}`}
                  className="w-full h-auto cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => window.open(`http://localhost:8000/api/results/${img}`, '_blank')}
                />
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div>
        <h3 className="text-lg font-medium mb-3">Execution Output</h3>
        <pre className="p-4 rounded-md bg-gray-900 border border-gray-800 text-gray-300 overflow-x-auto whitespace-pre-wrap text-sm font-mono">
          {executionOutput || 'No output.'}
        </pre>
      </div>
    </div>
  );
}
