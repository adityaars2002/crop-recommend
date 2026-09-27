import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: React.ReactNode;
}

export default function EmptyState({ title, message, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 px-4 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-stone-100">
        {icon || <Inbox className="h-7 w-7 text-stone-400" aria-hidden="true" />}
      </div>
      <div className="space-y-1">
        <h3 className="text-lg font-semibold text-stone-700">{title}</h3>
        <p className="text-sm text-stone-400 max-w-sm">{message}</p>
      </div>
    </div>
  );
}
