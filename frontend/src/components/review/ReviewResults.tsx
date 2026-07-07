import * as React from 'react';
import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { ReviewDetail, Finding } from '../../pages/ReviewWorkspace';
import { CreateTicketButton } from '../tickets/CreateTicketButton';
import { TicketCard, TicketData } from '../tickets/TicketCard';
import { ReviewTabs } from './ReviewTabs';
import { ReviewSummaryCard } from './ReviewSummaryCard';
import { DeveloperDebugPanel } from './DeveloperDebugPanel';
import { SeverityBadge } from '../shared/SeverityBadge';
import { SourceBadge } from '../shared/SourceBadge';
import { CategoryBadge } from '../shared/CategoryBadge';
import { ConfidenceBadge } from '../shared/ConfidenceBadge';
import { EmptyState } from '../shared/EmptyState';

interface ReviewResultsProps {
  status: 'idle' | 'processing' | 'success' | 'error';
  reviewData: ReviewDetail | null;
  setReviewData?: React.Dispatch<React.SetStateAction<ReviewDetail | null>>;
  showDebug?: boolean;
}

const getEstimatedFixTime = (severity: string): string => {
  const norm = severity.toLowerCase();
  if (norm === 'critical') return '~45 mins';
  if (norm === 'high') return '~30 mins';
  if (norm === 'medium') return '~15 mins';
  return '~5 mins';
};

const SectionLabel = ({ children }: { children: React.ReactNode }) => (
  <span
    style={{
      fontSize: '0.68rem',
      fontWeight: 700,
      letterSpacing: '0.8px',
      textTransform: 'uppercase',
      color: 'var(--text-muted)',
    }}
  >
    {children}
  </span>
);

const InfoBlock = ({
  icon,
  label,
  color,
  children,
}: {
  icon: string;
  label: string;
  color: string;
  children: React.ReactNode;
}) => (
  <div
    style={{
      background: 'rgba(255,255,255,0.025)',
      border: `1px solid ${color}22`,
      borderLeft: `3px solid ${color}`,
      borderRadius: '8px',
      padding: '10px 14px',
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
    }}
  >
    <span
      style={{
        fontSize: '0.68rem',
        fontWeight: 700,
        letterSpacing: '0.8px',
        color,
      }}
    >
      {icon} {label}
    </span>
    <span
      style={{
        fontSize: '0.84rem',
        lineHeight: '1.55',
        color: 'var(--text-secondary)',
      }}
    >
      {children}
    </span>
  </div>
);

