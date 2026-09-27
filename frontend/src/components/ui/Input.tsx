import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  unit?: string;
  hint?: string;
  error?: string;
  icon?: ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, unit, hint, error, icon, id, className = '', ...props }, ref) => {
    const inputId = id || label.toLowerCase().replace(/\s+/g, '-');

    return (
      <div className={`flex flex-col gap-1.5 ${className}`}>
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-stone-700"
        >
          {label}
          {unit && (
            <span className="ml-1 text-xs font-normal text-stone-400">
              ({unit})
            </span>
          )}
        </label>
        <div className="relative">
          {icon && (
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400 pointer-events-none">
              {icon}
            </span>
          )}
          <input
            ref={ref}
            id={inputId}
            className={`
              w-full rounded-lg border bg-white px-3.5 py-2.5 text-sm text-stone-900
              placeholder:text-stone-400
              transition-colors duration-150
              focus:outline-none focus:ring-2 focus:ring-emerald-500/40 focus:border-emerald-500
              disabled:bg-stone-50 disabled:text-stone-400
              ${icon ? 'pl-10' : ''}
              ${error ? 'border-red-400 focus:ring-red-500/40 focus:border-red-500' : 'border-stone-300 hover:border-stone-400'}
            `.trim()}
            aria-invalid={!!error}
            aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
            {...props}
          />
        </div>
        {hint && !error && (
          <p id={`${inputId}-hint`} className="text-xs text-stone-400">
            {hint}
          </p>
        )}
        {error && (
          <p id={`${inputId}-error`} className="text-xs text-red-600 flex items-center gap-1" role="alert">
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
);

Input.displayName = 'Input';
export default Input;
