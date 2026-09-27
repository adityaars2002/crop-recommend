interface ConfidenceBarProps {
  score: number;  // 0.0 – 1.0
  label?: string;
  size?: 'sm' | 'md';
}

export default function ConfidenceBar({ score, label, size = 'md' }: ConfidenceBarProps) {
  const percent = Math.round(score * 10000) / 100; // 0.9878 → 98.78
  const barHeight = size === 'sm' ? 'h-1.5' : 'h-2.5';

  // Color based on score ranges
  const barColor =
    percent >= 70 ? 'bg-emerald-500' :
    percent >= 40 ? 'bg-amber-500' :
    'bg-stone-400';

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between gap-2">
        {label && <span className="text-sm text-stone-600 truncate">{label}</span>}
        <span className="text-sm font-semibold text-stone-800 tabular-nums shrink-0">
          {percent.toFixed(2)}%
        </span>
      </div>
      <div className={`w-full ${barHeight} rounded-full bg-stone-100 overflow-hidden`}>
        <div
          className={`${barHeight} rounded-full ${barColor} transition-all duration-700 ease-out`}
          style={{ width: `${Math.min(percent, 100)}%` }}
          role="progressbar"
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`${label || 'Confidence'}: ${percent.toFixed(2)}%`}
        />
      </div>
    </div>
  );
}
