import React from 'react';

interface RepositoryProgressProps {
    repoName: string;
    onBackToHistory: () => void;
}

export const RepositoryProgress: React.FC<RepositoryProgressProps> = ({ repoName, onBackToHistory }) => {
    return (
        <div style={{ maxWidth: '600px', margin: '60px auto', textAlign: 'center', padding: '0 20px' }}>
            <div style={{ fontSize: '4.5rem', marginBottom: '24px' }}>⚙️</div>
            
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '12px' }}>
                Analyzing {repoName}
            </h2>
            
            <p style={{ color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: '1.6', marginBottom: '32px' }}>
                The Hybrid Analysis Engine is reviewing your codebase. Multiple files are being evaluated in parallel. Larger codebases may take a minute.
            </p>

            <div style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '12px', padding: '24px', marginBottom: '32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                    <span>Pipeline Status</span>
                    <span style={{ color: 'var(--accent-color)' }}>PROCESSING</span>
                </div>
                
                {/* Simulated infinite slow progress bar */}
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div
                        style={{
                            width: '75%',
                            height: '100%',
                            background: 'var(--accent-color)',
                            borderRadius: '3px',
                            animation: 'pulseBar 2s infinite ease-in-out',
                        }}
                    />
                </div>
                
                <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <span className="dot" style={{ width: '8px', height: '8px', background: 'var(--accent-color)', borderRadius: '50%', display: 'inline-block', animation: 'blink 1.5s infinite' }} />
                        Executing AST Scanner and AI heuristics
                    </div>
                </div>
            </div>

            <button
                onClick={onBackToHistory}
                style={{
                    background: 'transparent',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    color: 'var(--text-primary)',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
                View Repository Logs
            </button>

            <style>{`
                @keyframes pulseBar {
                    0% { transform: translateX(-100%); }
                    50% { transform: translateX(30%); }
                    100% { transform: translateX(100%); }
                }
                @keyframes blink {
                    0%, 100% { opacity: 0.3; }
                    50% { opacity: 1; }
                }
            `}</style>
        </div>
    );
};
