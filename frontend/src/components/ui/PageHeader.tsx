interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: React.ReactNode;
}

export default function PageHeader({ title, description, badge }: PageHeaderProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-3 mb-2">
        <h1 className="text-2xl md:text-3xl font-bold text-stone-900">{title}</h1>
        {badge}
      </div>
      {description && (
        <p className="text-stone-500 max-w-2xl">{description}</p>
      )}
    </div>
  );
}
