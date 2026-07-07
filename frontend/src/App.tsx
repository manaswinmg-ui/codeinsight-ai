import { useState } from 'react';
import { ReviewWorkspace } from './pages/ReviewWorkspace';
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { ReviewHistoryPage } from './pages/ReviewHistory/ReviewHistoryPage';
import { RepositoryDashboard } from './pages/Repository/RepositoryDashboard';
import { ToastProvider } from './components/shared/ToastProvider';
import { useAuth } from './hooks/useAuth';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { UserMenu } from './components/auth/UserMenu';

type Page = 'dashboard' | 'new-review' | 'history' | 'repository' | 'login' | 'register';

function App() {
  const { isAuthenticated, isLoading } = useAuth();
  const [activePage, setActivePage] = useState<Page>('dashboard');
  const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null);
  const [devMode, setDevMode] = useState<boolean>(false);
  const [authPage, setAuthPage] = useState<'login' | 'register'>('login');

  const handleSelectReview = (reviewId: number) => {
    setSelectedReviewId(reviewId);
    setActivePage('new-review');
  };

  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: 'var(--bg-primary)',
          color: 'var(--text-secondary)',
          fontSize: '1.2rem',
          gap: '16px',
        }}
      >
        <span className="pulse-indicator" style={{ width: '16px', height: '16px' }} />
        Initializing CodeInsight AI...
      </div>
    );
  }

  if (!isAuthenticated) {
    return authPage === 'login' ? (
      <LoginPage onSwitchToRegister={() => setAuthPage('register')} />
    ) : (
      <RegisterPage onSwitchToLogin={() => setAuthPage('login')} />
    );
  }

  const renderContent = () => {
    switch (activePage) {
      case 'dashboard':
        return (
          <DashboardPage
            onNavigate={setActivePage}
            onSelectReview={handleSelectReview}
          />
        );
      case 'new-review':
        return (
          <ReviewWorkspace
            initialReviewId={selectedReviewId}
            onClearInitialReviewId={() => setSelectedReviewId(null)}
            showDebug={devMode}
          />
        );
      case 'history':
        return <ReviewHistoryPage onSelectReview={handleSelectReview} />;
      case 'repository':
        return <RepositoryDashboard onSelectReview={handleSelectReview} />;
      default:
        return null;
    }
  };

  return (
    <ToastProvider>
      <div
        style={{
          display: 'flex',
          gap: '32px',
          minHeight: '92vh',
          alignItems: 'stretch',
        }}
      >
        {/* Navigation Sidebar */}
        <aside
          className="glass-card"
          style={{
            width: '240px',
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            padding: '24px',
            alignSelf: 'flex-start',
            position: 'sticky',
            top: '2rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              borderBottom: '1px solid var(--border-color)',
              paddingBottom: '16px',
            }}
          >
            <span style={{ fontSize: '1.8rem' }}>🔍</span>
            <h2
              style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800 }}
              className="gradient-text"
            >
              CodeInsight AI
            </h2>
          </div>

          <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {[
              { id: 'dashboard', label: '📊 Dashboard' },
              { id: 'new-review', label: '✨ New Review' },
              { id: 'history', label: '🕒 Review History' },
              { id: 'repository', label: '📦 Repo Review' },
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id as Page)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background:
                    activePage === item.id
                      ? 'var(--accent-color)'
                      : 'transparent',
                  color:
                    activePage === item.id ? '#fff' : 'var(--text-secondary)',
                  border: 'none',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  transition: 'background 0.2s, color 0.2s',
                }}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* Developer Mode Toggle in Sidebar */}
          <div
            style={{
              marginTop: 'auto',
              borderTop: '1px solid var(--border-color)',
              paddingTop: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
            }}
          >
            <input
              type="checkbox"
              id="dev-mode-toggle"
              checked={devMode}
              onChange={(e) => setDevMode(e.target.checked)}
              style={{
                width: '16px',
                height: '16px',
                accentColor: 'var(--accent-color)',
                cursor: 'pointer',
              }}
            />
            <label
              htmlFor="dev-mode-toggle"
              style={{
                fontSize: '0.85rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                userSelect: 'none',
              }}
            >
              🛠️ Developer Mode
            </label>
          </div>
        </aside>

        {/* Main Content Area */}
        <div
          style={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            gap: '32px',
            minWidth: 0,
          }}
        >
          {/* Top Header */}
          <header
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderBottom: '1px solid var(--border-color)',
              paddingBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '1.5rem' }}>
                {activePage === 'dashboard'
                  ? '📊'
                  : activePage === 'new-review'
                    ? '✨'
                    : activePage === 'history'
                      ? '🕒'
                      : '📦'}
              </span>
              <h1 style={{ margin: 0, fontSize: '1.4rem', fontWeight: 800 }}>
                {activePage === 'dashboard'
                  ? 'Engineering Dashboard'
                  : activePage === 'new-review'
                    ? 'Code Review Workspace'
                    : activePage === 'history'
                      ? 'Review History Logs'
                      : 'Repository Review Logs'}
              </h1>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <UserMenu />
            </div>
          </header>

          {/* Render Active View */}
          <main style={{ flexGrow: 1 }}>{renderContent()}</main>

          {/* Footer */}
          <footer
            style={{
              borderTop: '1px solid var(--border-color)',
              paddingTop: '16px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.85rem',
              marginTop: 'auto',
            }}
          >
            CodeInsight AI © {new Date().getFullYear()} — Built for Production
            Engineering Workflows
          </footer>
        </div>
      </div>
    </ToastProvider>
  );
}

export default App;
