import * as React from 'react';

export interface FilterState {
  status: string;
  language: string;
  qualityRange: string;
  criticalOnly: boolean;
  hasTickets: string; // 'all' | 'true' | 'false'
}

interface FilterSidebarProps {
  filters: FilterState;
  onFiltersChange: (updater: (prev: FilterState) => FilterState) => void;
  onReset: () => void;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({
  filters,
  onFiltersChange,
  onReset,
}) => {
  const updateField = (key: keyof FilterState, value: string | boolean) => {
    onFiltersChange((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
    <div
      className="glass-card"
      style={{
        width: '280px',
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        padding: '24px',
        alignSelf: 'flex-start',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>🛠️ Filters</h3>
        <button
          onClick={onReset}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--accent-color)',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          Reset All
        </button>
      </div>

      {/* Filter by Status */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>Status</span>
        <select
          value={filters.status}
          onChange={(e) => updateField('status', e.target.value)}
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '8px 12px',
            color: '#fff',
            cursor: 'pointer',
            fontSize: '0.9rem',
          }}
        >
          <option value="">All Statuses</option>
          <option value="COMPLETED">Completed</option>
          <option value="PROCESSING">Processing</option>
          <option value="FAILED">Failed</option>
          <option value="PENDING">Pending</option>
        </select>
      </div>

      {/* Filter by Language */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>Language</span>
        <select
          value={filters.language}
          onChange={(e) => updateField('language', e.target.value)}
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '8px 12px',
            color: '#fff',
            cursor: 'pointer',
            fontSize: '0.9rem',
          }}
        >
          <option value="">All Languages</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="typescript">TypeScript</option>
          <option value="go">Go</option>
          <option value="java">Java</option>
          <option value="c++">C++</option>
          <option value="c#">C#</option>
        </select>
      </div>

      {/* Filter by Quality Score */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>Quality Score Range</span>
        <select
          value={filters.qualityRange}
          onChange={(e) => updateField('qualityRange', e.target.value)}
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '8px 12px',
            color: '#fff',
            cursor: 'pointer',
            fontSize: '0.9rem',
          }}
        >
          <option value="">All Scores</option>
          <option value="0-50">Poor (0–50)</option>
          <option value="51-70">Fair (51–70)</option>
          <option value="71-90">Good (71–90)</option>
          <option value="91-100">Excellent (91–100)</option>
        </select>
      </div>

      {/* Filter by Tickets */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>Ticket Linkage</span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {[
            { id: 'all', label: 'All' },
            { id: 'true', label: 'Has Filed Tickets' },
            { id: 'false', label: 'No Filed Tickets' },
          ].map((opt) => (
            <label key={opt.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', cursor: 'pointer' }}>
              <input
                type="radio"
                name="hasTickets"
                value={opt.id}
                checked={filters.hasTickets === opt.id}
                onChange={() => updateField('hasTickets', opt.id)}
                style={{ cursor: 'pointer' }}
              />
              {opt.label}
            </label>
          ))}
        </div>
      </div>

      {/* Toggle by Critical Findings */}
      <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={filters.criticalOnly}
            onChange={(e) => updateField('criticalOnly', e.target.checked)}
            style={{ width: '16px', height: '16px', cursor: 'pointer' }}
          />
          <span style={{ fontWeight: 600 }}>⚠️ Critical Issues Only</span>
        </label>
      </div>
    </div>
  );
};
