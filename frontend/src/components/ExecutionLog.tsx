'use client';
import { useEffect, useRef } from 'react';
import { WSMessage } from '../types';
import { cn } from '@/lib/utils';

interface Props {
  messages: WSMessage[];
}

export function ExecutionLog({ messages }: Props) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div 
      ref={scrollRef}
      className="h-64 bg-black border border-gray-800 rounded-md p-4 overflow-y-auto font-mono text-sm space-y-2"
    >
      {messages.length === 0 ? (
        <div className="text-gray-500 italic">Waiting for logs...</div>
      ) : (
        messages.map((msg, i) => (
          <div key={i} className="flex gap-3">
            <span className="text-gray-600">
              [{new Date().toLocaleTimeString()}]
            </span>
            <span className={cn(
              "font-semibold",
              msg.status === 'error' ? 'text-red-500' :
              msg.status === 'complete' ? 'text-green-500' :
              'text-blue-500'
            )}>
              [{msg.status.toUpperCase()}]
            </span>
            <span className="text-gray-300">{msg.message}</span>
          </div>
        ))
      )}
    </div>
  );
}
