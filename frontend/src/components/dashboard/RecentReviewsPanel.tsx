import * as React from 'react';
import { SkeletonCard } from '../shared/SkeletonCard';

export interface ReviewSummary {
  id: number;
  language: string;
  status: string;
  created_at: string;
  quality_score: number;
  findings_count: number;
  open_tickets_count: number;
}

interface RecentReviewsPanelProps {
  reviews: ReviewSummary[];
  loading: boolean;
  onSelectReview: (id: number) => void;
}

export const RecentReviewsPanel: React.FC<RecentReviewsPanelProps> = ({
  reviews,
  loading,
  onSelectReview,
}) => {
  if (loading) {
    return (
      <div
        className="glass-card"
        style={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>
          🔍 Recent Reviews
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <SkeletonCard variant="table-row" count={3} />
        </div>
      </div>
    );
  }

  return (
    <div
      className="glass-card"
      style={{
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        minWidth: 0,
      }}
    >
      <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>
        🔍 Recent Reviews
      </h3>
      {reviews.length === 0 ? (
        <div
          style={{
            padding: '24px',
            textAlign: 'center',
            color: 'var(--text-muted)',
          }}
        >
          No reviews available. Try submitting a code snippet first!
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              textAlign: 'left',
              minWidth: '500px',
            }}
          >
            <thead>
              <tr
                style={{
                  borderBottom: '1px solid var(--border-color)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.85rem',
                }}
              >
                <th style={{ padding: '12px 16px' }}>Review ID</th>
                <th style={{ padding: '12px 16px' }}>Language</th>
                <th style={{ padding: '12px 16px' }}>Status</th>
                <th style={{ padding: '12px 16px' }}>Quality Score</th>
                <th style={{ padding: '12px 16px' }}>Findings</th>
                <th style={{ padding: '12px 16px' }}>Tickets</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {reviews.map((rev) => (
                <tr
                  key={rev.id}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s',
                  }}
                  className="table-row-hover"
                  onClick={() => onSelectReview(rev.id)}
                >
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>
                    #{rev.id}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        background: 'rgba(255,255,255,0.04)',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                      }}
                    >
                      {rev.language}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        background:
                          rev.status === 'COMPLETED'
                            ? 'rgba(16, 185, 129, 0.1)'
                            : rev.status === 'FAILED'
                              ? 'rgba(239, 68, 68, 0.1)'
                              : 'rgba(245, 158, 11, 0.1)',
                        color:
                          rev.status === 'COMPLETED'
                            ? 'var(--success-color)'
                            : rev.status === 'FAILED'
                              ? 'var(--danger-color)'
                              : 'var(--warning-color)',
                      }}
                    >
                      {rev.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        fontWeight: 700,
                        color:
                          rev.quality_score >= 90
                            ? 'var(--success-color)'
                            : rev.quality_score >= 70
                              ? 'var(--warning-color)'
                              : 'var(--danger-color)',
                      }}
                    >
                      {rev.quality_score}%
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>{rev.findings_count}</td>
                  <td style={{ padding: '12px 16px' }}>
                    {rev.open_tickets_count} open
                  </td>
                  <td
                    style={{ padding: '12px 16px', textAlign: 'right' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => onSelectReview(rev.id)}
                      className="btn btn-secondary"
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                      }}
                    >
                      Open Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
export default RecentReviewsPanel;
