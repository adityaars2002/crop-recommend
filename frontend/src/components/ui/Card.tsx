import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export default function Card({
  children,
  className = '',
  hover = false,
  padding = 'md',
}: CardProps) {
  return (
    <div
      className={`
        bg-white rounded-xl border border-stone-200/80 shadow-sm
        ${paddingClasses[padding]}
        ${hover ? 'transition-all duration-200 hover:shadow-md hover:border-stone-300 hover:-translate-y-0.5' : ''}
        ${className}
      `.trim()}
    >
      {children}
    </div>
  );
}
