import React from 'react';
import { AlertCircle } from 'lucide-react';

export const DemoBanner: React.FC = () => {
  return (
    <div className="bg-amber-950/80 border-b border-amber-800/80 text-amber-200 px-4 py-2 text-xs flex items-center justify-between shadow-inner">
      <div className="flex items-center gap-2 max-w-5xl mx-auto text-center font-medium">
        <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
        <span>
          <strong>DEMO MODE</strong> — Values are synthetic demonstration data and are not official MOIL operational figures.
        </span>
      </div>
    </div>
  );
};
