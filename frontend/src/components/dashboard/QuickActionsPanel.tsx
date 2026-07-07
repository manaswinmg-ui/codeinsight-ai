import * as React from 'react';

type Page = 'dashboard' | 'new-review' | 'history' | 'repository';

interface QuickActionsPanelProps {
  onNavigate: (page: Page) => void;
}

export const QuickActionsPanel: React.FC<QuickActionsPanelProps> = ({
  onNavigate,
}) => {
  return (
    <div
      className="glass-card"
      style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
    >
      <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>
        ⚡ Quick Actions
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <button
          className="btn"
          onClick={() => onNavigate('repository')}
          style={{
            width: '100%',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '0.92rem',
          }}
        >
          <span>📦</span> Scan Codebase
        </button>
        <button
          className="btn"
          onClick={() => onNavigate('new-review')}
          style={{
            width: '100%',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '0.92rem',
            background: 'rgba(255, 255, 255, 0.05)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
          }}
        >
          <span>✨</span> Single-file Review
        </button>
        <button
          className="btn"
          onClick={() => onNavigate('history')}
          style={{
            width: '100%',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '0.92rem',
            background: 'rgba(255, 255, 255, 0.05)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
          }}
        >
          <span>🕒</span> Review History
        </button>
        <button
          className="btn"
          onClick={() => onNavigate('history')}
          style={{
            width: '100%',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            fontSize: '0.92rem',
            background: 'rgba(255, 255, 255, 0.05)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)',
          }}
        >
          <span>🎫</span> Open Tickets
        </button>
      </div>
    </div>
  );
};
export default QuickActionsPanel;
