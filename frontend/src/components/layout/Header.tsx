import { Radar } from 'lucide-react';

export function Header() {
  return (
    <header className="h-16 border-b border-gray-800 bg-gray-950 flex items-center px-6 text-gray-100">
      <div className="flex items-center gap-2">
        <Radar className="w-6 h-6 text-blue-500" />
        <h1 className="text-lg font-semibold">Radar Research Agent</h1>
      </div>
    </header>
  );
}
