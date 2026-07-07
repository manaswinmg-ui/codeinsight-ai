import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';

export function UserMenu() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, []);

  if (!user) return null;

  const initials = (user.full_name || user.username || 'U')
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <div
      ref={dropdownRef}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--border-color)',
          borderRadius: '24px',
          padding: '4px 12px 4px 6px',
          cursor: 'pointer',
          color: 'var(--text-primary)',
          fontSize: '0.9rem',
          fontWeight: 600,
          transition: 'all 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
          e.currentTarget.style.borderColor = 'var(--border-focus)';
        }}
        onMouseLeave={(e) => {
          if (!isOpen) {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)';
            e.currentTarget.style.borderColor = 'var(--border-color)';
          }
        }}
      >
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #818cf8 0%, #6366f1 100%)',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.85rem',
            fontWeight: 800,
            boxShadow: '0 2px 8px rgba(99, 102, 241, 0.3)',
          }}
        >
          {initials}
        </div>
        <span
          style={{
            maxWidth: '120px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {user.full_name || user.username}
        </span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
          {isOpen ? '▲' : '▼'}
        </span>
      </button>

      {isOpen && (
        <div
          className="glass-card"
          style={{
            position: 'absolute',
            right: 0,
            top: 'calc(100% + 8px)',
            width: '240px',
            zIndex: 1000,
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            borderRadius: '12px',
            boxShadow:
              '0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5)',
            transform: 'none',
          }}
        >
          <div
            style={{
              borderBottom: '1px solid var(--border-color)',
              paddingBottom: '12px',
            }}
          >
            <div
              style={{
                fontWeight: 700,
                fontSize: '0.95rem',
                color: 'var(--text-primary)',
              }}
            >
              {user.full_name || user.username}
            </div>
            <div
              style={{
                fontSize: '0.8rem',
                color: 'var(--text-secondary)',
                marginTop: '2px',
              }}
            >
              @{user.username}
            </div>
            <div
              style={{
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                marginTop: '4px',
                wordBreak: 'break-all',
              }}
            >
              {user.email}
            </div>
          </div>

          <button
            onClick={() => {
              setIsOpen(false);
              logout();
            }}
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '6px',
              background: 'rgba(239, 68, 68, 0.08)',
              color: '#fca5a5',
              border: '1px solid rgba(239, 68, 68, 0.2)',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
              e.currentTarget.style.borderColor = 'var(--danger-color)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(239, 68, 68, 0.08)';
              e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.2)';
            }}
          >
            🚪 Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
