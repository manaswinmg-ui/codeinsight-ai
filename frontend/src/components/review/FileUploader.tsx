import * as React from 'react';
import { useRef } from 'react';

interface FileUploaderProps {
  onCodeUpload: (
    code: string,
    fileName: string,
    detectedLanguage?: string
  ) => void;
  disabled?: boolean;
  uploadedFileName: string | null;
  onClearFile: () => void;
}

const EXTENSION_MAP: Record<string, string> = {
  py: 'python',
  js: 'javascript',
  jsx: 'javascript',
  ts: 'typescript',
  tsx: 'typescript',
  go: 'go',
  java: 'java',
  cpp: 'cpp',
  cc: 'cpp',
  h: 'cpp',
  cs: 'csharp',
};

export const FileUploader: React.FC<FileUploaderProps> = ({
  onCodeUpload,
  disabled = false,
  uploadedFileName,
  onClearFile,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const fileName = file.name;
    const extension = fileName.split('.').pop()?.toLowerCase() || '';
    const detectedLanguage = EXTENSION_MAP[extension];

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      onCodeUpload(text, fileName, detectedLanguage);
    };
    reader.readAsText(file);
  };

  const triggerFileInput = () => {
    if (disabled) return;
    fileInputRef.current?.click();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <label
        style={{
          fontSize: '0.9rem',
          color: 'var(--text-secondary)',
          fontWeight: 600,
        }}
      >
        File Upload (Optional)
      </label>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        disabled={disabled}
        accept=".py,.js,.jsx,.ts,.tsx,.go,.java,.cpp,.cc,.h,.cs,.txt"
      />
      <div
        onClick={triggerFileInput}
        style={{
          border: '2px dashed var(--border-color)',
          borderRadius: '8px',
          padding: '16px',
          textAlign: 'center',
          cursor: disabled ? 'not-allowed' : 'pointer',
          background: 'rgba(255, 255, 255, 0.02)',
          transition: 'border-color 0.2s, background-color 0.2s',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        {uploadedFileName ? (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              width: '100%',
              justifyContent: 'center',
            }}
          >
            <span style={{ fontSize: '1.2rem' }}>📄</span>
            <span
              style={{
                fontSize: '0.9rem',
                fontWeight: 600,
                color: 'var(--success-color)',
              }}
            >
              {uploadedFileName}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClearFile();
                if (fileInputRef.current) fileInputRef.current.value = '';
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--danger-color)',
                cursor: 'pointer',
                fontSize: '1rem',
                padding: '4px 8px',
                borderRadius: '4px',
              }}
            >
              ✕
            </button>
          </div>
        ) : (
          <>
            <span style={{ fontSize: '1.5rem' }}>📤</span>
            <span
              style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}
            >
              Drag & drop or{' '}
              <strong style={{ color: 'var(--accent-color)' }}>
                browse file
              </strong>
            </span>
          </>
        )}
      </div>
    </div>
  );
};
