import { useState } from 'react';
import {
  Microscope,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  RotateCcw,
  ScanLine,
} from 'lucide-react';
import { Card, Button, Badge, PageHeader, ConfidenceBar, Loader, ErrorMessage } from '../../components/ui';
import ImageUploader from '../../components/disease/ImageUploader';
import { predictDisease } from '../../services/diseaseService';
import { parseApiError } from '../../services/api';
import type { DiseasePredictionResponse } from '../../types';

const statusConfig = {
  healthy: {
    label: 'Healthy',
    variant: 'success' as const,
    icon: <CheckCircle2 className="h-4 w-4" />,
    color: 'text-emerald-700',
    bg: 'bg-emerald-50',
  },
  diseased: {
    label: 'Diseased',
    variant: 'danger' as const,
    icon: <AlertTriangle className="h-4 w-4" />,
    color: 'text-red-700',
    bg: 'bg-red-50',
  },
  uncertain: {
    label: 'Uncertain',
    variant: 'warning' as const,
    icon: <HelpCircle className="h-4 w-4" />,
    color: 'text-amber-700',
    bg: 'bg-amber-50',
  },
};

export default function DiseaseDetectionPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [result, setResult] = useState<DiseasePredictionResponse | null>(null);

  const handleAnalyze = async () => {
    if (!file) return;
    setApiError(null);
    setIsLoading(true);

    try {
      const response = await predictDisease(file);
      setResult(response);
    } catch (err) {
      const parsed = parseApiError(err);
      setApiError(parsed.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setApiError(null);
  };

  // Results View
  if (result) {
    const { prediction, top_3 } = result;
    const status = statusConfig[prediction.status] || statusConfig.uncertain;

    return (
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
        <PageHeader
          title="Analysis Results"
          description="Disease prediction results based on the uploaded leaf image."
        />

        {/* Main Result */}
        <Card className="mb-6">
          <div className="flex items-center gap-3 mb-6">
            <div className={`flex h-10 w-10 items-center justify-center rounded-full ${status.bg} ${status.color}`}>
              {status.icon}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-stone-900">Plant Status</h3>
                <Badge variant={status.variant} size="md">
                  {status.icon}
                  {status.label}
                </Badge>
              </div>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 mb-6">
            <div className="bg-stone-50 rounded-lg p-4">
              <p className="text-xs text-stone-400 uppercase tracking-wider font-medium mb-1">Crop</p>
              <p className="text-lg font-semibold text-stone-900">{prediction.crop}</p>
            </div>
            <div className="bg-stone-50 rounded-lg p-4">
              <p className="text-xs text-stone-400 uppercase tracking-wider font-medium mb-1">Condition</p>
              <p className="text-lg font-semibold text-stone-900 capitalize">
                {prediction.disease === 'healthy' ? 'No disease detected' : prediction.disease}
              </p>
            </div>
          </div>

          <ConfidenceBar score={prediction.score} label="Model Confidence" />
        </Card>

        {/* Top 3 Predictions */}
        <Card className="mb-6">
          <h3 className="text-sm font-semibold text-stone-700 mb-4">Top 3 Predictions</h3>
          <div className="space-y-3">
            {top_3.map((pred, i) => {
              const predStatus = statusConfig[pred.status] || statusConfig.uncertain;
              return (
                <div
                  key={pred.class_name}
                  className="flex items-center gap-3 p-3 rounded-lg bg-stone-50"
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-stone-200 text-xs font-bold text-stone-600 shrink-0">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-stone-800 truncate">
                        {pred.crop} — {pred.disease === 'healthy' ? 'Healthy' : pred.disease}
                      </span>
                      <Badge variant={predStatus.variant} size="sm">
                        {predStatus.label}
                      </Badge>
                    </div>
                    <ConfidenceBar score={pred.score} size="sm" />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Disclaimer */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-8">
          <div className="flex gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" aria-hidden="true" />
            <p className="text-xs text-amber-700 leading-relaxed">
              <strong>Disclaimer:</strong> Predictions are generated by an ML model and should be
              treated as informational guidance rather than a guaranteed diagnosis. Always consult
              local agricultural experts for treatment decisions.
            </p>
          </div>
        </div>

        <div className="flex justify-center">
          <Button variant="outline" onClick={handleReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            Analyze Another Image
          </Button>
        </div>
      </div>
    );
  }

  // Upload View
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10 motion-safe:animate-[fadeIn_0.3s_ease-out]">
      <PageHeader
        title="Plant Disease Detection"
        description="Upload a photo of a plant leaf. Our deep learning model will identify the crop and detect any diseases with confidence scoring."
      />

      {apiError && (
        <div className="mb-6">
          <ErrorMessage
            message={apiError}
            onRetry={() => setApiError(null)}
          />
        </div>
      )}

      <Card className="mb-6">
        <div className="flex items-center gap-2 mb-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-100 text-sky-700">
            <Microscope className="h-4 w-4" />
          </div>
          <h2 className="text-lg font-semibold text-stone-900">Upload Plant Leaf</h2>
        </div>

        <ImageUploader
          file={file}
          onFileSelect={setFile}
          disabled={isLoading}
        />
      </Card>

      {file && !isLoading && (
        <div className="flex justify-end">
          <Button size="lg" onClick={handleAnalyze} className="gap-2">
            <ScanLine className="h-4 w-4" />
            Analyze Leaf
          </Button>
        </div>
      )}

      {isLoading && (
        <Loader message="Analyzing your plant image..." size="lg" />
      )}

      {/* Info Section */}
      <div className="mt-10">
        <Card>
          <h3 className="text-sm font-semibold text-stone-700 mb-3">Supported Crops & Diseases</h3>
          <p className="text-xs text-stone-500 leading-relaxed mb-3">
            Our model covers <strong>14 crop species</strong> and classifies leaves into{' '}
            <strong>38 categories</strong>, including both healthy and diseased states. It achieves a test accuracy of 97.05%.
          </p>
          <div className="flex flex-wrap gap-1.5">
            {['Apple', 'Blueberry', 'Cherry', 'Corn', 'Grape', 'Orange', 'Peach', 'Pepper', 'Potato', 'Raspberry', 'Soybean', 'Squash', 'Strawberry', 'Tomato'].map(
              (crop) => (
                <span
                  key={crop}
                  className="inline-block px-2 py-0.5 rounded text-xs bg-stone-100 text-stone-600 font-medium"
                >
                  {crop}
                </span>
              )
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
