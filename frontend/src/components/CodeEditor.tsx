import React from 'react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        flexGrow: 1,
      }}
    >
      <label
        style={{
          fontSize: '0.9rem',
          color: 'var(--text-secondary)',
          fontWeight: 600,
        }}
      >
        Source Code
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder="Paste code snippet or upload a file above to begin code review analysis..."
        style={{
          width: '100%',
          flexGrow: 1,
          minHeight: '350px',
          background: 'var(--bg-tertiary)',
          border: '1px solid var(--border-color)',
          color: '#e2e8f0',
          fontFamily:
            'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
          fontSize: '0.9rem',
          padding: '16px',
          borderRadius: '8px',
          outline: 'none',
          resize: 'vertical',
          lineHeight: '1.5',
          cursor: disabled ? 'not-allowed' : 'text',
          opacity: disabled ? 0.7 : 1,
        }}
      />
    </div>
  );
};
