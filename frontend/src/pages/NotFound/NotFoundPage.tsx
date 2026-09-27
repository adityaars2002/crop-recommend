import { Link } from 'react-router-dom';
import { Home, MapPin } from 'lucide-react';
import { Button } from '../../components/ui';

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center motion-safe:animate-[fadeIn_0.3s_ease-out]">
      <div className="flex h-20 w-20 items-center justify-center rounded-full bg-stone-100 mb-6">
        <MapPin className="h-10 w-10 text-stone-400" />
      </div>
      <h1 className="text-5xl font-bold text-stone-900 mb-2">404</h1>
      <p className="text-lg text-stone-500 mb-8 max-w-md">
        This page doesn't exist. It might have been moved or the URL is incorrect.
      </p>
      <Link to="/">
        <Button size="lg" className="gap-2">
          <Home className="h-4 w-4" />
          Back to Home
        </Button>
      </Link>
    </div>
  );
}
