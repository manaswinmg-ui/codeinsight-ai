import * as React from 'react';
import { ReviewSummary } from '../dashboard/RecentReviewsPanel';

interface ReviewTableProps {
  reviews: ReviewSummary[];
  loading: boolean;
  selectedIds: number[];
  onToggleSelect: (id: number) => void;
  onSelectReview: (id: number) => void;
}

export const ReviewTable: React.FC<ReviewTableProps> = ({
  reviews,
  loading,
  selectedIds,
  onToggleSelect,
  onSelectReview,
}) => {
  if (loading) {
    return (
      <div
        className="glass-card"
        style={{
          height: '300px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
        }}
      >
        Synchronizing review logs...
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div
        className="glass-card"
        style={{
          padding: '48px',
          textAlign: 'center',
          color: 'var(--text-muted)',
        }}
      >
        No reviews matched your filter parameters.
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: '20px', minWidth: 0 }}>
      <div style={{ overflowX: 'auto' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            textAlign: 'left',
            minWidth: '700px',
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
              <th style={{ padding: '12px 8px', width: '40px' }}>Select</th>
              <th style={{ padding: '12px 8px' }}>Review ID</th>
              <th style={{ padding: '12px 8px' }}>Language</th>
              <th style={{ padding: '12px 8px' }}>Created At</th>
              <th style={{ padding: '12px 8px' }}>Status</th>
              <th style={{ padding: '12px 8px' }}>Quality Score</th>
              <th style={{ padding: '12px 8px' }}>Findings</th>
              <th style={{ padding: '12px 8px' }}>Tickets</th>
              <th style={{ padding: '12px 8px', textAlign: 'right' }}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {reviews.map((rev) => {
              const isChecked = selectedIds.includes(rev.id);
              const isDisabled = !isChecked && selectedIds.length >= 2;

              return (
                <tr
                  key={rev.id}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    fontSize: '0.9rem',
                    opacity: isDisabled ? 0.5 : 1,
                  }}
                  className="table-row-hover"
                >
                  <td style={{ padding: '12px 8px' }}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      disabled={isDisabled}
                      onChange={() => onToggleSelect(rev.id)}
                      style={{
                        cursor: isDisabled ? 'not-allowed' : 'pointer',
                        width: '16px',
                        height: '16px',
                      }}
                    />
                  </td>
                  <td style={{ padding: '12px 8px', fontWeight: 600 }}>
                    #{rev.id}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <span
                      style={{
                        background: 'rgba(255, 255, 255, 0.04)',
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '0.8rem',
                      }}
                    >
                      {rev.language}
                    </span>
                  </td>
                  <td
                    style={{
                      padding: '12px 8px',
                      color: 'var(--text-secondary)',
                      fontSize: '0.85rem',
                    }}
                  >
                    {new Date(rev.created_at).toLocaleString()}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
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
                  <td style={{ padding: '12px 8px' }}>
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
                  <td style={{ padding: '12px 8px' }}>
                    {rev.findings_count} finding(s)
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    {rev.open_tickets_count} open
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                    <button
                      className="btn"
                      onClick={() => onSelectReview(rev.id)}
                      style={{
                        padding: '6px 12px',
                        fontSize: '0.85rem',
                        background: 'transparent',
                        border: '1px solid var(--accent-color)',
                        color: 'var(--accent-color)',
                      }}
                    >
                      Open Review
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
