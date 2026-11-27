
function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="brand">
          <div className="brand-icon">O</div>
          <div>
            <h1>OpsPulse</h1>
            <p>Server Monitoring Platform</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-indicator"></span>
          System Initializing
        </div>
      </header>

      <main className="dashboard">
        <section className="welcome-section">
          <p className="eyebrow">INFRASTRUCTURE OVERVIEW</p>
          <h2>Welcome to OpsPulse</h2>
          <p className="subtitle">
            Your centralized Linux server monitoring and observability platform.
          </p>
        </section>

        <section className="metric-grid">
          <article className="metric-card">
            <span className="metric-label">CPU Usage</span>
            <strong className="metric-value">--%</strong>
            <span className="metric-description">Awaiting collector</span>
          </article>

          <article className="metric-card">
            <span className="metric-label">Memory Usage</span>
            <strong className="metric-value">--%</strong>
            <span className="metric-description">Awaiting collector</span>
          </article>

          <article className="metric-card">
            <span className="metric-label">Disk Usage</span>
            <strong className="metric-value">--%</strong>
            <span className="metric-description">Awaiting collector</span>
          </article>

          <article className="metric-card">
            <span className="metric-label">Active Alerts</span>
            <strong className="metric-value">0</strong>
            <span className="metric-description">No alert data yet</span>
          </article>
        </section>

        <section className="server-panel">
          <div>
            <h3>Server Inventory</h3>
            <p>No servers registered yet.</p>
          </div>
          <span className="panel-badge">Coming online</span>
        </section>
      </main>

      <footer className="app-footer">
        OpsPulse <span>·</span> Infrastructure Observability
      </footer>
    </div>
  );
}

export default App;
