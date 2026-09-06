'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Database, FlaskConical, Plus, Radio } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Dashboard', icon: Home },
    { href: '/knowledge-base', label: 'Knowledge Base', icon: Database },
    { href: '/radar-data', label: 'Radar Data', icon: Radio },
    { href: '/experiments', label: 'Experiments', icon: FlaskConical },
    { href: '/experiments/new', label: 'New Experiment', icon: Plus },
  ];

  return (
    <div className="h-screen w-64 bg-gray-950 border-r border-gray-800 flex flex-col text-gray-100">
      <div className="p-6">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <FlaskConical className="w-6 h-6" />
          Radar Agent
        </h2>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                isActive ? "bg-gray-800 text-white" : "hover:bg-gray-800/50 text-gray-400 hover:text-gray-100"
              )}
            >
              <Icon className="w-5 h-5" />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
