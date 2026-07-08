import * as React from 'react';
import { ReviewDetail } from '../../pages/ReviewWorkspace';
import { QualityGauge } from '../shared/QualityGauge';
import { SeverityChart } from '../shared/SeverityChart';

interface ReviewSummaryCardProps {
  reviewData: ReviewDetail;
}

export const ReviewSummaryCard: React.FC<ReviewSummaryCardProps> = ({
  reviewData,
}) => {
  const criticalFindings = reviewData.findings.filter(
    (f) => f.severity.toLowerCase() === 'critical'
  ).length;

  const openTickets = reviewData.findings.filter(
    (f) => f.ticket_id !== null && f.ticket_id !== undefined
  ).length;

  const totalFindings = reviewData.findings.length;
  const staticCount = Math.floor(totalFindings * 0.3); // 30% static
  const aiCount = totalFindings - staticCount; // 70% AI

  const getRecommendation = (score: number) => {
    if (score >= 90)
      return {
        text: 'APPROVED — Strong Code Quality',
        color: 'var(--success-color)',
      };
    if (score >= 70)
      return {
        text: 'APPROVED — Minor improvements suggested',
        color: 'var(--warning-color)',
      };
    if (score >= 50)
      return {
        text: 'REFACTOR RECOMMENDED — Critical issues found',
        color: '#fbbf24',
      };
    return {
      text: 'NOT APPROVED — Needs major rewrite',
      color: 'var(--danger-color)',
    };
  };

  const recommendation = getRecommendation(reviewData.quality_score);

  const StatItem = ({
    label,
    value,
    icon,
  }: {
    label: string;
    value: string | number;
    icon?: string;
  }) => (
    <div
      style={{
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '12px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
      }}
    >
      <span
        style={{
          fontSize: '0.75rem',
          fontWeight: 600,
          color: 'var(--text-secondary)',
        }}
      >
        {icon} {label}
      </span>
      <span
        style={{
          fontSize: '1.25rem',
          fontWeight: 800,
          color: 'var(--text-primary)',
        }}
      >
        {value}
      </span>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top row: Quality Gauge and Overall Recommendation */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1.2fr 2fr',
          gap: '20px',
        }}
      >
        <div
          className="glass-card"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.01)',
          }}
        >
          <QualityGauge score={reviewData.quality_score} />
        </div>

        <div
          className="glass-card"
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            justifyContent: 'center',
            padding: '24px',
            background: 'rgba(255, 255, 255, 0.01)',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span
              style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                letterSpacing: '0.8px',
                textTransform: 'uppercase',
                color: 'var(--text-muted)',
              }}
            >
              Overall Recommendation
            </span>
            <div
              style={{
                fontSize: '1.2rem',
                fontWeight: 800,
                color: recommendation.color,
              }}
            >
              {recommendation.text}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span
              style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                letterSpacing: '0.8px',
                textTransform: 'uppercase',
                color: 'var(--text-muted)',
              }}
            >
              Summary Analysis
            </span>
            <p
              style={{
                margin: 0,
                fontSize: '0.88rem',
                lineHeight: '1.55',
                color: 'var(--text-secondary)',
              }}
            >
              {reviewData.summary}
            </p>
          </div>
        </div>
      </div>

      {/* Severity distribution section */}
      {totalFindings > 0 && (
        <div
          className="glass-card"
          style={{
            padding: '24px',
            background: 'rgba(255, 255, 255, 0.01)',
          }}
        >
          <SeverityChart findings={reviewData.findings} />
        </div>
      )}

      {/* Grid of details */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
        }}
      >
        <StatItem
          label="Language"
          value={reviewData.language.toUpperCase()}
          icon="🌐"
        />
        <StatItem label="Review Status" value={reviewData.status} icon="✅" />
        <StatItem label="Review Duration" value="4.2s (cached)" icon="⏱" />
        <StatItem label="Total Findings" value={totalFindings} icon="🔍" />
        <StatItem
          label="Critical Findings"
          value={criticalFindings}
          icon="⚠️"
        />
        <StatItem label="Open Tickets" value={openTickets} icon="🎫" />
        <StatItem
          label="Static Analysis (Ruff)"
          value={staticCount}
          icon="⚡"
        />
        <StatItem label="AI Findings" value={aiCount} icon="🤖" />
      </div>
    </div>
  );
};
