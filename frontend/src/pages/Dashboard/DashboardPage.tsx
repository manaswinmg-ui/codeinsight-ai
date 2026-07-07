import React, { useState, useEffect } from 'react';
import { DashboardStats, DashboardMetrics } from '../../components/dashboard/DashboardStats';
import { QuickActionsPanel } from '../../components/dashboard/QuickActionsPanel';
import { RecentReviewsPanel, ReviewSummary } from '../../components/dashboard/RecentReviewsPanel';
import { RecentTicketsPanel, TicketSummary } from '../../components/dashboard/RecentTicketsPanel';

type Page = 'dashboard' | 'new-review' | 'history' | 'repository';

interface DashboardPageProps {
  onNavigate: (page: Page) => void;
  onSelectReview: (reviewId: number) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigate,
  onSelectReview,
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [reviews, setReviews] = useState<ReviewSummary[]>([]);
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [loadingMetrics, setLoadingMetrics] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [loadingTickets, setLoadingTickets] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    const baseUrl = window.location.origin.includes('5173')
      ? 'http://localhost:8000'
      : '';

    // Parallel fetch for dashboard data
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${baseUrl}/api/v1/dashboard/metrics`);
        if (!response.ok) throw new Error('Failed to load metrics');
        const data = await response.json();
        setMetrics(data);
      } catch (err) {
        console.error(err);
        setError('Could not sync workspace metrics.');
      } finally {
        setLoadingMetrics(false);
      }
    };

    const fetchReviews = async () => {
      try {
        const response = await fetch(`${baseUrl}/api/v1/dashboard/recent-reviews?limit=5`);
        if (!response.ok) throw new Error('Failed to load recent reviews');
        const data = await response.json();
        setReviews(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingReviews(false);
      }
    };

    const fetchTickets = async () => {
      try {
        const response = await fetch(`${baseUrl}/api/v1/dashboard/recent-tickets?limit=5`);
        if (!response.ok) throw new Error('Failed to load recent tickets');
        const data = await response.json();
        setTickets(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingTickets(false);
      }
    };

    await Promise.all([fetchMetrics(), fetchReviews(), fetchTickets()]);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Metrics Row */}
      <section>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '1.2rem', color: 'var(--text-secondary)' }}>
          Workspace Metrics
        </h2>
        {error && (
          <div
            style={{
              background: 'rgba(239, 68, 68, 0.1)',
              color: 'var(--danger-color)',
              padding: '12px 16px',
              borderRadius: '8px',
              marginBottom: '16px',
              fontSize: '0.9rem',
              fontWeight: 600,
            }}
          >
            ⚠️ {error}
          </div>
        )}
        <DashboardStats metrics={metrics} loading={loadingMetrics} />
      </section>

      {/* Main Grid: Left Side is Tables, Right Side is Quick Actions */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '24px',
          alignItems: 'stretch',
        }}
      >
        {/* Lists Column */}
        <div
          style={{
            flex: '2 1 600px',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            minWidth: 0,
          }}
        >
          <RecentReviewsPanel
            reviews={reviews}
            loading={loadingReviews}
            onSelectReview={onSelectReview}
          />
          <RecentTicketsPanel
            tickets={tickets}
            loading={loadingTickets}
            onSelectReview={onSelectReview}
          />
        </div>

        {/* Quick Actions Column */}
        <div style={{ flex: '1 1 300px', alignSelf: 'flex-start' }}>
          <QuickActionsPanel onNavigate={onNavigate} />
        </div>
      </div>
    </div>
  );
};
