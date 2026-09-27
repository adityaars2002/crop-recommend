import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Search, Sprout, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, PageHeader, Loader, ErrorMessage, EmptyState } from '../../components/ui';
import { getCrops, type CropListResponse } from '../../services/cropService';
import { parseApiError } from '../../services/api';
import type { Crop } from '../../types';

export default function CropsPage() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCrops = useCallback(async (p: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const response: CropListResponse = await getCrops(p, 12);
      setCrops(response.crops);
      setTotalCount(response.pagination.count);
      setHasNext(!!response.pagination.next);
      setHasPrev(!!response.pagination.previous);
    } catch (err) {
      const parsed = parseApiError(err);
      setError(parsed.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCrops(page);
  }, [page, fetchCrops]);

  const filteredCrops = search
    ? crops.filter((c) =>
        c.name.toLowerCase().includes(search.toLowerCase())
      )
    : crops;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
      <PageHeader
        title="Crop Directory"
        description={`Browse all ${totalCount} supported crops in our recommendation system.`}
      />

      {/* Search */}
      <div className="relative mb-6 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-stone-400" aria-hidden="true" />
        <input
          type="search"
          placeholder="Search crops..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-stone-300 bg-white pl-10 pr-4 py-2.5 text-sm text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500"
          aria-label="Search crops"
        />
      </div>

      {/* States */}
      {isLoading && <Loader message="Loading crops..." />}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={() => fetchCrops(page)}
        />
      )}

      {!isLoading && !error && filteredCrops.length === 0 && (
        <EmptyState
          title="No Crops Found"
          message={search ? `No crops matching "${search}".` : 'No crops available yet.'}
        />
      )}

      {/* Grid */}
      {!isLoading && !error && filteredCrops.length > 0 && (
        <>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
            {filteredCrops.map((crop) => (
              <Link key={crop.id} to={`/crops/${crop.id}`}>
                <Card hover className="h-full">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 mb-3">
                    <Sprout className="h-5 w-5" />
                  </div>
                  <h3 className="text-sm font-semibold text-stone-900 capitalize mb-1">
                    {crop.name}
                  </h3>
                  {crop.scientific_name && (
                    <p className="text-xs text-stone-400 italic mb-2">{crop.scientific_name}</p>
                  )}
                  {crop.description && (
                    <p className="text-xs text-stone-500 line-clamp-2">{crop.description}</p>
                  )}
                  <span className="mt-3 inline-block text-xs font-medium text-emerald-600">
                    View Details →
                  </span>
                </Card>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {(hasPrev || hasNext) && (
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={!hasPrev}
                className="inline-flex items-center gap-1 px-3 py-2 text-sm font-medium text-stone-600 rounded-lg border border-stone-300 hover:bg-stone-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                aria-label="Previous page"
              >
                <ChevronLeft className="h-4 w-4" /> Previous
              </button>
              <span className="text-sm text-stone-500">Page {page}</span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!hasNext}
                className="inline-flex items-center gap-1 px-3 py-2 text-sm font-medium text-stone-600 rounded-lg border border-stone-300 hover:bg-stone-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                aria-label="Next page"
              >
                Next <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
