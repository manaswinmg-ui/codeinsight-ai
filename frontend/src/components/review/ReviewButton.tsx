import * as React from 'react';

interface ReviewButtonProps {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
}

export const ReviewButton: React.FC<ReviewButtonProps> = ({
  onClick,
  disabled,
  loading,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="btn"
      style={{
        width: '100%',
        justifyContent: 'center',
        padding: '12px 24px',
        fontSize: '1.05rem',
        fontWeight: 700,
        height: '48px',
      }}
    >
      {loading ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            className="pulse-indicator"
            style={{ animationDuration: '0.8s' }}
          ></span>
          Analyzing Code...
        </div>
      ) : (
        'Review Code'
      )}
    </button>
  );
};
