import React, { useState } from 'react';
import { useToast } from './ToastProvider';

interface CreateTicketButtonProps {
  findingId: number;
  ticketId: number | null | undefined;
  onCreateSuccess: (findingId: number, ticketId: number) => void;
  onViewTicket: (ticketId: number) => void;
}

export const CreateTicketButton: React.FC<CreateTicketButtonProps> = ({
  findingId,
  ticketId,
  onCreateSuccess,
  onViewTicket,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addToast } = useToast();

  const handleCreate = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setLoading(true);
    setError(null);
    try {
      // Use absolute endpoint prefix to ensure proxy/direct works correctly
      const baseUrl = window.location.origin.includes('5173')
        ? 'http://localhost:8000'
        : '';
      const response = await fetch(`${baseUrl}/api/v1/findings/${findingId}/ticket`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

       if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to create ticket');
      }

      const ticket = await response.json();
      onCreateSuccess(findingId, ticket.id);
      addToast(`Ticket #T-${ticket.id} created successfully!`, 'success');
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Error creating ticket';
      setError(errMsg);
      addToast(errMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  if (ticketId) {
    return (
      <button
        onClick={(e) => {
          e.stopPropagation();
          onViewTicket(ticketId);
        }}
        style={{
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid var(--accent-color)',
          borderRadius: '6px',
          padding: '5px 12px',
          color: 'var(--accent-color)',
          cursor: 'pointer',
          fontSize: '0.78rem',
          fontWeight: 600,
          transition: 'all 0.2s',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
        }}
        onMouseEnter={(e) => {
          (e.target as HTMLButtonElement).style.background = 'var(--accent-color)';
          (e.target as HTMLButtonElement).style.color = '#ffffff';
        }}
        onMouseLeave={(e) => {
          (e.target as HTMLButtonElement).style.background = 'rgba(99, 102, 241, 0.1)';
          (e.target as HTMLButtonElement).style.color = 'var(--accent-color)';
        }}
      >
        🎟️ View Ticket
      </button>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'flex-start' }}>
      <button
        onClick={handleCreate}
        disabled={loading}
        style={{
          background: 'none',
          border: '1px solid var(--border-color)',
          borderRadius: '6px',
          padding: '5px 12px',
          color: 'var(--text-primary)',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontSize: '0.78rem',
          fontWeight: 600,
          transition: 'all 0.2s',
          opacity: loading ? 0.6 : 1,
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
        }}
        onMouseEnter={(e) => {
          if (!loading) {
            (e.target as HTMLButtonElement).style.borderColor = 'var(--accent-color)';
            (e.target as HTMLButtonElement).style.color = 'var(--accent-color)';
          }
        }}
        onMouseLeave={(e) => {
          if (!loading) {
            (e.target as HTMLButtonElement).style.borderColor = 'var(--border-color)';
            (e.target as HTMLButtonElement).style.color = 'var(--text-primary)';
          }
        }}
      >
        {loading ? 'Creating...' : '➕ Create Ticket'}
      </button>
      {error && (
        <span style={{ fontSize: '0.7rem', color: 'var(--danger-color)', marginTop: '2px' }}>
          {error}
        </span>
      )}
    </div>
  );
};
