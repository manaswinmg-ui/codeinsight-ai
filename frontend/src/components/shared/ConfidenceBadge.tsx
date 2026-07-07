import * as React from 'react';

interface ConfidenceBadgeProps {
  value: number; // confidence score (0 to 100)
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ value }) => {
  const level = value >= 85 ? 'High' : value >= 60 ? 'Medium' : 'Low';
  const color = level === 'High' ? '#34d399' : level === 'Medium' ? '#fbbf24' : '#f87171';
  const bg = level === 'High' ? 'rgba(52, 211, 153, 0.08)' : level === 'Medium' ? 'rgba(251, 191, 36, 0.08)' : 'rgba(248, 113, 113, 0.08)';
  const border = level === 'High' ? '1px solid rgba(52, 211, 153, 0.25)' : level === 'Medium' ? '1px solid rgba(251, 191, 36, 0.25)' : '1px solid rgba(248, 113, 113, 0.25)';

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
      <span
        style={{
          fontSize: '0.69rem',
          fontWeight: 700,
          color,
          background: bg,
          border,
          padding: '2px 7px',
          borderRadius: '4px',
          letterSpacing: '0.4px',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
        }}
      >
        <span>🎯</span>
        <span>Confidence: {level}</span>
      </span>
      <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
        ({value}%)
      </span>
    </div>
  );
};
