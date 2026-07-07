import * as React from 'react';
import { MetricCard } from './MetricCard';
import { SkeletonCard } from '../shared/SkeletonCard';

export interface DashboardMetrics {
  reviews_count: number;
  completed_reviews: number;
  open_tickets: number;
  critical_findings: number;
  average_quality: number;
  language_distribution: Record<string, number>;
}

interface DashboardStatsProps {
  metrics: DashboardMetrics | null;
  loading: boolean;
}

export const DashboardStats: React.FC<DashboardStatsProps> = ({
  metrics,
  loading,
}) => {
  if (loading) {
    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px',
        }}
      >
        <SkeletonCard variant="metric" count={5} />
      </div>
    );
  }

  if (!metrics) return null;

  // Format languages count and description
  const languagesCount = Object.keys(metrics.language_distribution).length;
  const topLanguages = Object.entries(metrics.language_distribution)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([lang]) => lang.charAt(0).toUpperCase() + lang.slice(1))
    .join(', ');

  const langDesc =
    languagesCount > 0
      ? `${languagesCount} lang(s) (${topLanguages || 'None'})`
      : 'No languages reviewed';

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
      }}
    >
      <MetricCard
        title="Reviews"
        value={metrics.reviews_count}
        icon="📊"
        description={`${metrics.completed_reviews} completed reviews`}
      />
      <MetricCard
        title="Average Quality"
        value={`${metrics.average_quality}%`}
        icon="⭐"
        description="Average quality rating"
      />
      <MetricCard
        title="Open Tickets"
        value={metrics.open_tickets}
        icon="🎫"
        description="Active engineering tickets"
      />
      <MetricCard
        title="Critical Findings"
        value={metrics.critical_findings}
        icon="⚠️"
        description="High risk violations"
      />
      <MetricCard
        title="Languages Reviewed"
        value={languagesCount}
        icon="🌐"
        description={langDesc}
      />
    </div>
  );
};
export default DashboardStats;
