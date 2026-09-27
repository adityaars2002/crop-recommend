import { Loader2 } from 'lucide-react';

interface LoaderProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: 'h-5 w-5',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
};

export default function Loader({ message, size = 'md' }: LoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12" role="status">
      <Loader2 className={`${sizeMap[size]} animate-spin text-emerald-600`} aria-hidden="true" />
      {message && <p className="text-sm text-stone-500 animate-pulse">{message}</p>}
      <span className="sr-only">Loading</span>
    </div>
  );
}
