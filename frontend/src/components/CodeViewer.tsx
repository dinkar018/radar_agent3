'use client';
import { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Check, Copy } from 'lucide-react';

interface Props {
  code: string;
  language?: string;
}

export function CodeViewer({ code, language = 'python' }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative rounded-md overflow-hidden border border-gray-800">
      <div className="absolute right-4 top-4">
        <button 
          onClick={handleCopy}
          className="p-2 rounded-md bg-gray-800 hover:bg-gray-700 text-gray-300 transition-colors"
        >
          {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
        </button>
      </div>
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        customStyle={{ margin: 0, padding: '1.5rem', background: '#09090b' }}
        showLineNumbers
      >
        {code || ''}
      </SyntaxHighlighter>
    </div>
  );
}
