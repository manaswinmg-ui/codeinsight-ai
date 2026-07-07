import * as React from 'react';

export interface FindingComparisonItem {
  id: number;
  title: string;
  severity: string;
  category: string;
  line_start: number | null;
}

export interface ReviewComparison {
  left_review_id: number;
  right_review_id: number;
  quality_difference: number;
  new_findings: FindingComparisonItem[];
  resolved_findings: FindingComparisonItem[];
  critical_fixed_count: number;
  tickets_closed_count: number;
}

interface ComparisonModalProps {
  comparison: ReviewComparison | null;
  loading: boolean;
  onClose: () => void;
}

export const ComparisonModal: React.FC<ComparisonModalProps> = ({
  comparison,
  loading,
  onClose,
}) => {
  if (!comparison && !loading) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.65)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '800px',
          maxHeight: '90vh',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-focus)',
        }}
      >
        {/* Modal Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid var(--border-color)',
            paddingBottom: '16px',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '1.4rem' }}>
            ⚔️ Review Comparison: #{comparison?.left_review_id} vs #{comparison?.right_review_id}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '1.5rem',
              cursor: 'pointer',
            }}
          >
            ×
          </button>
        </div>

        {loading ? (
          <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
            Comparing reviews and indexing codebase diffs...
          </div>
        ) : (
          comparison && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
              {/* Quality score comparison box */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '16px',
                  background: 'rgba(255,255,255,0.02)',
                  padding: '20px',
                  borderRadius: '12px',
                  border: '1px solid var(--border-color)',
                }}
              >
                <div style={{ textAlign: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Base Review #{comparison.left_review_id}</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px' }}>
                    Active
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Quality Change</span>
                  <div
                    style={{
                      fontSize: '1.8rem',
                      fontWeight: 800,
                      marginTop: '4px',
                      color:
                        comparison.quality_difference > 0
                          ? 'var(--success-color)'
                          : comparison.quality_difference < 0
                            ? 'var(--danger-color)'
                            : 'var(--text-muted)',
                    }}
                  >
                    {comparison.quality_difference > 0 ? '+' : ''}
                    {comparison.quality_difference}%
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Criticals Fixed</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--success-color)', marginTop: '4px' }}>
                    {comparison.critical_fixed_count}
                  </div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Tickets Closed</span>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--success-color)', marginTop: '4px' }}>
                    {comparison.tickets_closed_count}
                  </div>
                </div>
              </div>

              {/* Lists side-by-side */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                {/* Resolved Findings */}
                <div
                  style={{
                    background: 'rgba(16, 185, 129, 0.03)',
                    border: '1px solid rgba(16, 185, 129, 0.1)',
                    borderRadius: '12px',
                    padding: '16px',
                  }}
                >
                  <h4 style={{ margin: '0 0 12px 0', color: 'var(--success-color)', fontSize: '0.95rem' }}>
                    ✅ Resolved Issues ({comparison.resolved_findings.length})
                  </h4>
                  {comparison.resolved_findings.length === 0 ? (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '8px 0' }}>
                      No issues resolved in this revision.
                    </div>
                  ) : (
                    <ul style={{ paddingLeft: '16px', margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {comparison.resolved_findings.map((item) => (
                        <li key={item.id} style={{ fontSize: '0.85rem' }}>
                          <span style={{ fontWeight: 600 }}>{item.title}</span>
                          {item.line_start !== null && (
                            <span style={{ color: 'var(--text-muted)' }}> (Line {item.line_start})</span>
                          )}
                          <span
                            style={{
                              marginLeft: '8px',
                              fontSize: '0.7rem',
                              padding: '2px 4px',
                              borderRadius: '4px',
                              background: 'rgba(255,255,255,0.05)',
                              color: 'var(--text-secondary)',
                            }}
                          >
                            {item.severity}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* New Findings */}
                <div
                  style={{
                    background: 'rgba(239, 68, 68, 0.03)',
                    border: '1px solid rgba(239, 68, 68, 0.1)',
                    borderRadius: '12px',
                    padding: '16px',
                  }}
                >
                  <h4 style={{ margin: '0 0 12px 0', color: 'var(--danger-color)', fontSize: '0.95rem' }}>
                    ⚠️ New Issues Introduced ({comparison.new_findings.length})
                  </h4>
                  {comparison.new_findings.length === 0 ? (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '8px 0' }}>
                      No new issues introduced. Clean code!
                    </div>
                  ) : (
                    <ul style={{ paddingLeft: '16px', margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {comparison.new_findings.map((item) => (
                        <li key={item.id} style={{ fontSize: '0.85rem' }}>
                          <span style={{ fontWeight: 600 }}>{item.title}</span>
                          {item.line_start !== null && (
                            <span style={{ color: 'var(--text-muted)' }}> (Line {item.line_start})</span>
                          )}
                          <span
                            style={{
                              marginLeft: '8px',
                              fontSize: '0.7rem',
                              padding: '2px 4px',
                              borderRadius: '4px',
                              background:
                                item.severity.toLowerCase() === 'critical' || item.severity.toLowerCase() === 'high'
                                  ? 'rgba(239, 68, 68, 0.15)'
                                  : 'rgba(255,255,255,0.05)',
                              color:
                                item.severity.toLowerCase() === 'critical' || item.severity.toLowerCase() === 'high'
                                  ? 'var(--danger-color)'
                                  : 'var(--text-secondary)',
                            }}
                          >
                            {item.severity}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          )
        )}

        {/* Modal Footer */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn" onClick={onClose} style={{ padding: '8px 20px', fontSize: '0.9rem' }}>
            Close comparison
          </button>
        </div>
      </div>
    </div>
  );
};
