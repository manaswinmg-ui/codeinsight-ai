import * as React from 'react';

interface CategoryBadgeProps {
  category?: string | null;
}

const CATEGORY_META: Record<string, { icon: string; color: string; label: string }> = {
  BUG:             { icon: '🐛', color: '#f87171', label: 'BUG' },
  SECURITY:        { icon: '🔒', color: '#e879f9', label: 'SECURITY' },
  PERFORMANCE:     { icon: '⚡', color: '#fbbf24', label: 'PERFORMANCE' },
  MAINTAINABILITY: { icon: '🔧', color: '#60a5fa', label: 'MAINTAINABILITY' },
  ARCHITECTURE:    { icon: '🏛️', color: '#a78bfa', label: 'ARCHITECTURE' },
  STYLE:           { icon: '🎨', color: '#34d399', label: 'STYLE' },
  READABILITY:     { icon: '📖', color: '#34d399', label: 'READABILITY' },
  RELIABILITY:     { icon: '🛡️', color: '#a78bfa', label: 'RELIABILITY' },
  BEST_PRACTICE:   { icon: '✅', color: '#6ee7b7', label: 'BEST PRACTICE' },
  DOCUMENTATION:   { icon: '📝', color: '#93c5fd', label: 'DOCUMENTATION' },
  UNKNOWN:         { icon: '❓', color: '#9ca3af', label: 'UNKNOWN' },
};

export const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category }) => {
  const norm = (category ?? 'UNKNOWN').toUpperCase();
  const meta = CATEGORY_META[norm] || CATEGORY_META['UNKNOWN'];

  return (
    <span
      style={{
        fontSize: '0.69rem',
        fontWeight: 700,
        color: meta.color,
        background: `${meta.color}18`,
        border: `1px solid ${meta.color}33`,
        padding: '2px 7px',
        borderRadius: '4px',
        letterSpacing: '0.4px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
      }}
    >
      <span>{meta.icon}</span>
      <span>{meta.label}</span>
    </span>
  );
};
