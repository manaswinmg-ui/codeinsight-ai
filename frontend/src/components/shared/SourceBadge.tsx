import * as React from 'react';

interface SourceBadgeProps {
  source: string;
}

const SOURCE_META: Record<
  string,
  { label: string; icon: string; color: string; bg: string; border: string }
> = {
  ai: {
    label: 'AI',
    icon: '🤖',
    color: '#a78bfa',
    bg: 'rgba(167, 139, 250, 0.1)',
    border: '1px solid rgba(167, 139, 250, 0.25)',
  },
  ruff: {
    label: 'RUFF',
    icon: '⚡',
    color: '#38bdf8',
    bg: 'rgba(56, 189, 248, 0.1)',
    border: '1px solid rgba(56, 189, 248, 0.25)',
  },
  hybrid: {
    label: 'HYBRID',
    icon: '🧬',
    color: '#f472b6',
    bg: 'rgba(244, 114, 182, 0.1)',
    border: '1px solid rgba(244, 114, 182, 0.25)',
  },
};

export const SourceBadge: React.FC<SourceBadgeProps> = ({ source }) => {
  const norm = source.toLowerCase();
  const meta = SOURCE_META[norm] || SOURCE_META['ai'];

  return (
    <span
      style={{
        fontSize: '0.69rem',
        fontWeight: 700,
        color: meta.color,
        background: meta.bg,
        border: meta.border,
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
