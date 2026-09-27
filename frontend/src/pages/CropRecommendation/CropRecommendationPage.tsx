import { useState, type FormEvent } from 'react';
import { Sprout, Beaker, Thermometer, Droplets, CloudRain, Award, RotateCcw } from 'lucide-react';
import { Card, Button, Input, PageHeader, ConfidenceBar, Loader, ErrorMessage } from '../../components/ui';
import { recommendCrops } from '../../services/cropService';
import { parseApiError } from '../../services/api';
import type { CropRecommendationInput, CropRecommendationResponse } from '../../types';

interface FormErrors {
  [key: string]: string;
}

const initialFormData: CropRecommendationInput = {
  nitrogen: '' as unknown as number,
  phosphorus: '' as unknown as number,
  potassium: '' as unknown as number,
  temperature: '' as unknown as number,
  humidity: '' as unknown as number,
  ph: '' as unknown as number,
  rainfall: '' as unknown as number,
};

function validateForm(data: Record<string, string | number>): FormErrors {
  const errors: FormErrors = {};

  const numFields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall'];

  for (const field of numFields) {
    const val = data[field];
    if (val === '' || val === undefined || val === null) {
      errors[field] = 'This field is required.';
      continue;
    }
    const num = Number(val);
    if (isNaN(num)) {
      errors[field] = 'Must be a valid number.';
      continue;
    }

    if (['nitrogen', 'phosphorus', 'potassium', 'rainfall'].includes(field) && num < 0) {
      errors[field] = 'Value must be 0 or greater.';
    }
    if (field === 'humidity' && (num < 0 || num > 100)) {
      errors[field] = 'Must be between 0 and 100.';
    }
    if (field === 'ph' && (num < 0 || num > 14)) {
      errors[field] = 'Must be between 0 and 14.';
    }
  }

  return errors;
}

const rankColors = [
  'from-amber-400 to-amber-500', // Gold
  'from-stone-300 to-stone-400', // Silver
  'from-orange-400 to-orange-500', // Bronze
];

const rankLabels = ['1st', '2nd', '3rd'];

