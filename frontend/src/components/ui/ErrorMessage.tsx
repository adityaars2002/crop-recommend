import { AlertCircle, WifiOff, ServerCrash } from 'lucide-react';
import Button from './Button';

interface ErrorMessageProps {
  title?: string;
  message: string;
  code?: string;
  onRetry?: () => void;
}

export default function ErrorMessage({ title, message, code, onRetry }: ErrorMessageProps) {
  const isNetwork = code === 'NETWORK_ERROR';
  const isServer = code?.startsWith('HTTP_5') || code === 'INTERNAL_SERVER_ERROR';

  const Icon = isNetwork ? WifiOff : isServer ? ServerCrash : AlertCircle;

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12 px-4 text-center" role="alert">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50">
        <Icon className="h-7 w-7 text-red-500" aria-hidden="true" />
      </div>
      <div className="space-y-1">
        <h3 className="text-lg font-semibold text-stone-800">
          {title || (isNetwork ? 'Connection Error' : 'Something Went Wrong')}
        </h3>
        <p className="text-sm text-stone-500 max-w-md">{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}
