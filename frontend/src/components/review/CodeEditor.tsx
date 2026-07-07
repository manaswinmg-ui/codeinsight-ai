import * as React from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  language?: string;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  disabled = false,
  language = 'python',
}) => {
  // Map our language selector values to Monaco Editor language IDs if needed
  const getMonacoLanguage = (lang: string) => {
    switch (lang.toLowerCase()) {
      case 'cpp':
        return 'cpp';
      case 'csharp':
        return 'csharp';
      default:
        return lang;
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        flexGrow: 1,
        minHeight: '400px',
        minWidth: 0,
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
      <div
        style={{
          width: '100%',
          height: '380px',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          overflow: 'hidden',
          background: '#1e1e1e', // Monaco vs-dark default background
          opacity: disabled ? 0.7 : 1,
          cursor: disabled ? 'not-allowed' : 'text',
        }}
      >
        <Editor
          height="100%"
          language={getMonacoLanguage(language)}
          theme="vs-dark"
          value={value}
          onChange={(val) => onChange(val || '')}
          options={{
            readOnly: disabled,
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily:
              'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
            lineNumbers: 'on',
            roundedSelection: true,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    </div>
  );
};
