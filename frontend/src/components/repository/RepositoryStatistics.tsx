import React from 'react';

interface RepositoryStatisticsProps {
    filesCount: number;
    criticalCount: number;
    ticketsCount: number;
    duration: number | null;
}

export const RepositoryStatistics: React.FC<RepositoryStatisticsProps> = ({
    filesCount,
    criticalCount,
    ticketsCount,
    duration,
}) => {
    const formattedDuration = duration !== null
        ? `${duration.toFixed(1)}s`
        : 'N/A';

    const statCards = [
        {
            label: 'Files Analyzed',
            value: filesCount,
            icon: '📂',
            color: 'rgba(99, 102, 241, 0.1)',
            textColor: 'var(--accent-color)',
        },
        {
            label: 'Critical Issues',
            value: criticalCount,
            icon: '⚠️',
            color: criticalCount > 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(255, 255, 255, 0.05)',
            textColor: criticalCount > 0 ? 'var(--danger-color)' : 'var(--text-secondary)',
        },
        {
            label: 'Tickets Filed',
            value: ticketsCount,
            icon: '🎟️',
            color: 'rgba(16, 185, 129, 0.1)',
            textColor: 'var(--success-color)',
        },
        {
            label: 'Scan Duration',
            value: formattedDuration,
            icon: '⏱️',
            color: 'rgba(245, 158, 11, 0.1)',
            textColor: '#f59e0b',
        },
    ];

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            {statCards.map((card, idx) => (
                <div
                    key={idx}
                    style={{
                        background: 'var(--card-bg)',
                        borderRadius: '12px',
                        padding: '20px',
                        boxShadow: 'var(--card-shadow)',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                    }}
                >
                    <div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            {card.label}
                        </div>
                        <div style={{ fontSize: '1.8rem', fontWeight: 700, marginTop: '8px', color: card.textColor }}>
                            {card.value}
                        </div>
                    </div>
                    <div
                        style={{
                            width: '46px',
                            height: '46px',
                            borderRadius: '10px',
                            background: card.color,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '1.4rem',
                        }}
                    >
                        {card.icon}
                    </div>
                </div>
            ))}
        </div>
    );
};
