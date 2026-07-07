import { RegisterForm } from '../components/auth/RegisterForm';

interface RegisterPageProps {
  onSwitchToLogin: () => void;
}

export function RegisterPage({ onSwitchToLogin }: RegisterPageProps) {
  return (
    <div className="auth-container">
      <div className="auth-card glass-card">
        <div className="auth-header">
          <span style={{ fontSize: '2.5rem' }}>🔍</span>
          <h1 className="gradient-text" style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800 }}>
            CodeInsight AI
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: '4px 0 0', fontSize: '0.9rem' }}>
            Create your account
          </p>
        </div>

        <RegisterForm />

        <div className="auth-footer">
          <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Already have an account?{' '}
            <button className="auth-link" onClick={onSwitchToLogin}>
              Sign in
            </button>
          </span>
        </div>
      </div>
    </div>
  );
}
