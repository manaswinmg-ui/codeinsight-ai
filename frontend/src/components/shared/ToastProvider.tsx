import React, { createContext, useContext, useState, useCallback } from 'react';

export type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  addToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const getToastColors = (type: ToastType) => {
    switch (type) {
      case 'success':
        return {
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderLeft: '4px solid var(--success-color)',
          bg: 'rgba(18, 19, 26, 0.95)',
          icon: '✅',
          iconColor: 'var(--success-color)',
        };
      case 'error':
        return {
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderLeft: '4px solid var(--danger-color)',
          bg: 'rgba(18, 19, 26, 0.95)',
          icon: '❌',
          iconColor: 'var(--danger-color)',
        };
      case 'info':
      default:
        return {
          border: '1px solid rgba(99, 102, 241, 0.2)',
          borderLeft: '4px solid var(--accent-color)',
          bg: 'rgba(18, 19, 26, 0.95)',
          icon: 'ℹ️',
          iconColor: 'var(--accent-color)',
        };
    }
  };

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          maxWidth: '380px',
          width: '100%',
          pointerEvents: 'none',
        }}
      >
        {toasts.map((toast) => {
          const styleConfig = getToastColors(toast.type);
          return (
            <div
              key={toast.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                padding: '14px 18px',
                background: styleConfig.bg,
                border: styleConfig.border,
                borderLeft: styleConfig.borderLeft,
                borderRadius: '8px',
                boxShadow:
                  '0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.5)',
                color: 'var(--text-primary)',
                fontSize: '0.88rem',
                lineHeight: '1.4',
                pointerEvents: 'auto',
                animation: 'slideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
              }}
            >
              <div
                style={{ display: 'flex', alignItems: 'center', gap: '10px' }}
              >
                <span
                  style={{ fontSize: '1.1rem', color: styleConfig.iconColor }}
                >
                  {styleConfig.icon}
                </span>
                <span>{toast.message}</span>
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  fontSize: '1.1rem',
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'color 0.2s',
                }}
                onMouseEnter={(e) =>
                  ((e.target as HTMLButtonElement).style.color =
                    'var(--text-primary)')
                }
                onMouseLeave={(e) =>
                  ((e.target as HTMLButtonElement).style.color =
                    'var(--text-muted)')
                }
              >
                &times;
              </button>
            </div>
          );
        })}
      </div>
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </ToastContext.Provider>
  );
};
