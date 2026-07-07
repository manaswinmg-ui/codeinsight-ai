import React, { useState, useRef } from 'react';

interface RepositoryUploadPageProps {
  onUploadSuccess: (repoId: number) => void;
}

export const RepositoryUploadPage: React.FC<RepositoryUploadPageProps> = ({
  onUploadSuccess,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndUpload = async (file: File) => {
    setError(null);

    // Limit checks
    if (!file.name.endsWith('.zip')) {
      setError('Unsupported format. Please upload a ZIP archive (.zip).');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds the 50 MB limit.');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    const baseUrl = window.location.origin.includes('5173')
      ? 'http://localhost:8000'
      : '';

    try {
      const response = await fetch(`${baseUrl}/api/v1/repositories`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to scan repository.');
      }

      const data = await response.json();
      onUploadSuccess(data.repository_id);
    } catch (err: any) {
      setError(err.message || 'Error occurred during upload.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndUpload(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div style={{ maxWidth: '680px', margin: '40px auto', padding: '0 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '12px' }}>
          Scan Codebase Repository
        </h1>
        <p
          style={{
            color: 'var(--text-secondary)',
            fontSize: '1.05rem',
            lineHeight: '1.5',
          }}
        >
          Upload a ZIP archive of your project directory to run automated
          multi-file reviews and evaluate codebase quality.
        </p>
      </div>

      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        style={{
          border: dragActive
            ? '2px dashed var(--accent-color)'
            : '2px dashed rgba(255, 255, 255, 0.15)',
          background: dragActive
            ? 'rgba(99, 102, 241, 0.05)'
            : 'var(--card-bg)',
          borderRadius: '16px',
          padding: '60px 40px',
          textAlign: 'center',
          cursor: uploading ? 'not-allowed' : 'pointer',
          transition: 'all 0.25s ease',
          boxShadow: 'var(--card-shadow)',
          position: 'relative',
        }}
        onClick={uploading ? undefined : onButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          disabled={uploading}
        />

        <div style={{ fontSize: '4rem', marginBottom: '20px' }}>📦</div>

        {uploading ? (
          <div>
            <div
              className="spinner"
              style={{
                width: '36px',
                height: '36px',
                border: '3px solid rgba(255,255,255,0.1)',
                borderTopColor: 'var(--accent-color)',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite',
                margin: '0 auto 16px auto',
              }}
            />
            <p style={{ fontWeight: 600, fontSize: '1.1rem' }}>
              Uploading and scanning archive...
            </p>
            <p
              style={{
                color: 'var(--text-secondary)',
                fontSize: '0.9rem',
                marginTop: '6px',
              }}
            >
              Validating and parsing project structure in-memory
            </p>
          </div>
        ) : (
          <div>
            <p
              style={{
                fontSize: '1.15rem',
                fontWeight: 600,
                marginBottom: '8px',
              }}
            >
              Drag and drop your ZIP here, or{' '}
              <span style={{ color: 'var(--accent-color)' }}>browse files</span>
            </p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              ZIP archives up to 50 MB are supported.
            </p>
          </div>
        )}
      </div>

      {error && (
        <div
          style={{
            marginTop: '24px',
            padding: '16px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            color: 'var(--danger-color)',
            borderRadius: '12px',
            fontSize: '0.95rem',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}
        >
          <span>⚠️</span>
          <div>{error}</div>
        </div>
      )}

      <div
        style={{
          marginTop: '40px',
          padding: '24px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        <h3
          style={{
            fontSize: '1rem',
            fontWeight: 600,
            marginBottom: '16px',
            color: 'var(--text-primary)',
          }}
        >
          Scan Exclusions & Limits
        </h3>
        <ul
          style={{
            paddingLeft: '20px',
            margin: 0,
            color: 'var(--text-secondary)',
            fontSize: '0.88rem',
            lineHeight: '1.7',
          }}
        >
          <li>
            Excludes metadata and build folders: <code>node_modules</code>,{' '}
            <code>.git</code>, <code>dist</code>, <code>venv</code>, etc.
          </li>
          <li>Skips compiled binaries and unrecognized text types.</li>
          <li>
            Supported file extensions: <code>.py</code>, <code>.js</code>,{' '}
            <code>.ts</code>, <code>.tsx</code>, <code>.go</code>,{' '}
            <code>.java</code>, <code>.cpp</code>, <code>.cs</code>.
          </li>
          <li>
            Limits: Max 1,000 total files, 500 source files, and 2 MB per file.
          </li>
        </ul>
      </div>

      <style>{`
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `}</style>
    </div>
  );
};
