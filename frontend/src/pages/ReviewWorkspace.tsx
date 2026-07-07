import { useState, useEffect } from 'react';

import { CodeEditor } from '../components/review/CodeEditor';
import { FileUploader } from '../components/review/FileUploader';
import { LanguageSelector } from '../components/review/LanguageSelector';
import { ProcessingStatus } from '../components/review/ProcessingStatus';
import { ReviewButton } from '../components/review/ReviewButton';

import { FindingsModal } from '../components/modals/FindingsModal';

export interface Finding {
  id: number;
  title: string;
  description: string;
  severity: string;
  status: string;
  suggested_fix?: string | null;
  test_case_hint?: string | null;
  // Enhanced engineering metadata
  category?: string | null;
  confidence?: number | null;
  impact?: string | null;
  why_it_matters?: string | null;
  improved_code?: string | null;
  estimated_fix_time?: string | null;
  references?: string[] | null;
  ticket_id?: number | null;
  line_start?: number | null;
  line_end?: number | null;
}

export interface ReviewDetail {
  id: number;
  code: string;
  language: string;
  status: string;
  summary: string;
  quality_score: number;
  findings: Finding[];
  created_at: string;
}

interface ReviewWorkspaceProps {
  initialReviewId?: number | null;
  onClearInitialReviewId?: () => void;
  showDebug?: boolean;
}