export const ReviewResults = ({
  status,
  reviewData,
  setReviewData,
  showDebug = false,
}: ReviewResultsProps) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<number>>(
    new Set()
  );
  const [activeTicket, setActiveTicket] = useState<TicketData | null>(null);
  const [fetchingTicketId, setFetchingTicketId] = useState<number | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const [selectedFindingInCode, setSelectedFindingInCode] =
    useState<Finding | null>(null);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationsRef = useRef<string[]>([]);
  const allDecorationsRef = useRef<string[]>([]);

  // Clear decorations when switching tabs or unmounting
  React.useEffect(() => {
    return () => {
      if (editorRef.current) {
        if (decorationsRef.current.length > 0) {
          editorRef.current.deltaDecorations(decorationsRef.current, []);
        }
        if (allDecorationsRef.current.length > 0) {
          editorRef.current.deltaDecorations(allDecorationsRef.current, []);
        }
      }
    };
  }, [activeTab]);

  const handleSelectFindingInCode = (finding: Finding) => {
    setSelectedFindingInCode(finding);
    if (finding.line_start && editorRef.current && monacoRef.current) {
      const editor = editorRef.current;
      const monaco = monacoRef.current;

      editor.revealLineInCenter(finding.line_start);
      editor.setPosition({ lineNumber: finding.line_start, column: 1 });
      editor.focus();

      if (decorationsRef.current.length > 0) {
        decorationsRef.current = editor.deltaDecorations(
          decorationsRef.current,
          []
        );
      }

      decorationsRef.current = editor.deltaDecorations(
        [],
        [
          {
            range: new monaco.Range(
              finding.line_start,
              1,
              finding.line_start,
              1
            ),
            options: {
              isWholeLine: true,
              className: 'monaco-line-highlight-finding',
              marginClassName: 'monaco-margin-highlight-finding',
            },
          },
        ]
      );
    }
  };

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Apply markers/decorations for all findings
    if (reviewData) {
      const newDecorations = reviewData.findings
        .filter((f) => f.line_start != null)
        .map((f) => {
          const severity = f.severity.toLowerCase();
          return {
            range: new monaco.Range(f.line_start!, 1, f.line_start!, 1),
            options: {
              isWholeLine: false,
              glyphMarginClassName: `monaco-glyph-margin-${severity}`,
              overviewRuler: {
                color:
                  severity === 'critical' || severity === 'high'
                    ? '#ef4444'
                    : '#fbbf24',
                position: monaco.editor.OverviewRulerLane.Right,
              },
              minimap: {
                color:
                  severity === 'critical' || severity === 'high'
                    ? '#ef4444'
                    : '#fbbf24',
                position: monaco.editor.MinimapPosition.Inline,
              },
            },
          };
        });

      allDecorationsRef.current = editor.deltaDecorations([], newDecorations);
    }

    // If there is already a selected finding, highlight it
    if (selectedFindingInCode) {
      handleSelectFindingInCode(selectedFindingInCode);
    }
  };

  if (status !== 'success' || !reviewData) return null;

  const formattedDate = new Date(reviewData.created_at).toLocaleString();

  const toggleExpandCard = (id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleExpandDescription = (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedDescriptions((prev) => {
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
      setFetchError(
        err instanceof Error ? err.message : 'Error fetching ticket'
      );
    } finally {
      setFetchingTicketId(null);
    }
  };

  // Extract all findings with associated tickets
  const ticketedFindings = reviewData.findings.filter(
    (f) => f.ticket_id != null
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
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
        <div
          style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid var(--danger-color)',
            padding: '12px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            color: '#f87171',
          }}
        >
          {fetchError}
        </div>
      )}

      {/* Tabs Controller */}
      <ReviewTabs
        activeTab={activeTab}
        onTabChange={setActiveTab}
        showDebug={showDebug}
      />

      {/* Render Tab Contents */}
      {activeTab === 'overview' && (
        <ReviewSummaryCard reviewData={reviewData} />
      )}

      {activeTab === 'code' && (
        <div
          style={{
            display: 'flex',
            gap: '24px',
            height: '520px',
            width: '100%',
            alignItems: 'stretch',
          }}
        >
          {/* Left Column: Monaco Editor Container */}
          <div
            style={{
              flex: '1 1 65%',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              overflow: 'hidden',
              background: '#1e1e1e',
              height: '100%',
              minWidth: 0,
            }}
          >
            <Editor
              height="100%"
              language={reviewData.language.toLowerCase()}
              theme="vs-dark"
              value={reviewData.code}
              onMount={handleEditorDidMount}
              options={{
                readOnly: true,
                minimap: { enabled: true },
                fontSize: 13,
                fontFamily:
                  'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
                lineNumbers: 'on',
                glyphMargin: true,
                roundedSelection: true,
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 12, bottom: 12 },
              }}
            />
          </div>

          {/* Right Column: Finding Navigation List */}
          <div
            style={{
              flex: '0 0 32%',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              overflowY: 'auto',
              paddingRight: '6px',
              height: '100%',
            }}
          >
            <h4
              style={{
                margin: 0,
                fontSize: '0.9rem',
                color: 'var(--text-secondary)',
                fontWeight: 700,
              }}
            >
              📌 Review Findings ({reviewData.findings.length})
            </h4>
            {reviewData.findings.length === 0 ? (
              <div
                style={{
                  padding: '20px',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                  fontSize: '0.85rem',
                }}
              >
                No findings in this review.
              </div>
            ) : (
              reviewData.findings.map((f) => {
                const isSelected = selectedFindingInCode?.id === f.id;
                return (
                  <div
                    key={f.id}
                    onClick={() => handleSelectFindingInCode(f)}
                    style={{
                      padding: '12px',
                      borderRadius: '8px',
                      background: isSelected
                        ? 'rgba(99, 102, 241, 0.12)'
                        : 'rgba(255, 255, 255, 0.02)',
                      border: isSelected
                        ? '1px solid var(--accent-color)'
                        : '1px solid var(--border-color)',
                      borderLeft: `4px solid ${f.severity.toLowerCase() === 'critical' ? '#e879f9' : f.severity.toLowerCase() === 'high' ? '#f87171' : '#fbbf24'}`,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        gap: '8px',
                        marginBottom: '6px',
                      }}
                    >
                      <span
                        style={{
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                          wordBreak: 'break-word',
                        }}
                      >
                        {f.title}
                      </span>
                      {f.line_start != null && (
                        <span
                          style={{
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            color: 'var(--accent-color)',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          L{f.line_start}
                        </span>
                      )}
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        gap: '6px',
                        flexWrap: 'wrap',
                        alignItems: 'center',
                      }}
                    >
                      <SeverityBadge severity={f.severity} />
                      <CategoryBadge category={f.category} />
                    </div>
                    {isSelected && (
                      <div
                        style={{
                          marginTop: '8px',
                          fontSize: '0.78rem',
                          color: 'var(--text-secondary)',
                          borderTop: '1px solid rgba(255,255,255,0.06)',
                          paddingTop: '8px',
                          lineHeight: '1.4',
                        }}
                      >
                        {f.description}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {activeTab === 'findings' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <h3
              style={{
                margin: 0,
                fontSize: '1.1rem',
                color: 'var(--text-secondary)',
              }}
            >
              Detailed Findings ({reviewData.findings.length})
            </h3>
            {reviewData.findings.length > 0 && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  className="btn btn-secondary"
                  onClick={() =>
                    setExpandedIds(
                      new Set(reviewData.findings.map((f) => f.id))
                    )
                  }
                  style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                >
                  Expand All
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => setExpandedIds(new Set())}
                  style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                >
                  Collapse All
                </button>
              </div>
            )}
          </div>

          {reviewData.findings.length === 0 ? (
            <EmptyState
              title="Excellent work!"
              description="No bugs, security issues, or performance bottlenecks were detected in this analysis."
              icon="🎉"
            />
          ) : (
            reviewData.findings.map((finding) => {
              const isCardExpanded = expandedIds.has(finding.id);
              const isDescExpanded = expandedDescriptions.has(finding.id);
              const hasExtras =
                finding.why_it_matters ||
                finding.test_case_hint ||
                (finding.references && finding.references.length > 0);

              const descriptionLimit = 180;
              const isLongDescription =
                finding.description.length > descriptionLimit;
              const displayedDescription =
                isDescExpanded || isCardExpanded
                  ? finding.description
                  : `${finding.description.substring(0, descriptionLimit)}...`;

              const mockSource = finding.suggested_fix ? 'ruff' : 'ai'; // Simple heuristics to assign a source if none exists
              const mockConfidence = finding.confidence ?? 85;

              return (
                <div
                  key={finding.id}
                  className="glass-card"
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '14px',
                    borderLeft: `4px solid ${finding.severity.toLowerCase() === 'critical' ? '#e879f9' : finding.severity.toLowerCase() === 'high' ? '#f87171' : '#fbbf24'}`,
                    padding: '20px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                  onClick={() => toggleExpandCard(finding.id)}
                >
                  {/* Card Header */}
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      gap: '12px',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                        flex: 1,
                      }}
                    >
                      <h4
                        style={{
                          margin: 0,
                          fontSize: '1rem',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                        }}
                      >
                        {finding.title}
                      </h4>
                      <div
                        style={{
                          display: 'flex',
                          gap: '8px',
                          flexWrap: 'wrap',
                          alignItems: 'center',
                        }}
                      >
                        <SeverityBadge severity={finding.severity} />
                        <SourceBadge
                          source={
                            finding.category?.toLowerCase() === 'style'
                              ? 'ruff'
                              : mockSource
                          }
                        />
                        <CategoryBadge category={finding.category} />
                        <ConfidenceBadge value={mockConfidence} />
                        <span
                          style={{
                            fontSize: '0.69rem',
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            background: 'rgba(255,255,255,0.04)',
                            border: '1px solid var(--border-color)',
                            padding: '2px 7px',
                            borderRadius: '4px',
                          }}
                        >
                          ⏱ {getEstimatedFixTime(finding.severity)}
                        </span>
                      </div>
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        gap: '8px',
                        alignItems: 'center',
                        flexShrink: 0,
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {finding.line_start != null && (
                        <span
                          style={{
                            fontSize: '0.69rem',
                            fontWeight: 700,
                            color: 'var(--accent-color)',
                            background: 'rgba(99, 102, 241, 0.08)',
                            border: '1px solid rgba(99, 102, 241, 0.2)',
                            padding: '2px 7px',
                            borderRadius: '4px',
                          }}
                        >
                          📍 L{finding.line_start}
                          {finding.line_end &&
                          finding.line_end !== finding.line_start
                            ? `–${finding.line_end}`
                            : ''}
                        </span>
                      )}
                      <CreateTicketButton
                        findingId={finding.id}
                        ticketId={finding.ticket_id}
                        onCreateSuccess={handleTicketCreated}
                        onViewTicket={handleViewTicket}
                      />
                      <span
                        onClick={() => toggleExpandCard(finding.id)}
                        style={{
                          fontSize: '0.8rem',
                          color: 'var(--text-muted)',
                          cursor: 'pointer',
                          padding: '4px',
                        }}
                      >
                        {isCardExpanded ? '▲' : '▼'}
                      </span>
                    </div>
                  </div>

                  {/* Card Description */}
                  <div
                    style={{
                      margin: 0,
                      fontSize: '0.88rem',
                      lineHeight: '1.55',
                      color: 'var(--text-secondary)',
                    }}
                  >
                    <span>{displayedDescription}</span>
                    {isLongDescription && !isCardExpanded && (
                      <button
                        onClick={(e) => toggleExpandDescription(finding.id, e)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--accent-color)',
                          cursor: 'pointer',
                          fontSize: '0.85rem',
                          fontWeight: 600,
                          padding: '0 4px',
                          textDecoration: 'underline',
                        }}
                      >
                        {isDescExpanded ? 'Read less' : 'Read more'}
                      </button>
                    )}
                  </div>

                  {/* Expanded Content */}
                  {isCardExpanded && (
                    <div
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '16px',
                        marginTop: '4px',
                        width: '100%',
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      {finding.impact && (
                        <InfoBlock icon="🎯" label="Impact" color="#fbbf24">
                          {finding.impact}
                        </InfoBlock>
                      )}

                      {finding.suggested_fix && (
                        <div
                          style={{
                            background: 'var(--bg-tertiary)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '8px',
                            padding: '12px 16px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px',
                          }}
                        >
                          <SectionLabel>Suggested Fix</SectionLabel>
                          <pre
                            style={{
                              margin: 0,
                              fontFamily: 'monospace',
                              fontSize: '0.82rem',
                              color: '#a5b4fc',
                              overflowX: 'auto',
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-all',
                            }}
                          >
                            <code>{finding.suggested_fix}</code>
                          </pre>
                        </div>
                      )}

                      {finding.improved_code && (
                        <div
                          style={{
                            background: 'rgba(52,211,153,0.04)',
                            border: '1px solid rgba(52,211,153,0.18)',
                            borderRadius: '8px',
                            padding: '12px 16px',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px',
                          }}
                        >
                          <span
                            style={{
                              fontSize: '0.68rem',
                              fontWeight: 700,
                              letterSpacing: '0.8px',
                              color: '#34d399',
                            }}
                          >
                            ✨ IMPROVED CODE
                          </span>
                          <pre
                            style={{
                              margin: 0,
                              fontFamily: 'monospace',
                              fontSize: '0.82rem',
                              color: '#6ee7b7',
                              overflowX: 'auto',
                              whiteSpace: 'pre-wrap',
                              wordBreak: 'break-all',
                            }}
                          >
                            <code>{finding.improved_code}</code>
                          </pre>
                        </div>
                      )}

                      {fetchingTicketId === finding.ticket_id &&
                        finding.ticket_id != null && (
                          <div
                            style={{
                              display: 'flex',
                              gap: '12px',
                              alignItems: 'center',
                              marginTop: '4px',
                            }}
                          >
                            <span
                              style={{
                                fontSize: '0.75rem',
                                color: 'var(--text-muted)',
                              }}
                            >
                              Loading ticket...
                            </span>
                          </div>
                        )}

                      {hasExtras && (
                        <div
                          style={{
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '12px',
                            borderTop: '1px solid var(--border-color)',
                            paddingTop: '14px',
                            marginTop: '4px',
                          }}
                        >
                          {finding.why_it_matters && (
                            <InfoBlock
                              icon="💡"
                              label="Why It Matters"
                              color="#a78bfa"
                            >
                              {finding.why_it_matters}
                            </InfoBlock>
                          )}
                          {finding.test_case_hint && (
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '8px',
                                background: 'rgba(99,102,241,0.04)',
                                border: '1px solid rgba(99,102,241,0.14)',
                                padding: '10px 14px',
                                borderRadius: '8px',
                              }}
                            >
                              <span
                                style={{ fontSize: '1rem', lineHeight: '1.2' }}
                              >
                                🧪
                              </span>
                              <div
                                style={{
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: '2px',
                                }}
                              >
                                <span
                                  style={{
                                    fontSize: '0.68rem',
                                    fontWeight: 700,
                                    letterSpacing: '0.8px',
                                    color: 'var(--accent-color)',
                                  }}
                                >
                                  TEST CASE HINT
                                </span>
                                <span
                                  style={{
                                    fontSize: '0.82rem',
                                    color: 'var(--text-secondary)',
                                    lineHeight: '1.4',
                                  }}
                                >
                                  {finding.test_case_hint}
                                </span>
                              </div>
                            </div>
                          )}
                          {finding.references &&
                            finding.references.length > 0 && (
                              <div
                                style={{
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: '6px',
                                }}
                              >
                                <SectionLabel>📚 References</SectionLabel>
                                <div
                                  style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '4px',
                                  }}
                                >
                                  {finding.references.map((ref, i) => {
                                    const isUrl =
                                      ref.startsWith('http://') ||
                                      ref.startsWith('https://');
                                    return isUrl ? (
                                      <a
                                        key={i}
                                        href={ref}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        style={{
                                          fontSize: '0.81rem',
                                          color: '#60a5fa',
                                          textDecoration: 'none',
                                          wordBreak: 'break-all',
                                        }}
                                      >
                                        🔗 {ref}
                                      </a>
                                    ) : (
                                      <span
                                        key={i}
                                        style={{
                                          fontSize: '0.81rem',
                                          color: 'var(--text-muted)',
                                        }}
                                      >
                                        • {ref}
                                      </span>
                                    );
                                  })}
                                </div>
                              </div>
                            )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}

      {activeTab === 'tickets' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3
            style={{
              margin: 0,
              fontSize: '1.1rem',
              color: 'var(--text-secondary)',
            }}
          >
            Associated Tickets ({ticketedFindings.length})
          </h3>

          {ticketedFindings.length === 0 ? (
            <EmptyState
              title="No tickets created yet."
              description="You can create bug-tracking tickets directly from specific finding items inside the Findings tab."
              icon="🎫"
            />
          ) : (
            <div
              className="glass-card"
              style={{ padding: 0, overflowX: 'auto' }}
            >
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  textAlign: 'left',
                }}
              >
                <thead>
                  <tr
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      background: 'rgba(255,255,255,0.01)',
                    }}
                  >
                    <th
                      style={{
                        padding: '16px 24px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--text-secondary)',
                      }}
                    >
                      PRIORITY
                    </th>
                    <th
                      style={{
                        padding: '16px 24px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--text-secondary)',
                      }}
                    >
                      STATUS
                    </th>
                    <th
                      style={{
                        padding: '16px 24px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--text-secondary)',
                      }}
                    >
                      TITLE
                    </th>
                    <th
                      style={{
                        padding: '16px 24px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--text-secondary)',
                      }}
                    >
                      CREATED
                    </th>
                    <th
                      style={{
                        padding: '16px 24px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        color: 'var(--text-secondary)',
                        textAlign: 'right',
                      }}
                    >
                      ACTION
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {ticketedFindings.map((finding) => (
                    <tr
                      key={finding.id}
                      style={{
                        borderBottom: '1px solid var(--border-color)',
                        transition: 'background-color 0.2s',
                      }}
                      className="table-row-hover"
                    >
                      <td style={{ padding: '16px 24px' }}>
                        <SeverityBadge severity={finding.severity} />
                      </td>
                      <td style={{ padding: '16px 24px' }}>
                        <span
                          style={{
                            fontSize: '0.72rem',
                            background: 'rgba(56, 189, 248, 0.1)',
                            color: '#38bdf8',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontWeight: 700,
                          }}
                        >
                          OPEN
                        </span>
                      </td>
                      <td
                        style={{
                          padding: '16px 24px',
                          fontSize: '0.88rem',
                          fontWeight: 600,
                          color: 'var(--text-primary)',
                        }}
                      >
                        {finding.title}
                      </td>
                      <td
                        style={{
                          padding: '16px 24px',
                          fontSize: '0.8rem',
                          color: 'var(--text-muted)',
                        }}
                      >
                        {formattedDate}
                      </td>
                      <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                        <button
                          className="btn btn-secondary"
                          onClick={() => handleViewTicket(finding.ticket_id!)}
                          style={{
                            padding: '6px 12px',
                            fontSize: '0.75rem',
                            borderRadius: '4px',
                          }}
                        >
                          Open Ticket
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'debug' && showDebug && (
        <DeveloperDebugPanel reviewData={reviewData} />
      )}
    </div>
  );
};
export default ReviewResults;
