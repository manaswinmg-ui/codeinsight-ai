import * as React from 'react';
import { useState } from 'react';
import { ReviewDetail } from '../pages/ReviewWorkspace';
import { CreateTicketButton } from './CreateTicketButton';
import { TicketCard, TicketData } from './TicketCard';
import { QualityGauge } from './QualityGauge';
import { SeverityChart } from './SeverityChart';

interface ReviewResultsProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  reviewData: ReviewDetail | null;
  setReviewData?: React.Dispatch<React.SetStateAction<ReviewDetail | null>>;
}

const SEVERITY_STYLES: Record<string, { color: string; bg: string; border: string; label: string }> = {
  critical: { color: '#e879f9', bg: 'rgba(232,121,249,0.1)', border: '1px solid rgba(232,121,249,0.28)', label: 'CRITICAL' },
  high:     { color: '#f87171', bg: 'rgba(239,68,68,0.1)',   border: '1px solid rgba(239,68,68,0.25)',   label: 'HIGH'     },
  medium:   { color: '#fbbf24', bg: 'rgba(245,158,11,0.1)',  border: '1px solid rgba(245,158,11,0.25)',  label: 'MEDIUM'   },
  low:      { color: '#60a5fa', bg: 'rgba(59,130,246,0.1)',  border: '1px solid rgba(59,130,246,0.25)',  label: 'LOW'      },
  info:     { color: '#34d399', bg: 'rgba(16,185,129,0.1)',  border: '1px solid rgba(16,185,129,0.25)',  label: 'INFO'     },
};

const CATEGORY_META: Record<string, { icon: string; color: string }> = {
  BUG:             { icon: '🐛', color: '#f87171' },
  SECURITY:        { icon: '🔒', color: '#e879f9' },
  PERFORMANCE:     { icon: '⚡', color: '#fbbf24' },
  MAINTAINABILITY: { icon: '🔧', color: '#60a5fa' },
  READABILITY:     { icon: '📖', color: '#34d399' },
  RELIABILITY:     { icon: '🛡️', color: '#a78bfa' },
  BEST_PRACTICE:   { icon: '✅', color: '#6ee7b7' },
  DOCUMENTATION:   { icon: '📝', color: '#93c5fd' },
  UNKNOWN:         { icon: '❓', color: '#9ca3af' },
};

const getSeverityStyles = (severity: string) =>
  SEVERITY_STYLES[severity.toLowerCase()] ?? SEVERITY_STYLES['info'];

const getCategoryMeta = (category?: string | null) =>
  CATEGORY_META[(category ?? 'UNKNOWN').toUpperCase()] ?? CATEGORY_META['UNKNOWN'];

const getQualityFeedback = (score: number) => {
  if (score >= 90) return { text: 'Excellent Code Quality', color: 'var(--success-color)' };
  if (score >= 70) return { text: 'Good, but has room for improvement', color: 'var(--warning-color)' };
  if (score >= 50) return { text: 'Moderate — needs attention', color: '#fbbf24' };
  return { text: 'Needs significant attention', color: 'var(--danger-color)' };
};

const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <span style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.8px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
    {children}
  </span>
);

const InfoBlock = ({ icon, label, color, children }: { icon: string; label: string; color: string; children: React.ReactNode }) => (
  <div style={{ background: 'rgba(255,255,255,0.025)', border: `1px solid ${color}22`, borderLeft: `3px solid ${color}`, borderRadius: '8px', padding: '10px 14px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
    <span style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.8px', color }}>{icon} {label}</span>
    <span style={{ fontSize: '0.84rem', lineHeight: '1.55', color: 'var(--text-secondary)' }}>{children}</span>
  </div>
);

const ConfidenceMeter = ({ value }: { value: number }) => {
  const color = value >= 80 ? '#34d399' : value >= 60 ? '#fbbf24' : '#f87171';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '999px', overflow: 'hidden' }}>
        <div style={{ width: `${value}%`, height: '100%', background: color, borderRadius: '999px' }} />
      </div>
      <span style={{ fontSize: '0.75rem', fontWeight: 700, color, minWidth: '36px', textAlign: 'right' }}>{value}%</span>
    </div>
  );
};

