import * as React from 'react';
import { useState } from 'react';
import { useToast } from './ToastProvider';

export interface TicketData {
  id: number;
  finding_id: number;
  title: string;
  description: string;
  priority: string;
  status: string;
  assignee: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  resolution_notes: string | null;
}

interface TicketCardProps {
  ticket: TicketData;
  onClose: () => void;
  onStatusUpdated?: (updatedTicket: TicketData) => void;
}

const PRIORITY_COLORS: Record<string, string> = {
  P0: '#e879f9', // Critical / P0
  P1: '#f87171', // High / P1
  P2: '#fbbf24', // Medium / P2
  P3: '#60a5fa', // Low / P3
};

const STATUS_COLORS: Record<string, string> = {
  OPEN: '#34d399',
  TODO: '#60a5fa',
  IN_PROGRESS: '#fbbf24',
  IN_REVIEW: '#a78bfa',
  DONE: '#10b981',
  CLOSED: '#9ca3af',
};

// Allowed transitions mapping matching backend rules
const ALLOWED_TRANSITIONS: Record<string, string[]> = {
  OPEN: ['TODO', 'IN_PROGRESS', 'CLOSED'],
  TODO: ['IN_PROGRESS', 'CLOSED'],
  IN_PROGRESS: ['IN_REVIEW', 'TODO', 'CLOSED'],
  IN_REVIEW: ['DONE', 'IN_PROGRESS', 'CLOSED'],
  DONE: ['CLOSED', 'IN_PROGRESS'],
  CLOSED: [],
};

export const TicketCard: React.FC<TicketCardProps> = ({ ticket, onClose, onStatusUpdated }) => {
  const formattedDate = new Date(ticket.created_at).toLocaleString();
  const { addToast } = useToast();
  
  const [currentTicket, setCurrentTicket] = useState<TicketData>(ticket);
  const [transitioningTo, setTransitioningTo] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const allowedNext = ALLOWED_TRANSITIONS[currentTicket.status] || [];

  const handleTransitionClick = (nextStatus: string) => {
    if (nextStatus === 'DONE' || nextStatus === 'CLOSED') {
      setTransitioningTo(nextStatus);
      setNotes('');
    } else {
      executeTransition(nextStatus, null);
    }
  };

  const executeTransition = async (nextStatus: string, resolutionNotes: string | null) => {
    setLoading(true);
    try {
      const baseUrl = window.location.origin.includes('5173')
        ? 'http://localhost:8000'
        : '';
      const response = await fetch(`${baseUrl}/api/v1/tickets/${currentTicket.id}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: nextStatus,
          resolution_notes: resolutionNotes,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to update ticket status');
      }

      const updated: TicketData = await response.json();
      setCurrentTicket(updated);
      if (onStatusUpdated) {
        onStatusUpdated(updated);
      }
      addToast(`Ticket status updated to ${nextStatus}`, 'success');
      setTransitioningTo(null);
    } catch (err) {
      addToast(err instanceof Error ? err.message : 'Error transitioning ticket status', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="glass-card"
      style={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        zIndex: 1000,
        maxWidth: '520px',
        width: '90%',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: '24px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.5)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(16px)',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '1px' }}>
          TICKET #T-{currentTicket.id}
        </span>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            fontSize: '1.4rem',
            padding: 0,
            lineHeight: 1,
            transition: 'color 0.2s',
          }}
          onMouseEnter={(e) => ((e.target as HTMLButtonElement).style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => ((e.target as HTMLButtonElement).style.color = 'var(--text-muted)')}
        >
          &times;
        </button>
      </div>

      <h3 style={{ margin: 0, color: 'var(--text-primary)', fontSize: '1.15rem', fontWeight: 800 }}>
        {currentTicket.title}
      </h3>

      {/* Badges */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        <span
          style={{
            fontSize: '0.68rem',
            background: `${PRIORITY_COLORS[currentTicket.priority] || '#9ca3af'}18`,
            color: PRIORITY_COLORS[currentTicket.priority] || '#9ca3af',
            border: `1px solid ${PRIORITY_COLORS[currentTicket.priority] || '#9ca3af'}33`,
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: 700,
          }}
        >
          Priority: {currentTicket.priority}
        </span>
        <span
          style={{
            fontSize: '0.68rem',
            background: `${STATUS_COLORS[currentTicket.status] || '#9ca3af'}18`,
            color: STATUS_COLORS[currentTicket.status] || '#9ca3af',
            border: `1px solid ${STATUS_COLORS[currentTicket.status] || '#9ca3af'}33`,
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: 700,
          }}
        >
          Status: {currentTicket.status}
        </span>
      </div>

      {/* Description */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
          DESCRIPTION
        </span>
        <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
          {currentTicket.description}
        </p>
      </div>

      {/* Metadata */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '12px',
          borderTop: '1px solid var(--border-color)',
          paddingTop: '14px',
          marginTop: '4px',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600 }}>ASSIGNEE</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            👤 {currentTicket.assignee || 'Unassigned'}
          </span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 600 }}>CREATED ON</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            📅 {formattedDate}
          </span>
        </div>
      </div>

      {/* Resolution Notes Display */}
      {currentTicket.resolution_notes && (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '4px',
            background: 'rgba(255,255,255,0.02)',
            padding: '10px 12px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            marginTop: '4px',
          }}
        >
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.5px' }}>
            RESOLUTION NOTES
          </span>
          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
            {currentTicket.resolution_notes}
          </p>
        </div>
      )}

      {/* Transition Buttons UI */}
      {allowedNext.length > 0 && !transitioningTo && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
          <span style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
            UPDATE TICKET STATUS
          </span>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {allowedNext.map((next) => (
              <button
                key={next}
                onClick={() => handleTransitionClick(next)}
                disabled={loading}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    (e.target as HTMLButtonElement).style.borderColor = STATUS_COLORS[next];
                    (e.target as HTMLButtonElement).style.color = STATUS_COLORS[next];
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    (e.target as HTMLButtonElement).style.borderColor = 'var(--border-color)';
                    (e.target as HTMLButtonElement).style.color = 'var(--text-primary)';
                  }
                }}
              >
                ➔ {next}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Resolution Notes Form */}
      {transitioningTo && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
          <span style={{ fontSize: '0.68rem', fontWeight: 700, color: STATUS_COLORS[transitioningTo], letterSpacing: '0.5px' }}>
            ADD NOTES FOR TRANSITIONING TO {transitioningTo}
          </span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add resolution or closure details (optional)..."
            style={{
              width: '100%',
              minHeight: '60px',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              borderRadius: '6px',
              padding: '10px',
              fontSize: '0.85rem',
              outline: 'none',
              resize: 'vertical',
            }}
          />
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              onClick={() => setTransitioningTo(null)}
              disabled={loading}
              className="btn btn-secondary"
              style={{ padding: '6px 14px', fontSize: '0.8rem' }}
            >
              Cancel
            </button>
            <button
              onClick={() => executeTransition(transitioningTo, notes)}
              disabled={loading}
              className="btn"
              style={{ padding: '6px 14px', fontSize: '0.8rem', background: STATUS_COLORS[transitioningTo] }}
            >
              {loading ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
