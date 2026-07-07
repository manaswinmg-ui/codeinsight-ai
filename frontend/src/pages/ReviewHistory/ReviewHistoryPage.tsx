import * as React from 'react';
import { useState, useEffect } from 'react';
import { SearchToolbar } from '../../components/history/SearchToolbar';
import {
  FilterSidebar,
  FilterState,
} from '../../components/history/FilterSidebar';
import { ReviewTable } from '../../components/history/ReviewTable';
import { Pagination } from '../../components/history/Pagination';
import {
  ComparisonModal,
  ReviewComparison,
} from '../../components/modals/ComparisonModal';
import { ReviewSummary } from '../../components/dashboard/RecentReviewsPanel';

interface ReviewHistoryPageProps {
  onSelectReview: (id: number) => void;
}

export const ReviewHistoryPage: React.FC<ReviewHistoryPageProps> = ({
  onSelectReview,
}) => {
  const [reviews, setReviews] = useState<ReviewSummary[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  const [filters, setFilters] = useState<FilterState>({
    status: '',
    language: '',
    qualityRange: '',
    criticalOnly: false,
    hasTickets: 'all',
  });

  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparison, setComparison] = useState<ReviewComparison | null>(null);
  const [showComparison, setShowComparison] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingComparison, setLoadingComparison] = useState(false);

  // Debounced search trigger could be added, but a simple effect listening to search works too
  const fetchReviews = async () => {
    setLoading(true);
    const baseUrl = window.location.origin.includes('5173')
      ? 'http://localhost:8000'
      : '';

    // Build query params
    const params = new URLSearchParams();
    params.append('page', currentPage.toString());
    params.append('limit', '8'); // Paginate in blocks of 8 items
    params.append('sort_by', sortBy);

    if (search.trim()) {
      params.append('search', search.trim());
    }
    if (filters.status) {
      params.append('status', filters.status);
    }
    if (filters.language) {
      params.append('language', filters.language);
    }
    if (filters.criticalOnly) {
      params.append('critical_only', 'true');
    }
    if (filters.hasTickets !== 'all') {
      params.append('has_tickets', filters.hasTickets);
    }

    // Quality Range
    if (filters.qualityRange) {
      const [min, max] = filters.qualityRange.split('-');
      params.append('quality_min', min);
      params.append('quality_max', max);
    }

    try {
      const response = await fetch(
        `${baseUrl}/api/v1/reviews?${params.toString()}`
      );
      if (!response.ok) throw new Error('Failed to load review history logs.');
      const data = await response.json();
      setReviews(data.items || []);
      setTotalPages(data.pages || 1);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReviews();
     
  }, [currentPage, search, sortBy, filters]);

  // Reset page to 1 when filters or search change
  useEffect(() => {
    setCurrentPage(1);
  }, [search, filters]);

  const handleToggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((x) => x !== id);
      }
      if (prev.length >= 2) return prev;
      return [...prev, id];
    });
  };

  const handleCompare = async () => {
    if (selectedIds.length !== 2) return;
    setLoadingComparison(true);
    setShowComparison(true);

    const baseUrl = window.location.origin.includes('5173')
      ? 'http://localhost:8000'
      : '';

    try {
      // Order left_review_id as the older/smaller ID, right_review_id as the newer/larger ID
      const ordered = [...selectedIds].sort((a, b) => a - b);
      const response = await fetch(`${baseUrl}/api/v1/reviews/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          left_review_id: ordered[0],
          right_review_id: ordered[1],
        }),
      });

      if (!response.ok) throw new Error('Comparison calculation failed.');
      const data = await response.json();
      setComparison(data);
    } catch (err) {
      console.error(err);
      setShowComparison(false);
    } finally {
      setLoadingComparison(false);
    }
  };

  const handleResetFilters = () => {
    setFilters({
      status: '',
      language: '',
      qualityRange: '',
      criticalOnly: false,
      hasTickets: 'all',
    });
    setSearch('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Search & Action Bar */}
      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        sortBy={sortBy}
        onSortByChange={setSortBy}
        selectedCount={selectedIds.length}
        onCompare={handleCompare}
      />

      {/* Main Workspace Layout (Sidebar + Grid Table) */}
      <div style={{ display: 'flex', gap: '24px', alignItems: 'stretch' }}>
        <FilterSidebar
          filters={filters}
          onFiltersChange={setFilters}
          onReset={handleResetFilters}
        />

        <div
          style={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: '20px',
            minWidth: 0,
          }}
        >
          <ReviewTable
            reviews={reviews}
            loading={loading}
            selectedIds={selectedIds}
            onToggleSelect={handleToggleSelect}
            onSelectReview={onSelectReview}
          />

          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </div>
      </div>

      {/* Comparison Modal popover */}
      {showComparison && (
        <ComparisonModal
          comparison={comparison}
          loading={loadingComparison}
          onClose={() => {
            setShowComparison(false);
            setComparison(null);
          }}
        />
      )}
    </div>
  );
};
