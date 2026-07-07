import type { ReactNode } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Renders children only when the user is authenticated.
 * Shows a loading spinner while auth state is being restored,
 * and the fallback (or nothing) when not authenticated.
 */
export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          color: 'var(--text-secondary)',
          fontSize: '1.1rem',
          gap: '12px',
        }}
      >
        <span className="pulse-indicator" style={{ width: 12, height: 12 }} />
        Restoring session…
      </div>
    );
  }

  if (!isAuthenticated) {
    return <>{fallback ?? null}</>;
  }

  return <>{children}</>;
}
