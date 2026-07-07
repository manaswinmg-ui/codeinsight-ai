import * as React from 'react';

interface ReviewTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  showDebug: boolean;
}

export const ReviewTabs: React.FC<ReviewTabsProps> = ({
  activeTab,
  onTabChange,
  showDebug,
}) => {
  const tabs = [
    { id: 'overview', label: '📊 Overview' },
    { id: 'code', label: '💻 Source Code' },
    { id: 'findings', label: '🔎 Findings' },
    { id: 'tickets', label: '🎫 Tickets' },
  ];

  if (showDebug) {
    tabs.push({ id: 'debug', label: '⚙️ Debug (Dev)' });
  }

  return (
    <div
      style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        gap: '4px',
        paddingBottom: '0.2px',
        marginBottom: '20px',
      }}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            style={{
              padding: '12px 20px',
              background: 'transparent',
              border: 'none',
              color: isActive ? 'var(--accent-color)' : 'var(--text-secondary)',
              fontWeight: 600,
              fontSize: '0.92rem',
              cursor: 'pointer',
              position: 'relative',
              transition: 'color 0.2s',
            }}
          >
            {tab.label}
            {isActive && (
              <div
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  height: '2px',
                  background: 'var(--accent-color)',
                  boxShadow: '0 0 8px var(--accent-glow)',
                }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
};
