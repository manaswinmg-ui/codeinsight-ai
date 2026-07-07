import React from 'react';

interface FileReviewListItem {
    id: number;
    file_path: string;
    language: string;
    status: string;
    quality_score: number;
    findings_count: number;
    tickets_count: number;
}

interface RepositoryFileTableProps {
    files: FileReviewListItem[];
    onSelectFileReview: (reviewId: number) => void;
    largestFiles: { file_path: string; size_bytes: number }[];
    problematicFiles: { file_path: string; findings_count: number; quality_score: number }[];
}

export const RepositoryFileTable: React.FC<RepositoryFileTableProps> = ({
    files,
    onSelectFileReview,
    largestFiles,
    problematicFiles,
}) => {
    const getScoreBadgeStyle = (score: number) => {
        if (score >= 80) return { background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-color)' };
        if (score >= 50) return { background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' };
        return { background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger-color)' };
    };

    const getStatusStyle = (statusStr: string) => {
        const s = statusStr.toUpperCase();
        if (s === 'COMPLETED') return { background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-color)' };
        if (s === 'PROCESSING') return { background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-color)', animation: 'pulse 1.5s infinite' };
        if (s === 'FAILED') return { background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger-color)' };
        return { background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)' };
    };

    const formatBytes = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    return (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', alignItems: 'stretch' }}>
            
            {/* Main Files Table (Left Side) */}
            <div
                style={{
                    flex: '2 1 600px',
                    background: 'var(--card-bg)',
                    borderRadius: '16px',
                    padding: '24px',
                    boxShadow: 'var(--card-shadow)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    minWidth: 0,
                }}
            >
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '20px', color: 'var(--text-primary)' }}>
                    Files Table
                </h3>

                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '500px' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.08)', color: 'var(--text-secondary)', fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase' }}>
                                <th style={{ padding: '12px 16px' }}>File Path</th>
                                <th style={{ padding: '12px 16px' }}>Language</th>
                                <th style={{ padding: '12px 16px' }}>Score</th>
                                <th style={{ padding: '12px 16px' }}>Issues</th>
                                <th style={{ padding: '12px 16px' }}>Tickets</th>
                                <th style={{ padding: '12px 16px' }}>Status</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {files.map((file) => {
                                const scoreStyle = getScoreBadgeStyle(file.quality_score);
                                const statusStyle = getStatusStyle(file.status);

                                return (
                                    <tr
                                        key={file.id}
                                        style={{
                                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                                            fontSize: '0.9rem',
                                            transition: 'background 0.2s',
                                        }}
                                        onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'; }}
                                        onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                                    >
                                        <td style={{ padding: '16px', fontWeight: 500, color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                                            {file.file_path}
                                        </td>
                                        <td style={{ padding: '16px', textTransform: 'capitalize', color: 'var(--text-secondary)' }}>
                                            {file.language}
                                        </td>
                                        <td style={{ padding: '16px' }}>
                                            {file.status === 'COMPLETED' ? (
                                                <span
                                                    style={{
                                                        padding: '4px 8px',
                                                        borderRadius: '6px',
                                                        fontSize: '0.8rem',
                                                        fontWeight: 700,
                                                        ...scoreStyle,
                                                    }}
                                                >
                                                    {file.quality_score}
                                                </span>
                                            ) : (
                                                <span style={{ color: 'var(--text-secondary)' }}>-</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '16px', fontWeight: 600 }}>
                                            {file.findings_count}
                                        </td>
                                        <td style={{ padding: '16px' }}>
                                            {file.tickets_count > 0 ? (
                                                <span style={{ color: 'var(--success-color)', fontWeight: 600 }}>
                                                    {file.tickets_count}
                                                </span>
                                            ) : (
                                                <span style={{ color: 'var(--text-secondary)' }}>0</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '16px' }}>
                                            <span
                                                style={{
                                                    padding: '3px 8px',
                                                    borderRadius: '6px',
                                                    fontSize: '0.75rem',
                                                    fontWeight: 600,
                                                    display: 'inline-block',
                                                    ...statusStyle,
                                                }}
                                            >
                                                {file.status}
                                            </span>
                                        </td>
                                        <td style={{ padding: '16px' }}>
                                            <button
                                                onClick={() => onSelectFileReview(file.id)}
                                                disabled={file.status !== 'COMPLETED'}
                                                style={{
                                                    background: 'rgba(99, 102, 241, 0.1)',
                                                    color: 'var(--accent-color)',
                                                    border: 'none',
                                                    padding: '6px 12px',
                                                    borderRadius: '6px',
                                                    fontSize: '0.8rem',
                                                    fontWeight: 600,
                                                    cursor: file.status === 'COMPLETED' ? 'pointer' : 'not-allowed',
                                                    transition: 'all 0.2s',
                                                    opacity: file.status === 'COMPLETED' ? 1 : 0.4,
                                                }}
                                                onMouseEnter={(e) => {
                                                    if (file.status === 'COMPLETED') {
                                                        e.currentTarget.style.background = 'var(--accent-color)';
                                                        e.currentTarget.style.color = '#fff';
                                                    }
                                                }}
                                                onMouseLeave={(e) => {
                                                    if (file.status === 'COMPLETED') {
                                                        e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)';
                                                        e.currentTarget.style.color = 'var(--accent-color)';
                                                    }
                                                }}
                                            >
                                                View
                                            </button>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Codebase Meta Sidebars (Right Side) */}
            <div
                style={{
                    flex: '1 1 300px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '24px',
                    alignSelf: 'flex-start',
                }}
            >
                {/* Most Problematic Files */}
                <div
                    style={{
                        background: 'var(--card-bg)',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: 'var(--card-shadow)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                    }}
                >
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)' }}>
                        🚨 Most Problematic Files
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                        {problematicFiles.map((file, idx) => {
                            const scoreStyle = getScoreBadgeStyle(file.quality_score);
                            return (
                                <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '8px' }}>
                                    <div style={{ wordBreak: 'break-all', paddingRight: '12px' }}>
                                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{file.file_path}</div>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '3px' }}>
                                            {file.findings_count} findings detected
                                        </div>
                                    </div>
                                    <span
                                        style={{
                                            padding: '3px 8px',
                                            borderRadius: '6px',
                                            fontSize: '0.75rem',
                                            fontWeight: 700,
                                            flexShrink: 0,
                                            ...scoreStyle,
                                        }}
                                    >
                                        Score: {file.quality_score}
                                    </span>
                                </div>
                            );
                        })}
                        {problematicFiles.length === 0 && (
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>
                                No problematic files found! Clean codebase.
                            </p>
                        )}
                    </div>
                </div>

                {/* Largest Files */}
                <div
                    style={{
                        background: 'var(--card-bg)',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: 'var(--card-shadow)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                    }}
                >
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)' }}>
                        📦 Largest Files
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                        {largestFiles.map((file, idx) => (
                            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', borderBottom: '1px solid rgba(255,255,255,0.03)', paddingBottom: '8px' }}>
                                <span style={{ fontWeight: 600, color: 'var(--text-primary)', wordBreak: 'break-all', paddingRight: '12px' }}>
                                    {file.file_path}
                                </span>
                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', flexShrink: 0 }}>
                                    {formatBytes(file.size_bytes)}
                                </span>
                            </div>
                        ))}
                        {largestFiles.length === 0 && (
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: 0 }}>
                                No files list.
                            </p>
                        )}
                    </div>
                </div>
            </div>

            <style>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.6; }
                }
            `}</style>
        </div>
    );
};
