import * as React from 'react';
import { useEffect, useState } from 'react';

interface QualityGaugeProps {
  score: number;
}

export const QualityGauge: React.FC<QualityGaugeProps> = ({ score }) => {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    // Reset score to 0 on mount and animate to target score
    setAnimatedScore(0);
    const duration = 1000; // 1 second animation
    const steps = 60;
    const increment = score / steps;
    const stepTime = duration / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.round(current));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  const getColors = (val: number) => {
    if (val >= 90) return { stroke: 'var(--success-color)', text: 'Excellent' };
    if (val >= 70) return { stroke: 'var(--warning-color)', text: 'Good' };
    if (val >= 50) return { stroke: '#fbbf24', text: 'Moderate' };
    return { stroke: 'var(--danger-color)', text: 'Poor' };
  };

  const colors = getColors(score);
  const radius = 50;
  const strokeWidth = 10;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
        gap: '12px',
        width: '100%',
      }}
    >
      <div style={{ position: 'relative', width: '130px', height: '130px' }}>
        <svg width="130" height="130" style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle */}
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="transparent"
            stroke="rgba(255, 255, 255, 0.05)"
            strokeWidth={strokeWidth}
          />
          {/* Animated Foreground circle */}
          <circle
            cx="65"
            cy="65"
            r={radius}
            fill="transparent"
            stroke={colors.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dashoffset 0.1s ease-out, stroke 0.3s ease',
            }}
          />
        </svg>
        {/* Centered score text */}
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
            lineHeight: 1,
          }}
        >
          <span
            style={{
              fontSize: '2rem',
              fontWeight: 900,
              color: 'var(--text-primary)',
            }}
          >
            {animatedScore}
          </span>
          <span
            style={{
              fontSize: '0.7rem',
              color: 'var(--text-muted)',
              fontWeight: 700,
              marginTop: '4px',
            }}
          >
            / 100
          </span>
        </div>
      </div>
      <div
        style={{
          fontSize: '0.78rem',
          fontWeight: 700,
          color: colors.stroke,
          textTransform: 'uppercase',
          letterSpacing: '1px',
          background: `${colors.stroke}10`,
          padding: '4px 10px',
          borderRadius: '999px',
          border: `1px solid ${colors.stroke}20`,
        }}
      >
        {colors.text}
      </div>
    </div>
  );
};
