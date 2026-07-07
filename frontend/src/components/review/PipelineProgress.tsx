import * as React from 'react';

interface PipelineProgressProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  currentStep: number;
}

const PIPELINE_STAGES = [
  { id: 0, label: 'Uploading Code' },
  { id: 1, label: 'Running Static Analysis' },
  { id: 2, label: 'Generating AI Review' },
  { id: 3, label: 'Merging Findings' },
  { id: 4, label: 'Creating Tickets' },
  { id: 5, label: 'Analysis Complete' },
];

export const PipelineProgress: React.FC<PipelineProgressProps> = ({ status, currentStep }) => {
  if (status === 'idle') return null;

  // Map backend currentStep (0-3) and status to our 6 stages (0-5)
  let activeStage = 0;
  if (status === 'success') {
    activeStage = 5;
  } else if (status === 'error') {
    activeStage = Math.min(currentStep, 4); // Fail on the current stage
  } else {
    // Interpolate steps:
    // currentStep = 0 -> Uploading Code (0)
    // currentStep = 1 -> Running Static Analysis (1)
    // currentStep = 2 -> Generating AI Review (2)
    // currentStep = 3 -> Merging Findings (3) or Creating Tickets (4)
    activeStage = currentStep;
  }

  return (
    <div
      className="glass-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        padding: '24px',
        background: 'rgba(255, 255, 255, 0.01)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
      }}
    >
      <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
        Processing Pipeline
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', position: 'relative' }}>
        {PIPELINE_STAGES.map((stage, idx) => {
          const isCompleted = status === 'success' || idx < activeStage;
          const isActive = status === 'processing' && idx === activeStage;
          const isFailed = status === 'error' && idx === activeStage;


          let circleColor = 'rgba(255, 255, 255, 0.1)';
          let textColor = 'var(--text-muted)';
          let fontWeight = 400;
          let checkmark = '○';

          if (isCompleted) {
            circleColor = 'var(--success-color)';
            textColor = 'var(--text-primary)';
            checkmark = '✓';
          } else if (isActive) {
            circleColor = 'var(--accent-color)';
            textColor = 'var(--accent-color)';
            fontWeight = 600;
            checkmark = '▶';
          } else if (isFailed) {
            circleColor = 'var(--danger-color)';
            textColor = 'var(--danger-color)';
            fontWeight = 600;
            checkmark = '✗';
          }

          return (
            <div key={stage.id} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '6px 0' }}>
                {/* Visual Step Marker */}
                <div
                  style={{
                    width: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: isActive ? 'transparent' : circleColor + '15',
                    border: `2px solid ${circleColor}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.8rem',
                    fontWeight: 800,
                    color: circleColor,
                    zIndex: 2,
                    boxShadow: isActive ? '0 0 12px var(--accent-glow)' : 'none',
                    animation: isActive ? 'pulse-glow 1.5s infinite ease-in-out' : 'none',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <span style={{ fontSize: isCompleted ? '0.9rem' : '0.75rem' }}>{checkmark}</span>
                </div>

                {/* Stage Text */}
                <span
                  style={{
                    fontSize: '0.88rem',
                    color: textColor,
                    fontWeight,
                    transition: 'color 0.3s ease',
                  }}
                >
                  {stage.label}
                </span>
              </div>

              {/* Connecting line */}
              {idx < PIPELINE_STAGES.length - 1 && (
                <div
                  style={{
                    width: '2px',
                    height: '24px',
                    background: isCompleted ? 'var(--success-color)' : 'rgba(255, 255, 255, 0.08)',
                    marginLeft: '13px',
                    marginTop: '-6px',
                    marginBottom: '-6px',
                    zIndex: 1,
                    transition: 'background 0.3s ease',
                  }}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
