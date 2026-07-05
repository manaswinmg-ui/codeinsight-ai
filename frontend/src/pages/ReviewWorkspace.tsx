import { useState, useEffect } from 'react';

import { CodeEditor } from '../components/CodeEditor';
import { FileUploader } from '../components/FileUploader';
import { LanguageSelector } from '../components/LanguageSelector';
import { ProcessingStatus } from '../components/ProcessingStatus';
import { ReviewButton } from '../components/ReviewButton';
import { ReviewResults } from '../components/ReviewResults';

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

export const ReviewWorkspace = () => {
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

  // Poll review status when activeReviewId is set
  useEffect(() => {
    if (activeReviewId === null) return;

    let intervalId: ReturnType<typeof setInterval> | undefined = undefined;

    const poll = async () => {
      try {
        const response = await fetch(`/api/v1/reviews/${activeReviewId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch review status: ${response.statusText}`);
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
        setError(err instanceof Error ? err.message : 'An error occurred during status polling.');
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

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '32px',
        minHeight: '85vh',
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
          />
        </section>

        {/* Right Column: Execution control & Output layout */}
        <section
          style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}
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

          <ReviewResults status={status} reviewData={reviewData} />
        </section>
      </div>
    </div>
  );
};
export default ReviewWorkspace;
