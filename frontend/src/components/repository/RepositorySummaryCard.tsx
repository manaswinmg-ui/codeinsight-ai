import React from 'react';

interface RepositorySummaryCardProps {
  qualityScore: number;
  languages: Record<string, number>;
  summaryText: string;
}

export const RepositorySummaryCard: React.FC<RepositorySummaryCardProps> = ({
  qualityScore,
  languages,
  summaryText,
}) => {
  // Determine colors based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'var(--success-color)';
    if (score >= 50) return '#f59e0b'; // amber
    return 'var(--danger-color)';
  };

  const scoreColor = getScoreColor(qualityScore);

  // Calculate percentage coordinates for SVG circle
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (qualityScore / 100) * circumference;

  // Total files count for languages
  const totalLanguageFiles = Object.values(languages).reduce(
    (a, b) => a + b,
    0
  );

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        background: 'var(--card-bg)',
        borderRadius: '16px',
        padding: '28px',
        boxShadow: 'var(--card-shadow)',
        border: '1px solid rgba(255, 255, 255, 0.05)',
      }}
    >
      {/* Score Radial Column */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          borderRight: '1px solid rgba(255,255,255,0.06)',
          paddingRight: '20px',
        }}
      >
        <h3
          style={{
            fontSize: '0.9rem',
            color: 'var(--text-secondary)',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '20px',
          }}
        >
          Codebase Health
        </h3>

        <div style={{ position: 'relative', width: '130px', height: '130px' }}>
          <svg width="130" height="130" style={{ transform: 'rotate(-90deg)' }}>
            {/* Background Circle */}
            <circle
              cx="65"
              cy="65"
              r={radius}
              fill="transparent"
              stroke="rgba(255, 255, 255, 0.06)"
              strokeWidth="10"
            />
            {/* Foreground Circle */}
            <circle
              cx="65"
              cy="65"
              r={radius}
              fill="transparent"
              stroke={scoreColor}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              style={{ transition: 'stroke-dashoffset 0.8s ease' }}
            />
          </svg>
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span
              style={{
                fontSize: '2.1rem',
                fontWeight: 800,
                color: 'var(--text-primary)',
              }}
            >
              {qualityScore}
            </span>
            <span
              style={{
                fontSize: '0.7rem',
                color: 'var(--text-secondary)',
                textTransform: 'uppercase',
                fontWeight: 600,
              }}
            >
              Quality Index
            </span>
          </div>
        </div>
      </div>

      {/* Quality Summary Column */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <h3
          style={{
            fontSize: '0.9rem',
            color: 'var(--text-secondary)',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '12px',
          }}
        >
          Executive Summary
        </h3>
        <p
          style={{
            color: 'var(--text-primary)',
            fontSize: '0.95rem',
            lineHeight: '1.6',
            margin: 0,
          }}
        >
          {summaryText || 'Generating summary metrics...'}
        </p>
      </div>

      {/* Languages Distribution Column */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          paddingLeft: '10px',
        }}
      >
        <h3
          style={{
            fontSize: '0.9rem',
            color: 'var(--text-secondary)',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: '16px',
          }}
        >
          Language Distribution
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {Object.entries(languages).map(([lang, count], idx) => {
            const percent =
              totalLanguageFiles > 0
                ? Math.round((count / totalLanguageFiles) * 100)
                : 0;

            return (
              <div key={idx}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.85rem',
                    marginBottom: '4px',
                    fontWeight: 600,
                  }}
                >
                  <span style={{ textTransform: 'capitalize' }}>{lang}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    {count} file{count > 1 ? 's' : ''} ({percent}%)
                  </span>
                </div>
                <div
                  style={{
                    width: '100%',
                    height: '6px',
                    background: 'rgba(255,255,255,0.06)',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${percent}%`,
                      height: '100%',
                      background: 'var(--accent-color)',
                      borderRadius: '3px',
                    }}
                  />
                </div>
              </div>
            );
          })}
          {Object.keys(languages).length === 0 && (
            <p
              style={{
                color: 'var(--text-secondary)',
                fontSize: '0.85rem',
                margin: 0,
              }}
            >
              No language breakdown available.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