export const ReviewWorkspace = ({
  initialReviewId,
  onClearInitialReviewId,
  showDebug,
}: ReviewWorkspaceProps) => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [fileName, setFileName] = useState<string | null>(null);
  const [status, setStatus] = useState<
    'idle' | 'processing' | 'success' | 'error'
  >('idle');
  const [currentStep, setCurrentStep] = useState(0);
  const [reviewData, setReviewData] = useState<ReviewDetail | null>(null);
  const [activeReviewId, setActiveReviewId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFindingsModalOpen, setIsFindingsModalOpen] = useState(false);

  // Automatically open the findings modal when a review finishes successfully
  useEffect(() => {
    if (status === 'success' && reviewData) {
      setIsFindingsModalOpen(true);
    }
  }, [status, reviewData]);

  // Poll review status when activeReviewId is set
  useEffect(() => {
    if (activeReviewId === null) return;

    let intervalId: ReturnType<typeof setInterval> | undefined = undefined;

    const poll = async () => {
      try {
        const response = await fetch(`/api/v1/reviews/${activeReviewId}`);
        if (!response.ok) {
          throw new Error(
            `Failed to fetch review status: ${response.statusText}`
          );
        }
        const data: ReviewDetail = await response.json();

        // Map status to steps
        if (data.status === 'PENDING') {
          setCurrentStep((prev) => Math.max(prev, 1));
        } else if (data.status === 'PROCESSING') {
          setCurrentStep((prev) => Math.max(prev, 2));
        } else if (data.status === 'COMPLETED') {
          clearInterval(intervalId);
          setReviewData(data);
          setCurrentStep(3);
          setStatus('success');
          setActiveReviewId(null);
        } else if (data.status === 'FAILED') {
          clearInterval(intervalId);
          setStatus('error');
          setError('Review processing failed on the server.');
          setActiveReviewId(null);
        }
      } catch (err) {
        clearInterval(intervalId);
        setStatus('error');
        setError(
          err instanceof Error
            ? err.message
            : 'An error occurred during status polling.'
        );
        setActiveReviewId(null);
      }
    };

    poll();
    intervalId = setInterval(poll, 2000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [activeReviewId]);

  const handleCodeUpload = (
    text: string,
    uploadedName: string,
    detectedLanguage?: string
  ) => {
    setCode(text);
    setFileName(uploadedName);
    if (detectedLanguage) {
      setLanguage(detectedLanguage);
    }
  };

  const handleClearFile = () => {
    setCode('');
    setFileName(null);
  };

  const handleStartReview = async () => {
    if (!code.trim()) {
      setError('Please provide some source code to analyze.');
      setStatus('error');
      return;
    }

    setStatus('processing');
    setCurrentStep(0);
    setReviewData(null);
    setActiveReviewId(null);
    setError(null);

    try {
      const response = await fetch('/api/v1/reviews', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Server returned error status: ${response.status}`
        );
      }

      const data = await response.json();
      setActiveReviewId(data.review_id);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'An unexpected error occurred.'
      );
      setStatus('error');
    }
  };

  const handleLoadReview = async (id: number) => {
    setStatus('processing');
    setCurrentStep(0);
    setReviewData(null);
    setError(null);
    try {
      const baseUrl = window.location.origin.includes('5173')
        ? 'http://localhost:8000'
        : '';
      const response = await fetch(`${baseUrl}/api/v1/reviews/${id}`);
      if (!response.ok) {
        throw new Error(`Failed to load review: ${response.statusText}`);
      }
      const data: ReviewDetail = await response.json();
      setCode(data.code);
      setLanguage(data.language);
      setReviewData(data);
      setStatus('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred.');
      setStatus('error');
    }
  };

  useEffect(() => {
    if (initialReviewId) {
      handleLoadReview(initialReviewId);
      if (onClearInitialReviewId) {
        onClearInitialReviewId();
      }
    }
     
  }, [initialReviewId]);

  return (
    <div className="workspace-container" style={{ minHeight: '85vh' }}>
      {/* Main Content Workspace */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '32px',
          minWidth: 0,
        }}
      >
        {/* Page Header */}
        <header
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <h1
              style={{ margin: 0, fontSize: '1.8rem', fontWeight: 800 }}
              className="gradient-text"
            >
              Review Workspace
            </h1>
            <p
              style={{
                margin: '4px 0 0 0',
                color: 'var(--text-secondary)',
                fontSize: '0.9rem',
              }}
            >
              Submit code files or snippets for instant AI-assisted engineering
              reviews
            </p>
          </div>
        </header>

        {/* Main Grid */}
        <div
          className="workspace-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 1.2fr) minmax(0, 0.8fr)',
            gap: '32px',
            alignItems: 'start',
          }}
        >
          {/* Left Column: Code input workspace */}
          <section
            className="glass-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '20px',
              minHeight: '550px',
              minWidth: 0,
            }}
          >
            <LanguageSelector
              value={language}
              onChange={setLanguage}
              disabled={status === 'processing'}
            />
            <FileUploader
              onCodeUpload={handleCodeUpload}
              disabled={status === 'processing'}
              uploadedFileName={fileName}
              onClearFile={handleClearFile}
            />
            <CodeEditor
              value={code}
              onChange={setCode}
              disabled={status === 'processing'}
              language={language}
            />
          </section>

          {/* Right Column: Execution control & Output layout */}
          <section
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '24px',
              minWidth: 0,
            }}
          >
            <div
              className="glass-card"
              style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}
            >
              <h3
                style={{
                  margin: 0,
                  fontSize: '1.1rem',
                  color: 'var(--text-secondary)',
                }}
              >
                Execution Control
              </h3>
              <ReviewButton
                onClick={handleStartReview}
                disabled={!code.trim()}
                loading={status === 'processing'}
              />
              {status === 'success' && reviewData && (
                <button
                  onClick={() => setIsFindingsModalOpen(true)}
                  className="btn"
                  style={{
                    width: '100%',
                    justifyContent: 'center',
                    padding: '12px 24px',
                    fontSize: '1.05rem',
                    fontWeight: 700,
                    height: '48px',
                    background: 'var(--success-color)',
                    boxShadow: '0 4px 14px 0 rgba(16, 185, 129, 0.25)',
                  }}
                >
                  🔎 View Findings (#{reviewData.id})
                </button>
              )}
              {status === 'error' && error && (
                <div
                  style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid var(--danger-color)',
                    padding: '12px',
                    borderRadius: '8px',
                    fontSize: '0.85rem',
                    color: '#f87171',
                    wordBreak: 'break-word',
                  }}
                >
                  <strong>Error:</strong> {error}
                </div>
              )}
            </div>

            <ProcessingStatus status={status} currentStep={currentStep} />
          </section>
        </div>
      </div>

      {/* Findings Modal Dialog */}
      <FindingsModal
        isOpen={isFindingsModalOpen}
        onClose={() => setIsFindingsModalOpen(false)}
        reviewData={reviewData}
        status={status}
        setReviewData={setReviewData}
        showDebug={showDebug ?? false}
      />
    </div>
  );
};
export default ReviewWorkspace;
