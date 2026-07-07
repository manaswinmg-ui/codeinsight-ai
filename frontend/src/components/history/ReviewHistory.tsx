import * as React from 'react';
import { useEffect, useState } from 'react';
import { useToast } from '../shared/ToastProvider';

export interface HistoryItem {
  id: number;
  language: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  created_at: string;
}

interface ReviewHistoryProps {
  onSelectReview: (id: number) => void;
  activeReviewId: number | null;
  currentLoadedId: number | null;
}

export const ReviewHistory: React.FC<ReviewHistoryProps> = ({
  onSelectReview,
  activeReviewId,
  currentLoadedId,
}) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const { addToast } = useToast();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const baseUrl = window.location.origin.includes('5173')
        ? 'http://localhost:8000'
        : '';
      const response = await fetch(`${baseUrl}/api/v1/reviews`);
      if (!response.ok) {
        throw new Error('Failed to retrieve history');
      }
      const data = await response.json();
      const items = Array.isArray(data) ? data : data?.items || [];
      setHistory(items);
    } catch (err) {
      console.error(err);
      addToast('Could not load review history list.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
     
  }, [activeReviewId]); // Re-fetch history when a new review starts or completes

  const formatShortDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'var(--success-color)';
      case 'FAILED':
        return 'var(--danger-color)';
      case 'PROCESSING':
      case 'PENDING':
        return 'var(--warning-color)';
      default:
        return 'var(--text-muted)';
    }
  };

  if (collapsed) {
    return (
      <div
        className="sidebar-container sidebar-collapsed"
        style={{
          width: '50px',
          background: 'rgba(18, 19, 26, 0.8)',
          borderRight: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: '16px 0',
          gap: '24px',
          transition: 'width 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
        }}
      >
        <button
          onClick={() => setCollapsed(false)}
          title="Expand Sidebar"
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            fontSize: '1.2rem',
          }}
        >
          ➡️
        </button>
        <div
          style={{
            writingMode: 'vertical-rl',
            transform: 'rotate(180deg)',
            color: 'var(--text-muted)',
            fontSize: '0.8rem',
            fontWeight: 700,
            letterSpacing: '2px',
          }}
        >
          HISTORY
        </div>
      </div>
    );
  }

  return (
    <div
      className="sidebar-container sidebar-expanded"
      style={{
        width: '280px',
        background: 'rgba(18, 19, 26, 0.5)',
        borderRight: '1px solid var(--border-color)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        transition: 'width 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      {/* Sidebar Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-color)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '1.1rem' }}>📜</span>
          <span
            style={{
              fontWeight: 800,
              fontSize: '0.9rem',
              letterSpacing: '0.5px',
              color: 'var(--text-primary)',
            }}
          >
            Review History
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={fetchHistory}
            disabled={loading}
            title="Refresh list"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              fontSize: '0.95rem',
            }}
          >
            🔄
          </button>
          <button
            onClick={() => setCollapsed(true)}
            title="Collapse Sidebar"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.95rem',
            }}
          >
            ⬅️
          </button>
        </div>
      </div>

      {/* Sidebar Items */}
      <div
        style={{
          flexGrow: 1,
          overflowY: 'auto',
          padding: '12px 10px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        {loading && history.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.8rem',
              padding: '24px 0',
            }}
          >
            Loading reviews...
          </div>
        ) : history.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.8rem',
              padding: '24px 0',
              lineHeight: '1.4',
            }}
          >
            No reviews yet.
            <br />
            Submit your first file!
          </div>
        ) : (
          history.map((item) => {
            const isActive = currentLoadedId === item.id;
            return (
              <div
                key={item.id}
                onClick={() => onSelectReview(item.id)}
                style={{
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: isActive
                    ? 'rgba(99, 102, 241, 0.08)'
                    : 'transparent',
                  border: isActive
                    ? '1px solid rgba(99, 102, 241, 0.3)'
                    : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background =
                      'rgba(255, 255, 255, 0.02)';
                    e.currentTarget.style.borderColor =
                      'rgba(255, 255, 255, 0.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = 'transparent';
                    e.currentTarget.style.borderColor = 'transparent';
                  }
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span
                    style={{
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      color: 'var(--text-primary)',
                    }}
                  >
                    Review #{item.id}
                  </span>
                  <span
                    style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: getStatusColor(item.status),
                      display: 'inline-block',
                    }}
                    title={item.status}
                  />
                </div>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)',
                  }}
                >
                  <span
                    style={{ textTransform: 'capitalize', fontWeight: 600 }}
                  >
                    {item.language}
                  </span>
                  <span>{formatShortDate(item.created_at)}</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
