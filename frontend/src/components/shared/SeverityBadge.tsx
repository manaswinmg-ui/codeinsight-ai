import * as React from 'react';

interface SeverityBadgeProps {
  severity: string;
}

const SEVERITY_STYLES: Record<
  string,
  { color: string; bg: string; border: string; label: string }
> = {
  critical: {
    color: '#e879f9',
    bg: 'rgba(232,121,249,0.1)',
    border: '1px solid rgba(232,121,249,0.28)',
    label: 'CRITICAL',
  },
  high: {
    color: '#f87171',
    bg: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.25)',
    label: 'HIGH',
  },
  medium: {
    color: '#fbbf24',
    bg: 'rgba(245,158,11,0.1)',
    border: '1px solid rgba(245,158,11,0.25)',
    label: 'MEDIUM',
  },
  low: {
    color: '#60a5fa',
    bg: 'rgba(59,130,246,0.1)',
    border: '1px solid rgba(59,130,246,0.25)',
    label: 'LOW',
  },
  info: {
    color: '#34d399',
    bg: 'rgba(16,185,129,0.1)',
    border: '1px solid rgba(16,185,129,0.25)',
    label: 'INFO',
  },
};

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const norm = severity.toLowerCase();
  const style = SEVERITY_STYLES[norm] || SEVERITY_STYLES['info'];

  return (
    <span
      style={{
        fontSize: '0.7rem',
        background: style.bg,
        color: style.color,
        border: style.border,
        padding: '2px 8px',
        borderRadius: '4px',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.4px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
      }}
    >
      {style.label}
    </span>
  );
};
