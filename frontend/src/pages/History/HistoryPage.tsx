import { useState, useEffect, useCallback } from 'react';
import { Clock, ChevronLeft, ChevronRight, Sprout } from 'lucide-react';
import { Card, PageHeader, Loader, ErrorMessage, EmptyState, Badge } from '../../components/ui';
import { getRecommendationHistory, type HistoryListResponse } from '../../services/cropService';
import { parseApiError } from '../../services/api';
import type { RecommendationHistoryItem } from '../../types';

export default function HistoryPage() {
  const [items, setItems] = useState<RecommendationHistoryItem[]>([]);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrev, setHasPrev] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async (p: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const response: HistoryListResponse = await getRecommendationHistory(p, 10);
      setItems(response.items);
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
    fetchHistory(page);
  }, [page, fetchHistory]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
      <PageHeader
        title="Recommendation History"
        description={`${totalCount} past crop recommendation${totalCount !== 1 ? 's' : ''} recorded.`}
      />

      {isLoading && <Loader message="Loading history..." />}

      {error && (
        <ErrorMessage message={error} onRetry={() => fetchHistory(page)} />
      )}

      {!isLoading && !error && items.length === 0 && (
        <EmptyState
          title="No History Yet"
          message="Crop recommendations you make will appear here."
          icon={<Clock className="h-7 w-7 text-stone-400" />}
        />
      )}

      {!isLoading && !error && items.length > 0 && (
        <>
          <div className="space-y-4 mb-8">
            {items.map((item) => {
              const topRec = item.recommendations[0];
              return (
                <Card key={item.id} hover>
                  <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                    {/* Top recommendation */}
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 shrink-0">
                        <Sprout className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-sm font-semibold text-stone-900 capitalize">
                            {topRec?.crop?.name || 'Unknown'}
                          </h3>
                          <Badge variant="success" size="sm">
                            #{topRec?.rank || 1} Pick
                          </Badge>
                          <span className="text-xs font-semibold text-stone-600 tabular-nums">
                            {topRec ? `${(topRec.score * 100).toFixed(1)}%` : ''}
                          </span>
                        </div>
                        <p className="text-xs text-stone-400 mt-0.5">
                          N:{item.input.nitrogen} · P:{item.input.phosphorus} · K:{item.input.potassium} · pH:{item.input.ph} · {item.input.temperature}°C · {item.input.humidity}% · {item.input.rainfall}mm
                        </p>
                      </div>
                    </div>

                    {/* Other recommendations */}
                    <div className="flex items-center gap-2 shrink-0">
                      {item.recommendations.slice(1).map((rec) => (
                        <span
                          key={rec.rank}
                          className="text-xs text-stone-500 bg-stone-100 px-2 py-1 rounded capitalize"
                        >
                          #{rec.rank} {rec.crop?.name || '?'}
                        </span>
                      ))}
                    </div>

                    {/* Date */}
                    <div className="flex items-center gap-1 text-xs text-stone-400 shrink-0">
                      <Clock className="h-3 w-3" />
                      {formatDate(item.created_at)}
                    </div>
                  </div>
                </Card>
              );
            })}
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
