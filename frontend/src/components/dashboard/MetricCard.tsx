import * as React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: string;
  description?: string;
  trend?: {
    value: string;
    type: 'positive' | 'negative' | 'neutral';
  };
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  icon,
  description,
  trend,
}) => {
  return (
    <div className="glass-card" style={{ flex: '1 1 200px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600 }}>
          {title}
        </span>
        <span style={{ fontSize: '1.5rem', opacity: 0.85 }}>{icon}</span>
      </div>
      <div style={{ fontSize: '2rem', fontWeight: 800 }}>{value}</div>
      {trend && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
          <span
            style={{
              color:
                trend.type === 'positive'
                  ? 'var(--success-color)'
                  : trend.type === 'negative'
                    ? 'var(--danger-color)'
                    : 'var(--text-muted)',
              fontWeight: 700,
            }}
          >
            {trend.value}
          </span>
          <span style={{ color: 'var(--text-muted)' }}>than last week</span>
        </div>
      )}
      {description && !trend && (
        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          {description}
        </span>
      )}
    </div>
  );
};
