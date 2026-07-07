import { LoginForm } from '../components/auth/LoginForm';

interface LoginPageProps {
  onSwitchToRegister: () => void;
}

export function LoginPage({ onSwitchToRegister }: LoginPageProps) {
  return (
    <div className="auth-container">
      <div className="auth-card glass-card">
        <div className="auth-header">
          <span style={{ fontSize: '2.5rem' }}>🔍</span>
          <h1
            className="gradient-text"
            style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800 }}
          >
            CodeInsight AI
          </h1>
          <p
            style={{
              color: 'var(--text-secondary)',
              margin: '4px 0 0',
              fontSize: '0.9rem',
            }}
          >
            Sign in to your account
          </p>
        </div>

        <LoginForm />

        <div className="auth-footer">
          <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Don&apos;t have an account?{' '}
            <button className="auth-link" onClick={onSwitchToRegister}>
              Register
            </button>
          </span>
        </div>
      </div>
    </div>
  );
}