export const ReviewResults = ({ status, reviewData, setReviewData }: ReviewResultsProps) => {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());
  const [activeTicket, setActiveTicket] = useState<TicketData | null>(null);
  const [fetchingTicketId, setFetchingTicketId] = useState<number | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);

  if (status !== 'success' || !reviewData) return null;

  const formattedDate = new Date(reviewData.created_at).toLocaleString();
  const feedback = getQualityFeedback(reviewData.quality_score);

  const toggleExpand = (id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleTicketCreated = (findingId: number, ticketId: number) => {
    if (setReviewData) {
      setReviewData((prev) => {
        if (!prev) return null;
        return {
          ...prev,
          findings: prev.findings.map((f) =>
            f.id === findingId ? { ...f, ticket_id: ticketId } : f
          ),
        };
      });
    }
  };

  const handleViewTicket = async (ticketId: number) => {
    setFetchingTicketId(ticketId);
    setFetchError(null);
    try {
      const baseUrl = window.location.origin.includes('5173')
        ? 'http://localhost:8000'
        : '';
      const response = await fetch(`${baseUrl}/api/v1/tickets/${ticketId}`);
      if (!response.ok) {
        throw new Error('Failed to retrieve ticket details');
      }
      const ticket = await response.json();
      setActiveTicket(ticket);
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : 'Error fetching ticket');
    } finally {
      setFetchingTicketId(null);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Ticket Details Panel Modal */}
      {activeTicket && (
        <>
          <div
            onClick={() => setActiveTicket(null)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(4px)',
              zIndex: 999,
            }}
          />
          <TicketCard
            ticket={activeTicket}
            onClose={() => setActiveTicket(null)}
            onStatusUpdated={(updated) => {
              setActiveTicket(updated);
            }}
          />
        </>
      )}

      {fetchError && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--danger-color)', padding: '12px', borderRadius: '8px', fontSize: '0.85rem', color: '#f87171' }}>
          {fetchError}
        </div>
      )}

      <div className="glass-card" style={{ borderLeft: '4px solid var(--success-color)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h4 style={{ margin: 0, color: 'var(--success-color)', fontSize: '1.05rem', fontWeight: 700 }}>Review Completed Successfully</h4>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Analyzed on {formattedDate}</span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>REVIEW ID</span>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>#{reviewData.id}</div>
          </div>
        </div>
      </div>

      <div className="quality-details-grid" style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '20px' }}>
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '16px', borderLeft: `4px solid ${feedback.color}` }}>
          <QualityGauge score={reviewData.quality_score} />
        </div>
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px', justifyContent: 'center', padding: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <SectionLabel>Summary Analysis</SectionLabel>
            <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: '1.65', color: 'var(--text-primary)' }}>{reviewData.summary}</p>
          </div>
          <SeverityChart findings={reviewData.findings} />
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <h3 style={{ margin: '8px 0 0 0', fontSize: '1.1rem', color: 'var(--text-secondary)' }}>
          Detailed Findings ({reviewData.findings.length})
        </h3>

        {reviewData.findings.length === 0 ? (
          <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '48px 24px', textAlign: 'center', border: '1px dashed var(--success-color)', background: 'rgba(16,185,129,0.02)' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🎉</div>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--success-color)', fontSize: '1.1rem' }}>All Clear!</h4>
            <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '400px' }}>No engineering findings detected. The code adheres to standards and looks high quality.</p>
          </div>
        ) : (
          reviewData.findings.map((finding) => {
            const sev = getSeverityStyles(finding.severity);
            const cat = getCategoryMeta(finding.category);
            const isExpanded = expandedIds.has(finding.id);
            const hasExtras = finding.why_it_matters || finding.test_case_hint || (finding.references && finding.references.length > 0);

            return (
              <div key={finding.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '14px', borderLeft: `4px solid ${sev.color}`, padding: '20px' }}>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
                    <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{finding.title}</h4>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                      {finding.category && finding.category !== 'UNKNOWN' && (
                        <span style={{ fontSize: '0.69rem', fontWeight: 700, color: cat.color, background: `${cat.color}18`, border: `1px solid ${cat.color}33`, padding: '2px 7px', borderRadius: '4px', letterSpacing: '0.4px' }}>
                          {cat.icon} {finding.category}
                        </span>
                      )}
                      {finding.line_start != null && (
                        <span style={{ fontSize: '0.69rem', fontWeight: 700, color: 'var(--accent-color)', background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.2)', padding: '2px 7px', borderRadius: '4px', letterSpacing: '0.4px' }}>
                          📍 {finding.line_start === finding.line_end ? `Line ${finding.line_start}` : `Lines ${finding.line_start}–${finding.line_end}`}
                        </span>
                      )}
                      {finding.estimated_fix_time && (
                        <span style={{ fontSize: '0.69rem', fontWeight: 600, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', padding: '2px 7px', borderRadius: '4px' }}>
                          ⏱ {finding.estimated_fix_time}
                        </span>
                      )}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                    <span style={{ fontSize: '0.7rem', background: sev.bg, color: sev.color, border: sev.border, padding: '2px 8px', borderRadius: '4px', fontWeight: 700, textTransform: 'uppercase' }}>{sev.label}</span>
                    <span style={{ fontSize: '0.7rem', background: 'rgba(255,255,255,0.05)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>{finding.status}</span>
                  </div>
                </div>

                {finding.confidence != null && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <SectionLabel>AI Confidence</SectionLabel>
                    <ConfidenceMeter value={finding.confidence} />
                  </div>
                )}

                <p style={{ margin: 0, fontSize: '0.88rem', lineHeight: '1.55', color: 'var(--text-secondary)' }}>{finding.description}</p>

                {finding.impact && (
                  <InfoBlock icon="🎯" label="Impact" color="#fbbf24">{finding.impact}</InfoBlock>
                )}

                {finding.suggested_fix && (
                  <div style={{ background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <SectionLabel>Suggested Fix</SectionLabel>
                    <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.82rem', color: '#a5b4fc', overflowX: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                      <code>{finding.suggested_fix}</code>
                    </pre>
                  </div>
                )}

                {finding.improved_code && (
                  <div style={{ background: 'rgba(52,211,153,0.04)', border: '1px solid rgba(52,211,153,0.18)', borderRadius: '8px', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <span style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.8px', color: '#34d399' }}>✨ IMPROVED CODE</span>
                    <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.82rem', color: '#6ee7b7', overflowX: 'auto', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                      <code>{finding.improved_code}</code>
                    </pre>
                  </div>
                )}

                {/* Create Ticket & Action center controls */}
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginTop: '4px' }}>
                  <CreateTicketButton
                    findingId={finding.id}
                    ticketId={finding.ticket_id}
                    onCreateSuccess={handleTicketCreated}
                    onViewTicket={handleViewTicket}
                  />

                  {fetchingTicketId === finding.ticket_id && finding.ticket_id != null && (
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Loading ticket...</span>
                  )}

                  {hasExtras && (
                    <button
                      onClick={() => toggleExpand(finding.id)}
                      style={{
                        background: 'none',
                        border: '1px solid var(--border-color)',
                        borderRadius: '6px',
                        padding: '5px 12px',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        letterSpacing: '0.3px',
                      }}
                    >
                      {isExpanded ? '▲ Hide details' : '▼ Show details — why it matters, test hints & references'}
                    </button>
                  )}
                </div>

                {isExpanded && hasExtras && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '12px' }}>
                    {finding.why_it_matters && (
                      <InfoBlock icon="💡" label="Why It Matters" color="#a78bfa">{finding.why_it_matters}</InfoBlock>
                    )}
                    {finding.test_case_hint && (
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', background: 'rgba(99,102,241,0.04)', border: '1px solid rgba(99,102,241,0.14)', padding: '10px 14px', borderRadius: '8px' }}>
                        <span style={{ fontSize: '1rem', lineHeight: '1.2' }}>🧪</span>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                          <span style={{ fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.8px', color: 'var(--accent-color)' }}>TEST CASE HINT</span>
                          <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>{finding.test_case_hint}</span>
                        </div>
                      </div>
                    )}
                    {finding.references && finding.references.length > 0 && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <SectionLabel>📚 References</SectionLabel>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {finding.references.map((ref, i) => {
                            const isUrl = ref.startsWith('http://') || ref.startsWith('https://');
                            return isUrl ? (
                              <a key={i} href={ref} target="_blank" rel="noopener noreferrer"
                                style={{ fontSize: '0.81rem', color: '#60a5fa', textDecoration: 'none', wordBreak: 'break-all' }}>
                                🔗 {ref}
                              </a>
                            ) : (
                              <span key={i} style={{ fontSize: '0.81rem', color: 'var(--text-muted)' }}>• {ref}</span>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
