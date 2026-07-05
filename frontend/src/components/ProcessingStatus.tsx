import React from 'react';

interface ProcessingStatusProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  currentStep: number;
}

const STEPS = [
  'Preparing Review...',
  'Analyzing Code...',
  'Generating Findings...',
  'Finalizing Report...',
];

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  currentStep,
}) => {
  if (status === 'idle') return null;

  return (
    <div
      className="glass-card"
      style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
    >
      <h3
        style={{ margin: 0, fontSize: '1rem', color: 'var(--text-secondary)' }}
      >
        Analysis Progress
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {STEPS.map((step, index) => {
          const isCompleted = status === 'success' || index < currentStep;
          const isActive = status === 'processing' && index === currentStep;
          const isFailed = status === 'error' && index === currentStep;

          let statusIcon = '⚪';
          let textColor = 'var(--text-muted)';
          let fontWeight = 400;

          if (isCompleted) {
            statusIcon = '✅';
            textColor = 'var(--text-primary)';
          } else if (isActive) {
            statusIcon = '🔄';
            textColor = 'var(--accent-color)';
            fontWeight = 600;
          } else if (isFailed) {
            statusIcon = '❌';
            textColor = 'var(--danger-color)';
            fontWeight = 600;
          }

          return (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '8px 12px',
                background: isActive
                  ? 'rgba(99, 102, 241, 0.05)'
                  : 'transparent',
                borderRadius: '6px',
                transition: 'background-color 0.2s',
              }}
            >
              <span
                style={{
                  fontSize: '1.1rem',
                  animation: isActive ? 'spin 1.5s linear infinite' : 'none',
                  display: 'inline-block',
                }}
              >
                {statusIcon}
              </span>
              <span
                style={{ fontSize: '0.9rem', color: textColor, fontWeight }}
              >
                {step}
              </span>
            </div>
          );
        })}
      </div>

      {status === 'processing' && (
        <div
          style={{
            height: '4px',
            width: '100%',
            background: 'var(--bg-tertiary)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${((currentStep + 1) / STEPS.length) * 100}%`,
              background: 'linear-gradient(to right, #6366f1, #818cf8)',
              transition: 'width 0.5s ease',
            }}
          />
        </div>
      )}
    </div>
  );
};
