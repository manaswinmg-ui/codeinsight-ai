import React, { useState, useEffect } from 'react';
import { RepositoryUploadPage } from '../../components/repository/RepositoryUploadPage';
import { RepositoryProgress } from '../../components/repository/RepositoryProgress';
import { RepositoryStatistics } from '../../components/repository/RepositoryStatistics';
import { RepositorySummaryCard } from '../../components/repository/RepositorySummaryCard';
import { RepositoryFileTable } from '../../components/repository/RepositoryFileTable';

interface RepositoryListItem {
  id: number;
  name: string;
  status: string;
  overall_quality: number | null;
  created_at: string;
}

interface RepositoryDetail {
  id: number;
  name: string;
  status: string;
  created_at: string;
  updated_at: string;
  language_summary: Record<string, number>;
  overall_quality: number;
  summary: string;
  files_analyzed: number;
  critical_findings: number;
  open_tickets: number;
  duration_seconds: number | null;
  files: Array<{
    id: number;
    file_path: string;
    language: string;
    status: string;
    quality_score: number;
    findings_count: number;
    tickets_count: number;
  }>;
  largest_files: Array<{ file_path: string; size_bytes: number }>;
  most_problematic_files: Array<{
    file_path: string;
    findings_count: number;
    quality_score: number;
  }>;
}

interface RepositoryDashboardProps {
  onSelectReview: (reviewId: number) => void;
}

