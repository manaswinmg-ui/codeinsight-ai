import { ReviewWorkspace } from './pages/ReviewWorkspace';

function App() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '32px',
        minHeight: '90vh',
      }}
    >
      {/* App Global Header */}
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
          <span style={{ fontSize: '2rem' }}>🔍</span>
          <h1
            style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800 }}
            className="gradient-text"
          >
            CodeInsight AI
          </h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span className="pulse-indicator"></span>
          <span
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
              fontWeight: 600,
            }}
          >
            Production-Grade AI Code Review
          </span>
        </div>
      </header>

      {/* Main Workspace Page */}
      <main style={{ flexGrow: 1 }}>
        <ReviewWorkspace />
      </main>

      {/* App Global Footer */}
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
  );
}

export default App;
