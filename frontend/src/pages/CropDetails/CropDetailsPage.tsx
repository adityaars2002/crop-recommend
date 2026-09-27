import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Sprout, Thermometer, Droplets, Clock, Leaf } from 'lucide-react';
import { Card, PageHeader, Loader, ErrorMessage, Badge } from '../../components/ui';
import { getCropById } from '../../services/cropService';
import { parseApiError } from '../../services/api';
import type { Crop } from '../../types';

export default function CropDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const [crop, setCrop] = useState<Crop | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    setError(null);

    getCropById(Number(id))
      .then(setCrop)
      .catch((err) => {
        const parsed = parseApiError(err);
        setError(parsed.message);
      })
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) return <Loader message="Loading crop details..." />;
  if (error) return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <ErrorMessage message={error} onRetry={() => window.location.reload()} />
    </div>
  );
  if (!crop) return null;

  const details = [
    { label: 'Soil Type', value: crop.soil_type, icon: <Leaf className="h-4 w-4" /> },
    { label: 'pH Range', value: crop.min_ph != null && crop.max_ph != null ? `${crop.min_ph} – ${crop.max_ph}` : null, icon: <Droplets className="h-4 w-4" /> },
    { label: 'Temperature', value: crop.min_temperature != null && crop.max_temperature != null ? `${crop.min_temperature}°C – ${crop.max_temperature}°C` : null, icon: <Thermometer className="h-4 w-4" /> },
    { label: 'Water Requirement', value: crop.water_requirement, icon: <Droplets className="h-4 w-4" /> },
    { label: 'Growing Duration', value: crop.growing_duration, icon: <Clock className="h-4 w-4" /> },
  ].filter((d) => d.value);

  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
      <Link
        to="/crops"
        className="inline-flex items-center gap-1 text-sm text-stone-500 hover:text-emerald-700 transition-colors mb-6"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Crops
      </Link>

      <div className="flex items-start gap-4 mb-8">
        <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 shrink-0">
          <Sprout className="h-7 w-7" />
        </div>
        <div>
          <PageHeader title={crop.name} />
          {crop.scientific_name && (
            <p className="text-sm text-stone-400 italic -mt-6">{crop.scientific_name}</p>
          )}
        </div>
      </div>

      {crop.description && (
        <Card className="mb-6">
          <h2 className="text-sm font-semibold text-stone-700 mb-2">Description</h2>
          <p className="text-sm text-stone-600 leading-relaxed">{crop.description}</p>
        </Card>
      )}

      {details.length > 0 && (
        <Card className="mb-6">
          <h2 className="text-sm font-semibold text-stone-700 mb-4">Growing Conditions</h2>
          <div className="grid sm:grid-cols-2 gap-3">
            {details.map((d) => (
              <div key={d.label} className="flex items-center gap-3 bg-stone-50 rounded-lg p-3">
                <span className="text-stone-400">{d.icon}</span>
                <div>
                  <p className="text-xs text-stone-400 font-medium">{d.label}</p>
                  <p className="text-sm font-semibold text-stone-800">{d.value}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {crop.fertilizer_information && (
        <Card className="mb-6">
          <h2 className="text-sm font-semibold text-stone-700 mb-2">Fertilizer Information</h2>
          <p className="text-sm text-stone-600 leading-relaxed">{crop.fertilizer_information}</p>
        </Card>
      )}

      {crop.general_information && (
        <Card className="mb-6">
          <h2 className="text-sm font-semibold text-stone-700 mb-2">
            <Badge variant="info">Info</Badge> Additional Notes
          </h2>
          <p className="text-sm text-stone-600 leading-relaxed mt-2">{crop.general_information}</p>
        </Card>
      )}
    </div>
  );
}
