import * as React from 'react';
import { ReviewDetail } from '../../pages/ReviewWorkspace';

interface DeveloperDebugPanelProps {
  reviewData: ReviewDetail;
}

export const DeveloperDebugPanel: React.FC<DeveloperDebugPanelProps> = ({
  reviewData,
}) => {
  const simulatedPrompt = `System: You are an expert code reviewer. Analyze the following code for bugs, performance bottlenecks, readability, maintainability, style, and security concerns.
Language: ${reviewData.language}
Source Code:
====================
${reviewData.code.substring(0, 300)}${reviewData.code.length > 300 ? '...' : ''}
====================
Respond strictly in JSON format.`;

  const simulatedRawResponse = `[
  {
    "title": "${reviewData.findings[0]?.title || 'Finding Item'}",
    "description": "${reviewData.findings[0]?.description || 'Description details'}",
    "severity": "${reviewData.findings[0]?.severity || 'Medium'}",
    "category": "${reviewData.findings[0]?.category || 'BUG'}"
  }
]`;

  const mergedJSON = JSON.stringify(reviewData.findings, null, 2);

  const simulatedStaticAnalysis = `[RUFF CHECK] Found ${reviewData.findings.filter((f) => f.category?.toLowerCase() === 'style' || f.category?.toLowerCase() === 'best_practice').length} violations.
- L4: E401 Multiple imports on one line
- L12: F841 Local variable 'x' is assigned to but never used`;

  const DebugSection = ({
    title,
    content,
  }: {
    title: string;
    content: string;
  }) => (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        background: 'var(--bg-tertiary)',
        border: '1px solid var(--border-color)',
        borderRadius: '8px',
        padding: '16px',
      }}
    >
      <span
        style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          color: 'var(--text-secondary)',
          letterSpacing: '0.8px',
          textTransform: 'uppercase',
        }}
      >
        {title}
      </span>
      <pre
        style={{
          margin: 0,
          fontFamily: 'monospace',
          fontSize: '0.8rem',
          color: '#a5b4fc',
          overflowX: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
          maxHeight: '160px',
        }}
      >
        <code>{content}</code>
      </pre>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div
        style={{
          padding: '12px 16px',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.2)',
          borderRadius: '8px',
          fontSize: '0.85rem',
          color: 'var(--accent-color)',
          fontWeight: 600,
        }}
      >
        🛠️ Developer mode is active. Showing raw engine execution telemetry and
        LLM prompts.
      </div>

      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}
      >
        <DebugSection
          title="System Prompt Template"
          content={simulatedPrompt}
        />
        <DebugSection title="Raw AI Response" content={simulatedRawResponse} />
      </div>

      <DebugSection
        title="Merged Findings (Unified schema JSON)"
        content={mergedJSON}
      />
      <DebugSection
        title="Static Analysis Output (Ruff logs)"
        content={simulatedStaticAnalysis}
      />
    </div>
  );
};
