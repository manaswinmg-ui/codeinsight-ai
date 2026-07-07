import * as React from 'react';
import { ReviewDetail } from '../../pages/ReviewWorkspace';
import { ReviewResults } from '../review/ReviewResults';

interface FindingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  reviewData: ReviewDetail | null;
  status: 'idle' | 'processing' | 'success' | 'error';
  setReviewData?: React.Dispatch<React.SetStateAction<ReviewDetail | null>>;
  showDebug: boolean;
}

export const FindingsModal: React.FC<FindingsModalProps> = ({
  isOpen,
  onClose,
  reviewData,
  status,
  setReviewData,
  showDebug,
}) => {
  if (!isOpen || !reviewData) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(8px)',
        zIndex: 990,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }}
      onClick={onClose}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '1000px',
          maxHeight: '90vh',
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-focus)',
          padding: '32px',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid var(--border-color)',
            paddingBottom: '16px',
          }}
        >
          <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 800 }} className="gradient-text">
            🔎 Code Review Findings — #{reviewData.id}
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '1.8rem',
              cursor: 'pointer',
              padding: '4px 12px',
              borderRadius: '6px',
              lineHeight: 1,
            }}
          >
            ×
          </button>
        </div>

        {/* Modal Content - Review Results with Tabbed Layout */}
        <ReviewResults
          status={status}
          reviewData={reviewData}
          setReviewData={setReviewData}
          showDebug={showDebug}
        />

        {/* Modal Footer */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            className="btn btn-secondary"
            onClick={onClose}
            style={{
              padding: '8px 20px',
              fontSize: '0.95rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Close Findings
          </button>
        </div>
      </div>
    </div>
  );
};
