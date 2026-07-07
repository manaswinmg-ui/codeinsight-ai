import * as React from 'react';
import { Finding } from '../../pages/ReviewWorkspace';

interface SeverityChartProps {
  findings: Finding[];
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: '#e879f9',
  high: '#f87171',
  medium: '#fbbf24',
  low: '#60a5fa',
  info: '#34d399',
};

export const SeverityChart: React.FC<SeverityChartProps> = ({ findings }) => {
  // Count by severity
  const counts = findings.reduce(
    (acc, finding) => {
      const sev = finding.severity.toLowerCase();
      acc[sev] = (acc[sev] || 0) + 1;
      return acc;
    },
    { critical: 0, high: 0, medium: 0, low: 0, info: 0 } as Record<
      string,
      number
    >
  );

  const total = findings.length;

  if (total === 0) {
    return null;
  }

  const severities = ['critical', 'high', 'medium', 'low', 'info'];

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        width: '100%',
      }}
    >
      <span
        style={{
          fontSize: '0.68rem',
          fontWeight: 700,
          letterSpacing: '0.8px',
          textTransform: 'uppercase',
          color: 'var(--text-muted)',
        }}
      >
        Severity Distribution
      </span>
      {/* Stacked bar */}
      <div
        style={{
          display: 'flex',
          height: '10px',
          width: '100%',
          borderRadius: '999px',
          overflow: 'hidden',
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid var(--border-color)',
        }}
      >
        {severities.map((sev) => {
          const count = counts[sev];
          if (count === 0) return null;
          const percentage = (count / total) * 100;
          return (
            <div
              key={sev}
              style={{
                width: `${percentage}%`,
                background: SEVERITY_COLORS[sev],
                transition: 'width 0.3s ease',
              }}
              title={`${sev.toUpperCase()}: ${count} (${Math.round(percentage)}%)`}
            />
          );
        })}
      </div>
      {/* Legend list */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px 16px',
          marginTop: '4px',
        }}
      >
        {severities.map((sev) => {
          const count = counts[sev];
          if (count === 0) return null;
          return (
            <div
              key={sev}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.75rem',
              }}
            >
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: SEVERITY_COLORS[sev],
                  display: 'inline-block',
                }}
              />
              <span
                style={{
                  textTransform: 'capitalize',
                  fontWeight: 600,
                  color: 'var(--text-secondary)',
                }}
              >
                {sev}
              </span>
              <span
                style={{
                  color: 'var(--text-muted)',
                  fontWeight: 500,
                }}
              >
                ({count})
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
