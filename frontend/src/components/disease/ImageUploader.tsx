import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from 'react';
import { Upload, X, ImageIcon } from 'lucide-react';
import { Button } from '../ui';

interface ImageUploaderProps {
  onFileSelect: (file: File | null) => void;
  file: File | null;
  accept?: string;
  maxSizeMB?: number;
  disabled?: boolean;
}

const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

export default function ImageUploader({
  onFileSelect,
  file,
  accept = '.jpg,.jpeg,.png,.webp',
  maxSizeMB = 10,
  disabled = false,
}: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback(
    (f: File): string | null => {
      if (!ACCEPTED_TYPES.includes(f.type)) {
        return 'Invalid file type. Please upload a JPEG, PNG, or WebP image.';
      }
      if (f.size > maxSizeMB * 1024 * 1024) {
        return `File is too large. Maximum size is ${maxSizeMB}MB.`;
      }
      return null;
    },
    [maxSizeMB]
  );

  const handleFile = useCallback(
    (f: File) => {
      const validationError = validateFile(f);
      if (validationError) {
        setError(validationError);
        return;
      }

      setError(null);
      onFileSelect(f);

      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target?.result as string);
      reader.readAsDataURL(f);
    },
    [onFileSelect, validateFile]
  );

  const handleRemove = useCallback(() => {
    onFileSelect(null);
    setPreview(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onFileSelect]);

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) handleFile(droppedFile);
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) handleFile(selectedFile);
  };

  if (file && preview) {
    return (
      <div className="space-y-4">
        <div className="relative rounded-xl overflow-hidden border border-stone-200 bg-stone-50">
          <img
            src={preview}
            alt="Selected plant leaf for analysis"
            className="w-full max-h-80 object-contain bg-stone-100"
          />
          <button
            type="button"
            onClick={handleRemove}
            className="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full bg-stone-900/70 text-white hover:bg-stone-900 transition-colors focus:outline-none focus:ring-2 focus:ring-white"
            aria-label="Remove image"
            disabled={disabled}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center justify-between text-sm text-stone-500">
          <div className="flex items-center gap-2 truncate">
            <ImageIcon className="h-4 w-4 shrink-0" aria-hidden="true" />
            <span className="truncate">{file.name}</span>
          </div>
          <span className="shrink-0">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        onKeyDown={(e) => {
          if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload a plant leaf image. Click or drag and drop."
        className={`
          flex flex-col items-center justify-center gap-4 rounded-xl border-2 border-dashed p-10
          transition-all duration-200 cursor-pointer
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${isDragging
            ? 'border-emerald-500 bg-emerald-50/50'
            : error
              ? 'border-red-300 bg-red-50/30'
              : 'border-stone-300 bg-stone-50/50 hover:border-emerald-400 hover:bg-emerald-50/30'
          }
        `.trim()}
      >
        <div className={`flex h-14 w-14 items-center justify-center rounded-full transition-colors ${
          isDragging ? 'bg-emerald-100 text-emerald-600' : 'bg-stone-100 text-stone-400'
        }`}>
          <Upload className="h-6 w-6" aria-hidden="true" />
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-stone-700">
            {isDragging ? 'Drop your image here' : 'Drag & drop your plant leaf image'}
          </p>
          <p className="mt-1 text-xs text-stone-400">
            or click to browse · JPEG, PNG, WebP · Max {maxSizeMB}MB
          </p>
        </div>
        <Button type="button" variant="outline" size="sm" disabled={disabled} tabIndex={-1}>
          Choose File
        </Button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="sr-only"
        aria-hidden="true"
        disabled={disabled}
      />

      {error && (
        <p className="text-xs text-red-600 flex items-center gap-1" role="alert">
          <svg className="h-3 w-3 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
              clipRule="evenodd"
            />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
