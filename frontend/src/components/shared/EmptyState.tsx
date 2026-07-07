import * as React from 'react';

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  actionLabel,
  onAction,
  icon = '📂',
}) => {
  return (
    <div
      className="glass-card"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 24px',
        textAlign: 'center',
        border: '1px dashed var(--border-color)',
        background: 'rgba(255, 255, 255, 0.005)',
        borderRadius: '16px',
        minHeight: '240px',
      }}
    >
      <span
        style={{
          fontSize: '3.5rem',
          marginBottom: '16px',
          filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))',
        }}
      >
        {icon}
      </span>
      <h3
        style={{
          margin: '0 0 8px 0',
          fontSize: '1.25rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
        }}
      >
        {title}
      </h3>
      <p
        style={{
          margin: '0 0 24px 0',
          fontSize: '0.9rem',
          color: 'var(--text-secondary)',
          maxWidth: '400px',
          lineHeight: '1.5',
        }}
      >
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          className="btn"
          onClick={onAction}
          style={{
            padding: '10px 20px',
            fontSize: '0.9rem',
            fontWeight: 600,
            borderRadius: '8px',
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
