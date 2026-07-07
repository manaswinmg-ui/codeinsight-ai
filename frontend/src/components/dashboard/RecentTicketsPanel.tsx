import * as React from 'react';
import { SkeletonCard } from '../shared/SkeletonCard';

export interface TicketSummary {
  id: number;
  priority: string;
  status: string;
  title: string;
  review_id: number;
  created_at: string;
}

interface RecentTicketsPanelProps {
  tickets: TicketSummary[];
  loading: boolean;
  onSelectReview: (reviewId: number) => void;
}

export const RecentTicketsPanel: React.FC<RecentTicketsPanelProps> = ({
  tickets,
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
          🎫 Recent Tickets
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
        🎫 Recent Tickets
      </h3>
      {tickets.length === 0 ? (
        <div
          style={{
            padding: '24px',
            textAlign: 'center',
            color: 'var(--text-muted)',
          }}
        >
          No tickets created yet. Open a finding in any review to file a ticket!
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
                <th style={{ padding: '12px 16px' }}>Priority</th>
                <th style={{ padding: '12px 16px' }}>Ticket Title</th>
                <th style={{ padding: '12px 16px' }}>Status</th>
                <th style={{ padding: '12px 16px' }}>Parent Review</th>
                <th style={{ padding: '12px 16px' }}>Created</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((tkt) => (
                <tr
                  key={tkt.id}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    transition: 'background-color 0.2s',
                  }}
                  className="table-row-hover"
                  onClick={() => onSelectReview(tkt.review_id)}
                >
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        background:
                          tkt.priority === 'P0' || tkt.priority === 'P1'
                            ? 'rgba(239, 68, 68, 0.15)'
                            : 'rgba(245, 158, 11, 0.15)',
                        color:
                          tkt.priority === 'P0' || tkt.priority === 'P1'
                            ? 'var(--danger-color)'
                            : 'var(--warning-color)',
                      }}
                    >
                      {tkt.priority}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>
                    {tkt.title}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span
                      style={{
                        fontSize: '0.8rem',
                        fontWeight: 600,
                        color:
                          tkt.status === 'DONE' || tkt.status === 'CLOSED'
                            ? 'var(--text-muted)'
                            : 'var(--text-primary)',
                      }}
                    >
                      {tkt.status}
                    </span>
                  </td>
                  <td
                    style={{ padding: '12px 16px' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => onSelectReview(tkt.review_id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--accent-color)',
                        cursor: 'pointer',
                        padding: 0,
                        fontSize: '0.9rem',
                        fontWeight: 500,
                        textDecoration: 'underline',
                      }}
                    >
                      Review #{tkt.review_id}
                    </button>
                  </td>
                  <td
                    style={{
                      padding: '12px 16px',
                      color: 'var(--text-muted)',
                      fontSize: '0.8rem',
                    }}
                  >
                    {new Date(tkt.created_at).toLocaleDateString()}
                  </td>
                  <td
                    style={{ padding: '12px 16px', textAlign: 'right' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={() => onSelectReview(tkt.review_id)}
                      className="btn btn-secondary"
                      style={{
                        padding: '6px 12px',
                        borderRadius: '6px',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                      }}
                    >
                      Inspect
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
export default RecentTicketsPanel;
