import * as React from 'react';

interface SearchToolbarProps {
  search: string;
  onSearchChange: (val: string) => void;
  sortBy: string;
  onSortByChange: (val: string) => void;
  selectedCount: number;
  onCompare: () => void;
}

export const SearchToolbar: React.FC<SearchToolbarProps> = ({
  search,
  onSearchChange,
  sortBy,
  onSortByChange,
  selectedCount,
  onCompare,
}) => {
  return (
    <div
      className="glass-card"
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '16px',
        padding: '16px 24px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          flexGrow: 1,
          minWidth: '240px',
        }}
      >
        <span style={{ fontSize: '1.2rem' }}>🔍</span>
        <input
          type="text"
          placeholder="Search by ID, language, ticket, rule title, or keywords..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          style={{
            flexGrow: 1,
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            padding: '10px 14px',
            color: '#fff',
            fontSize: '0.95rem',
            outline: 'none',
          }}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Sort By:
          </span>
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            style={{
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '8px 12px',
              color: '#fff',
              cursor: 'pointer',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="highest_quality">Highest Quality</option>
            <option value="lowest_quality">Lowest Quality</option>
            <option value="most_findings">Most Findings</option>
            <option value="least_findings">Least Findings</option>
          </select>
        </div>

        {selectedCount === 2 ? (
          <button
            className="btn"
            onClick={onCompare}
            style={{
              padding: '8px 16px',
              fontSize: '0.9rem',
              animation: 'pulse 2s infinite',
            }}
          >
            ⚔️ Compare (2 selected)
          </button>
        ) : (
          <button
            className="btn"
            disabled
            style={{
              padding: '8px 16px',
              fontSize: '0.9rem',
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-muted)',
              border: '1px solid var(--border-color)',
              cursor: 'not-allowed',
            }}
          >
            Select 2 to Compare
          </button>
        )}
      </div>
    </div>
  );
};