export const RepositoryDashboard: React.FC<RepositoryDashboardProps> = ({
  onSelectReview,
}) => {
  const [repoList, setRepoList] = useState<RepositoryListItem[]>([]);
  const [activeRepoId, setActiveRepoId] = useState<number | null>(null);
  const [repoDetail, setRepoDetail] = useState<RepositoryDetail | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getBaseUrl = () => {
    return window.location.origin.includes('5173')
      ? 'http://localhost:8000'
      : '';
  };

  const fetchRepoList = async () => {
    setLoadingList(true);
    try {
      const response = await fetch(
        `${getBaseUrl()}/api/v1/repositories?page=1&limit=50`
      );
      if (!response.ok) throw new Error('Failed to load repositories logs.');
      const data = await response.json();
      setRepoList(data.items || []);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to sync repositories logs.');
    } finally {
      setLoadingList(false);
    }
  };

  const fetchRepoDetail = async (id: number) => {
    setLoadingDetail(true);
    try {
      const response = await fetch(`${getBaseUrl()}/api/v1/repositories/${id}`);
      if (!response.ok) throw new Error('Failed to fetch repository details.');
      const data = await response.json();
      setRepoDetail(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch details.');
    } finally {
      setLoadingDetail(false);
    }
  };

  // Load initial list on mount
  useEffect(() => {
    fetchRepoList();
  }, []);

  // Polling setup for active PENDING or PROCESSING repository
  useEffect(() => {
    if (activeRepoId === null) return;

    fetchRepoDetail(activeRepoId);

    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `${getBaseUrl()}/api/v1/repositories/${activeRepoId}`
        );
        if (response.ok) {
          const data: RepositoryDetail = await response.json();
          setRepoDetail(data);

          if (data.status !== 'PENDING' && data.status !== 'PROCESSING') {
            clearInterval(interval);
            // Refresh the sidebar logs list in background
            fetchRepoList();
          }
        }
      } catch (err) {
        console.error('Error polling repo status:', err);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [activeRepoId]);

  const handleUploadSuccess = (newRepoId: number) => {
    setShowUpload(false);
    setActiveRepoId(newRepoId);
  };

  const handleBackToList = () => {
    setActiveRepoId(null);
    setRepoDetail(null);
    setShowUpload(false);
    fetchRepoList();
  };

  // Render 1: Active Upload View
  if (showUpload) {
    return (
      <div>
        <button
          onClick={handleBackToList}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--accent-color)',
            fontSize: '0.95rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontWeight: 600,
            marginBottom: '20px',
          }}
        >
          ← Back to Repositories
        </button>
        <RepositoryUploadPage onUploadSuccess={handleUploadSuccess} />
      </div>
    );
  }

  // Render 2: Active Repository Analysis (Polling)
  if (activeRepoId !== null) {
    if (loadingDetail && !repoDetail) {
      return (
        <div
          style={{
            padding: '40px',
            textAlign: 'center',
            color: 'var(--text-secondary)',
          }}
        >
          Loading repository details...
        </div>
      );
    }
    if (!repoDetail) return null;
    const isProcessing =
      repoDetail.status === 'PENDING' || repoDetail.status === 'PROCESSING';

    if (isProcessing) {
      return (
        <div>
          <RepositoryProgress
            repoName={repoDetail.name}
            onBackToHistory={handleBackToList}
          />
        </div>
      );
    }

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px',
          }}
        >
          <div>
            <button
              onClick={handleBackToList}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--accent-color)',
                fontSize: '0.9rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontWeight: 600,
                marginBottom: '12px',
                padding: 0,
              }}
            >
              ← Back to Repositories
            </button>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>
              {repoDetail.name}
            </h1>
            <p
              style={{
                color: 'var(--text-secondary)',
                fontSize: '0.85rem',
                marginTop: '6px',
                margin: 0,
              }}
            >
              Analyzed on {new Date(repoDetail.created_at).toLocaleString()}
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.8rem',
                fontWeight: 700,
                background:
                  repoDetail.status === 'COMPLETED'
                    ? 'rgba(16, 185, 129, 0.15)'
                    : 'rgba(239, 68, 68, 0.15)',
                color:
                  repoDetail.status === 'COMPLETED'
                    ? 'var(--success-color)'
                    : 'var(--danger-color)',
              }}
            >
              {repoDetail.status}
            </span>

            <button
              onClick={() => setShowUpload(true)}
              style={{
                background: 'var(--accent-color)',
                color: '#fff',
                border: 'none',
                padding: '10px 18px',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.25s',
                boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-1px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'none';
              }}
            >
              📦 Scan Another
            </button>
          </div>
        </div>

        {/* Aggregate Statistics */}
        <RepositoryStatistics
          filesCount={repoDetail.files_analyzed}
          criticalCount={repoDetail.critical_findings}
          ticketsCount={repoDetail.open_tickets}
          duration={repoDetail.duration_seconds}
        />

        {/* Score and Summary charts */}
        <RepositorySummaryCard
          qualityScore={repoDetail.overall_quality}
          languages={repoDetail.language_summary}
          summaryText={repoDetail.summary}
        />

        {/* Main Files Table */}
        <RepositoryFileTable
          files={repoDetail.files}
          onSelectFileReview={onSelectReview}
          largestFiles={repoDetail.largest_files}
          problematicFiles={repoDetail.most_problematic_files}
        />
      </div>
    );
  }

  // Render 3: Repository Logs List Page
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>
            Repository Analysis Logs
          </h1>
          <p
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
              marginTop: '6px',
              margin: 0,
            }}
          >
            Review, aggregate, and audit quality insights for entire software
            projects.
          </p>
        </div>

        <button
          onClick={() => setShowUpload(true)}
          style={{
            background: 'var(--accent-color)',
            color: '#fff',
            border: 'none',
            padding: '10px 18px',
            borderRadius: '8px',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.25s',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.2)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'none';
          }}
        >
          📦 Scan Repository
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: '12px 16px',
            background: 'rgba(239, 68, 68, 0.1)',
            color: 'var(--danger-color)',
            borderRadius: '8px',
            fontSize: '0.9rem',
            fontWeight: 600,
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {/* List Table */}
      <div
        style={{
          background: 'var(--card-bg)',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: 'var(--card-shadow)',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        {loadingList ? (
          <div
            style={{
              padding: '40px',
              textAlign: 'center',
              color: 'var(--text-secondary)',
            }}
          >
            Loading codebase logs...
          </div>
        ) : repoList.length === 0 ? (
          <div style={{ padding: '60px 40px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📦</div>
            <p
              style={{
                fontWeight: 600,
                fontSize: '1.1rem',
                marginBottom: '8px',
              }}
            >
              No scanned repositories yet
            </p>
            <p
              style={{
                color: 'var(--text-secondary)',
                fontSize: '0.9rem',
                marginBottom: '20px',
              }}
            >
              Upload your codebase in a ZIP format to evaluate files and detect
              critical engineering issues.
            </p>
            <button
              onClick={() => setShowUpload(true)}
              style={{
                background: 'rgba(99, 102, 241, 0.15)',
                color: 'var(--accent-color)',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '8px',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Scan Your First Codebase
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
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
                    borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                    color: 'var(--text-secondary)',
                    fontSize: '0.82rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                  }}
                >
                  <th style={{ padding: '12px 16px' }}>Repository Name</th>
                  <th style={{ padding: '12px 16px' }}>Uploaded At</th>
                  <th style={{ padding: '12px 16px' }}>Overall Quality</th>
                  <th style={{ padding: '12px 16px' }}>Status</th>
                  <th style={{ padding: '12px 16px', textAlign: 'right' }}>
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {repoList.map((repo) => {
                  const qualityColor =
                    repo.overall_quality !== null
                      ? repo.overall_quality >= 80
                        ? 'var(--success-color)'
                        : repo.overall_quality >= 50
                          ? '#f59e0b'
                          : 'var(--danger-color)'
                      : 'var(--text-secondary)';

                  return (
                    <tr
                      key={repo.id}
                      style={{
                        borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                        fontSize: '0.9rem',
                        transition: 'background 0.2s',
                        cursor: 'pointer',
                      }}
                      onClick={() => setActiveRepoId(repo.id)}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background =
                          'rgba(255, 255, 255, 0.02)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'transparent';
                      }}
                    >
                      <td
                        style={{
                          padding: '16px',
                          fontWeight: 600,
                          color: 'var(--text-primary)',
                        }}
                      >
                        📁 {repo.name}
                      </td>
                      <td
                        style={{
                          padding: '16px',
                          color: 'var(--text-secondary)',
                        }}
                      >
                        {new Date(repo.created_at).toLocaleString()}
                      </td>
                      <td
                        style={{
                          padding: '16px',
                          fontWeight: 700,
                          color: qualityColor,
                        }}
                      >
                        {repo.overall_quality !== null
                          ? `${repo.overall_quality}/100`
                          : '-'}
                      </td>
                      <td style={{ padding: '16px' }}>
                        <span
                          style={{
                            padding: '3px 8px',
                            borderRadius: '6px',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            background:
                              repo.status === 'COMPLETED'
                                ? 'rgba(16, 185, 129, 0.1)'
                                : repo.status === 'PROCESSING'
                                  ? 'rgba(99, 102, 241, 0.1)'
                                  : 'rgba(239, 68, 68, 0.1)',
                            color:
                              repo.status === 'COMPLETED'
                                ? 'var(--success-color)'
                                : repo.status === 'PROCESSING'
                                  ? 'var(--accent-color)'
                                  : 'var(--danger-color)',
                          }}
                        >
                          {repo.status}
                        </span>
                      </td>
                      <td
                        style={{ padding: '16px', textAlign: 'right' }}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={() => setActiveRepoId(repo.id)}
                          style={{
                            background: 'rgba(255,255,255,0.05)',
                            color: 'var(--text-primary)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            padding: '6px 12px',
                            borderRadius: '6px',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background =
                              'rgba(255,255,255,0.1)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background =
                              'rgba(255,255,255,0.05)';
                          }}
                        >
                          Open Dashboard
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