export default function CropRecommendationPage() {
  const [formData, setFormData] = useState<Record<string, string | number>>(
    initialFormData as unknown as Record<string, string | number>
  );
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [result, setResult] = useState<CropRecommendationResponse | null>(null);

  const updateField = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error on change
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setApiError(null);

    const validationErrors = validateForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    const input: CropRecommendationInput = {
      nitrogen: Number(formData.nitrogen),
      phosphorus: Number(formData.phosphorus),
      potassium: Number(formData.potassium),
      temperature: Number(formData.temperature),
      humidity: Number(formData.humidity),
      ph: Number(formData.ph),
      rainfall: Number(formData.rainfall),
    };

    setIsLoading(true);
    try {
      const response = await recommendCrops(input);
      setResult(response);
    } catch (err) {
      const parsed = parseApiError(err);
      if (parsed.fields) {
        const fieldErrors: FormErrors = {};
        for (const [field, msgs] of Object.entries(parsed.fields)) {
          fieldErrors[field] = Array.isArray(msgs) ? msgs[0] : String(msgs);
        }
        setErrors(fieldErrors);
      } else {
        setApiError(parsed.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setApiError(null);
  };

  // Results View
  if (result) {
    return (
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
        <PageHeader
          title="Crop Recommendations"
          description="Based on your soil and environmental data, here are the best crop options."
        />

        {/* Submitted Conditions Summary */}
        <Card className="mb-8">
          <h3 className="text-sm font-semibold text-stone-700 mb-3">Your Input Conditions</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: 'Nitrogen', value: `${result.input.nitrogen} kg/ha`, icon: <Beaker className="h-3.5 w-3.5" /> },
              { label: 'Phosphorus', value: `${result.input.phosphorus} kg/ha`, icon: <Beaker className="h-3.5 w-3.5" /> },
              { label: 'Potassium', value: `${result.input.potassium} kg/ha`, icon: <Beaker className="h-3.5 w-3.5" /> },
              { label: 'pH', value: result.input.ph.toString(), icon: <Droplets className="h-3.5 w-3.5" /> },
              { label: 'Temperature', value: `${result.input.temperature}°C`, icon: <Thermometer className="h-3.5 w-3.5" /> },
              { label: 'Humidity', value: `${result.input.humidity}%`, icon: <Droplets className="h-3.5 w-3.5" /> },
              { label: 'Rainfall', value: `${result.input.rainfall} mm`, icon: <CloudRain className="h-3.5 w-3.5" /> },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2 text-xs text-stone-600 bg-stone-50 rounded-lg px-3 py-2">
                <span className="text-stone-400">{item.icon}</span>
                <span className="font-medium">{item.label}:</span>
                <span className="ml-auto font-semibold text-stone-800">{item.value}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Recommendations */}
        <div className="space-y-4 mb-8">
          {result.recommendations.map((rec, index) => (
            <Card key={rec.rank} hover className="!p-0 overflow-hidden">
              <div className="flex items-stretch">
                {/* Rank Badge */}
                <div className={`flex items-center justify-center w-20 sm:w-24 bg-gradient-to-b ${rankColors[index] || rankColors[2]} text-white shrink-0`}>
                  <div className="text-center">
                    <Award className="h-6 w-6 mx-auto mb-1" aria-hidden="true" />
                    <span className="text-xs font-bold">{rankLabels[index] || `#${rec.rank}`}</span>
                  </div>
                </div>
                {/* Details */}
                <div className="flex-1 p-5 sm:p-6">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-stone-900 capitalize">
                        {rec.crop.name}
                      </h3>
                      {rec.crop.scientific_name && (
                        <p className="text-xs text-stone-400 italic">{rec.crop.scientific_name}</p>
                      )}
                    </div>
                    <span className="text-2xl font-bold text-stone-800 tabular-nums shrink-0">
                      {(rec.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <ConfidenceBar score={rec.score} label="Model Confidence" size="sm" />
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="flex justify-center">
          <Button variant="outline" onClick={handleReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Form View
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
      <PageHeader
        title="Crop Recommendation"
        description="Enter your soil nutrient levels and environmental conditions. Our model will recommend the best crops for your land."
      />

      {apiError && (
        <div className="mb-6">
          <ErrorMessage
            message={apiError}
            onRetry={() => setApiError(null)}
          />
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        {/* Soil Conditions */}
        <Card className="mb-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 text-amber-700">
              <Beaker className="h-4 w-4" />
            </div>
            <h2 className="text-lg font-semibold text-stone-900">Soil Conditions</h2>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <Input
              label="Nitrogen"
              unit="kg/ha"
              hint="Soil nitrogen content"
              type="number"
              min={0}
              step="any"
              placeholder="e.g. 90"
              value={formData.nitrogen}
              onChange={(e) => updateField('nitrogen', e.target.value)}
              error={errors.nitrogen}
            />
            <Input
              label="Phosphorus"
              unit="kg/ha"
              hint="Soil phosphorus content"
              type="number"
              min={0}
              step="any"
              placeholder="e.g. 42"
              value={formData.phosphorus}
              onChange={(e) => updateField('phosphorus', e.target.value)}
              error={errors.phosphorus}
            />
            <Input
              label="Potassium"
              unit="kg/ha"
              hint="Soil potassium content"
              type="number"
              min={0}
              step="any"
              placeholder="e.g. 43"
              value={formData.potassium}
              onChange={(e) => updateField('potassium', e.target.value)}
              error={errors.potassium}
            />
            <Input
              label="Soil pH"
              unit="0 – 14"
              hint="Soil acidity/alkalinity level"
              type="number"
              min={0}
              max={14}
              step="any"
              placeholder="e.g. 6.5"
              value={formData.ph}
              onChange={(e) => updateField('ph', e.target.value)}
              error={errors.ph}
            />
          </div>
        </Card>

        {/* Environmental Conditions */}
        <Card className="mb-8">
          <div className="flex items-center gap-2 mb-5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-100 text-sky-700">
              <CloudRain className="h-4 w-4" />
            </div>
            <h2 className="text-lg font-semibold text-stone-900">Environmental Conditions</h2>
          </div>
          <div className="grid sm:grid-cols-2 gap-4">
            <Input
              label="Temperature"
              unit="°C"
              hint="Average temperature"
              type="number"
              step="any"
              placeholder="e.g. 25.5"
              value={formData.temperature}
              onChange={(e) => updateField('temperature', e.target.value)}
              error={errors.temperature}
            />
            <Input
              label="Humidity"
              unit="%"
              hint="Relative humidity (0–100)"
              type="number"
              min={0}
              max={100}
              step="any"
              placeholder="e.g. 80"
              value={formData.humidity}
              onChange={(e) => updateField('humidity', e.target.value)}
              error={errors.humidity}
            />
            <Input
              label="Rainfall"
              unit="mm"
              hint="Annual rainfall"
              type="number"
              min={0}
              step="any"
              placeholder="e.g. 200"
              value={formData.rainfall}
              onChange={(e) => updateField('rainfall', e.target.value)}
              error={errors.rainfall}
              className="sm:col-span-2 sm:max-w-[calc(50%-0.5rem)]"
            />
          </div>
        </Card>

        <div className="flex justify-end">
          <Button type="submit" size="lg" isLoading={isLoading} disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Get Recommendations'}
            {!isLoading && <Sprout className="h-4 w-4" />}
          </Button>
        </div>
      </form>

      {isLoading && (
        <div className="mt-8">
          <Loader message="Analyzing your soil and environmental data..." />
        </div>
      )}
    </div>
  );
}
