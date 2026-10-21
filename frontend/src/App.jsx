import { useState } from "react";
import "./App.css";

const SAMPLE_BUGGY_CODE = `# Sample Python code with classic bug patterns
def process_data(items=[], config={}):
    """Processes items and writes output."""
    file = open("output.log", "w")
    file.write("Processing started\\n")
    
    if items == None:
        return None
        print("Unreachable code after return")

    try:
        total = 100 / len(items)
    except:
        pass

    return total
`;

function App() {
  // Authentication State
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  // Workspace & Bug Analyzer State
  const [activeTab, setActiveTab] = useState("scanner"); // "scanner" | "sandbox" | "account"
  const [repoPath, setRepoPath] = useState(".");
  const [includeAi, setIncludeAi] = useState(false);
  const [repoAnalysis, setRepoAnalysis] = useState(null);
  const [isAnalyzingRepo, setIsAnalyzingRepo] = useState(false);
  const [repoError, setRepoError] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [showScoreGuide, setShowScoreGuide] = useState(false);

  // Interactive Sandbox State
  const [sandboxCode, setSandboxCode] = useState(SAMPLE_BUGGY_CODE);
  const [sandboxAnalysis, setSandboxAnalysis] = useState(null);
  const [isAnalyzingSandbox, setIsAnalyzingSandbox] = useState(false);
  const [sandboxError, setSandboxError] = useState("");
  const [copiedIndex, setCopiedIndex] = useState(null);

  const API_URL = "http://localhost:8000";

  // Login handler
  async function handleLogin(event) {
    event.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Login failed.");
      }

      setMessage("Login successful! Checking your session...");

      const sessionResponse = await fetch(`${API_URL}/auth/me`, {
        method: "GET",
        credentials: "include",
      });

      const sessionData = await sessionResponse.json();
      if (!sessionResponse.ok || !sessionData.logged_in) {
        setUser(null);
        setMessage("Login succeeded, but session was not recognized.");
        return;
      }

      setUser(sessionData);
      setMessage("");
    } catch (error) {
      console.error("Login error:", error);
      setMessage(
        error.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running on port 8000."
          : error.message
      );
    } finally {
      setLoading(false);
    }
  }

  // Sign up handler
  async function handleSignUp(event) {
    event.preventDefault();
    setMessage("");

    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Registration failed.");
      }

      setMessage("Account created successfully! You can now sign in.");
      setIsSignUp(false);
      setName("");
      setConfirmPassword("");
      setPassword("");
    } catch (error) {
      console.error("Registration error:", error);
      setMessage(
        error.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running on port 8000."
          : error.message
      );
    } finally {
      setLoading(false);
    }
  }

  // Run Repository Bug Analysis
  async function handleAnalyzeRepository(event) {
    if (event) event.preventDefault();
    setRepoError("");
    setIsAnalyzingRepo(true);

    try {
      const response = await fetch(`${API_URL}/repository/analyze-bugs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          repository_path: repoPath.trim() || ".",
          include_ai: includeAi,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to analyze repository.");
      }

      setRepoAnalysis(data);
    } catch (error) {
      console.error("Bug scan error:", error);
      setRepoError(error.message);
    } finally {
      setIsAnalyzingRepo(false);
    }
  }

  // Run Code Snippet Analysis
  async function handleAnalyzeSnippet(event) {
    if (event) event.preventDefault();
    setSandboxError("");
    setIsAnalyzingSandbox(true);

    try {
      const response = await fetch(`${API_URL}/code/analyze-snippet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          code: sandboxCode,
          filename: "sandbox.py",
          include_ai: includeAi,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Failed to analyze code snippet.");
      }

      setSandboxAnalysis(data);
    } catch (error) {
      console.error("Sandbox scan error:", error);
      setSandboxError(error.message);
    } finally {
      setIsAnalyzingSandbox(false);
    }
  }

  // Download REPORT button handler
  function handleDownloadReport() {
    if (!repoAnalysis || !repoAnalysis.report_markdown) {
      return;
    }

    const blob = new Blob([repoAnalysis.report_markdown], {
      type: "text/markdown;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `BUG_REPORT_${repoAnalysis.repository_name || "RepoGuide"}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // Copy proposed fix to clipboard
  function handleCopyFix(fixText, idx) {
    if (!fixText) return;
    navigator.clipboard.writeText(fixText);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  }

  // Filter findings
  const displayedRepoFindings = repoAnalysis?.findings
    ? repoAnalysis.findings.filter((f) =>
        severityFilter === "ALL" ? true : f.severity === severityFilter
      )
    : [];

  return (
    <main className="repoguide">
      <nav className="navbar">
        <a className="brand" href="/">
          <span className="brand-icon">R</span>
          RepoGuide<span className="brand-dot">.</span>
        </a>

        <div className="nav-right">
          <span className="nav-label">Code Quality & Onboarding Intelligence</span>
          {user && (
            <button
              className="btn-signout"
              onClick={() => {
                setUser(null);
                setRepoAnalysis(null);
                setSandboxAnalysis(null);
              }}
            >
              Sign out
            </button>
          )}
        </div>
      </nav>

      {!user ? (
        // Public Authentication Layout
        <section className="login-layout">
          <div className="welcome-panel">
            <span className="eyebrow">YOUR NEXT BUILD STARTS HERE</span>
            <h1>
              Understand code.<br />
              <span>Ship smarter.</span>
            </h1>
            <p className="welcome-text">
              Your AI-powered workspace to inspect repositories, detect hidden bugs,
              improve code quality, and help developers onboard faster.
            </p>

            <div className="feature-list">
              <div className="feature">
                <span className="feature-icon">🔍</span>
                <div>
                  <strong>AST Static Bug Detection</strong>
                  <p>Catch mutable defaults, resource leaks, and syntax errors safely.</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">⚡</span>
                <div>
                  <strong>Non-Destructive Fixes</strong>
                  <p>Preview syntax-validated code fixes before making any changes.</p>
                </div>
              </div>
              <div className="feature">
                <span className="feature-icon">📄</span>
                <div>
                  <strong>Exportable Reports</strong>
                  <p>Download comprehensive bug and code quality Markdown reports.</p>
                </div>
              </div>
            </div>

            <div className="welcome-footer">
              MADE FOR THE NEXT GENERATION OF DEVELOPERS
            </div>
          </div>

          <div className="form-panel">
            <div className="form-heading">
              <span className="form-kicker">
                {isSignUp ? "GET STARTED" : "WELCOME BACK"}
              </span>
              <h2>{isSignUp ? "Create your account" : "Sign in to RepoGuide"}</h2>
              <p>
                {isSignUp
                  ? "Join RepoGuide to analyze repositories and detect bugs."
                  : "Enter your account details to access the workspace."}
              </p>
            </div>

            <form onSubmit={isSignUp ? handleSignUp : handleLogin}>
              {isSignUp && (
                <>
                  <label htmlFor="name">Full name</label>
                  <input
                    id="name"
                    type="text"
                    placeholder="Enter your full name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                </>
              )}

              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <div className="password-label">
                <label htmlFor="password">Password</label>
              </div>
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              {isSignUp && (
                <>
                  <label htmlFor="confirmPassword">Confirm password</label>
                  <input
                    id="confirmPassword"
                    type="password"
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </>
              )}

              <button className="login-button" type="submit" disabled={loading}>
                {loading
                  ? isSignUp ? "Creating account..." : "Signing in..."
                  : isSignUp ? "Create Account" : "Sign in"}
                {!loading && <span aria-hidden="true"> →</span>}
              </button>
            </form>

            <div className="auth-toggle">
              {isSignUp ? "Already have an account?" : "Don't have an account?"}
              <button
                type="button"
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setMessage("");
                }}
              >
                {isSignUp ? "Sign in" : "Sign up"}
              </button>
            </div>

            {message && (
              <p className="status-message" role="status">
                {message}
              </p>
            )}
          </div>
        </section>
      ) : (
        // Authenticated Developer Workspace
        <section className="workspace-container">
          <header className="workspace-header">
            <div>
              <span className="eyebrow">DEVELOPER WORKSPACE</span>
              <h2>Bug Detection & Quality Engine</h2>
              <p className="workspace-sub">
                Logged in as <strong>{user.email || user.user_id}</strong> &bull; Role:{" "}
                <span className="badge-role">{user.role || "Developer"}</span>
              </p>
            </div>

            {/* Navigation Tabs */}
            <div className="workspace-tabs">
              <button
                className={`tab-btn ${activeTab === "scanner" ? "active" : ""}`}
                onClick={() => setActiveTab("scanner")}
              >
                🔍 Repository Bug Scanner
              </button>
              <button
                className={`tab-btn ${activeTab === "sandbox" ? "active" : ""}`}
                onClick={() => setActiveTab("sandbox")}
              >
                ⚡ Interactive Code Sandbox
              </button>
              <button
                className={`tab-btn ${activeTab === "account" ? "active" : ""}`}
                onClick={() => setActiveTab("account")}
              >
                👤 Session Info
              </button>
            </div>
          </header>

          {/* TAB 1: REPOSITORY BUG SCANNER */}
          {activeTab === "scanner" && (
            <div className="tab-content">
              <div className="scan-control-card">
                <form onSubmit={handleAnalyzeRepository} className="scan-form">
                  <div className="input-group">
                    <label htmlFor="repoPath">Repository Directory</label>
                    <input
                      id="repoPath"
                      type="text"
                      value={repoPath}
                      onChange={(e) => setRepoPath(e.target.value)}
                      placeholder="e.g. . or backend"
                    />
                  </div>

                  <div className="checkbox-group">
                    <input
                      id="includeAi"
                      type="checkbox"
                      checked={includeAi}
                      onChange={(e) => setIncludeAi(e.target.checked)}
                    />
                    <label htmlFor="includeAi">
                      Enrich with AI Explanations (requires GEMINI_API_KEY in backend/.env)
                    </label>
                  </div>

                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={isAnalyzingRepo}
                  >
                    {isAnalyzingRepo ? "Analyzing AST & Scanning Code..." : "Run Bug Analysis"}
                  </button>
                </form>

                {repoError && <div className="error-banner">{repoError}</div>}
              </div>

              {repoAnalysis && (
                <div className="results-panel">
                  {/* Summary Metric Cards */}
                  <div className="metrics-row">
                    <div className="metric-card score-card">
                      <span className="metric-title">Code Health Score</span>
                      <div
                        className={`score-value ${
                          repoAnalysis.health_score >= 80
                            ? "score-good"
                            : repoAnalysis.health_score >= 50
                            ? "score-fair"
                            : "score-poor"
                        }`}
                      >
                        {repoAnalysis.health_score}
                        <span className="score-max">/100</span>
                      </div>
                      <span className="score-label">
                        {repoAnalysis.health_score >= 80
                          ? "Good Quality"
                          : repoAnalysis.health_score >= 50
                          ? "Needs Improvement"
                          : "Action Required"}
                      </span>
                      <button
                        type="button"
                        className="btn-score-guide-toggle"
                        onClick={() => setShowScoreGuide(!showScoreGuide)}
                      >
                        {showScoreGuide ? "▲ Hide Guide" : "ℹ️ How it's scored"}
                      </button>
                    </div>

                    <div className="metric-card">
                      <span className="metric-title">Python Files</span>
                      <span className="metric-number">
                        {repoAnalysis.total_python_files}
                      </span>
                      <span className="metric-desc">
                        {repoAnalysis.total_python_lines.toLocaleString()} lines analyzed
                      </span>
                    </div>

                    <div className="metric-card">
                      <span className="metric-title">Total Findings</span>
                      <span className="metric-number">
                        {repoAnalysis.total_findings}
                      </span>
                      <span className="metric-desc">Code issues detected</span>
                    </div>

                    <div className="metric-card breakdown-card">
                      <span className="metric-title">Severity Breakdown</span>
                      <div className="pill-group">
                        <span className="pill pill-critical">
                          Critical: {repoAnalysis.severity_breakdown.Critical || 0}
                        </span>
                        <span className="pill pill-high">
                          High: {repoAnalysis.severity_breakdown.High || 0}
                        </span>
                        <span className="pill pill-medium">
                          Medium: {repoAnalysis.severity_breakdown.Medium || 0}
                        </span>
                        <span className="pill pill-low">
                          Low: {repoAnalysis.severity_breakdown.Low || 0}
                        </span>
                      </div>
                    </div>
                  </div>

                  {showScoreGuide && (
                    <div className="score-guide-panel">
                      <div className="guide-header">
                        <h4>Code Health Scoring System & Severity Reference Guide</h4>
                        <span className="guide-sub">Base score starts at 100 points. Points are deducted based on finding risk.</span>
                      </div>
                      <div className="guide-table-wrapper">
                        <table className="guide-table">
                          <thead>
                            <tr>
                              <th>Severity Tier</th>
                              <th>Point Deduction</th>
                              <th>Impact & Hazard Description</th>
                              <th>Detected Bug Patterns</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td><span className="severity-badge sev-critical">CRITICAL</span></td>
                              <td className="deduct-pts">-20 pts</td>
                              <td>Confirmed syntax/compilation failure. Python cannot execute or import this file.</td>
                              <td><code>SyntaxError</code> (missing colons, broken brackets, invalid indentation)</td>
                            </tr>
                            <tr>
                              <td><span className="severity-badge sev-high">HIGH</span></td>
                              <td className="deduct-pts">-10 pts</td>
                              <td>Severe runtime hazards, resource leaks, or masked system termination signals.</td>
                              <td><code>open()</code> without <code>with</code> context manager, Bare <code>except:</code></td>
                            </tr>
                            <tr>
                              <td><span className="severity-badge sev-medium">MEDIUM</span></td>
                              <td className="deduct-pts">-5 pts</td>
                              <td>Silent failure traps and state leakage persisting across function calls.</td>
                              <td>Mutable default arguments (<code>x=[]</code>, <code>x=&#123;&#125;</code>), <code>except Exception: pass</code></td>
                            </tr>
                            <tr>
                              <td><span className="severity-badge sev-low">LOW</span></td>
                              <td className="deduct-pts">-2 pts</td>
                              <td>Code hygiene, PEP 8 identity checks, and global built-in collision.</td>
                              <td><code>== None</code> vs <code>is None</code>, Variable shadowing (<code>list</code>, <code>dict</code>)</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Actions & Filters Bar */}
                  <div className="action-bar">
                    <div className="filter-group">
                      <span className="filter-label">Filter by Severity:</span>
                      {["ALL", "Critical", "High", "Medium", "Low"].map((sev) => (
                        <button
                          key={sev}
                          className={`filter-btn ${
                            severityFilter === sev ? "active" : ""
                          }`}
                          onClick={() => setSeverityFilter(sev)}
                        >
                          {sev}
                        </button>
                      ))}
                    </div>

                    {/* Exact user-requested button name */}
                    <button
                      className="btn-download-report"
                      onClick={handleDownloadReport}
                      title="Download Markdown Quality & Bug Report"
                    >
                      📥 Download REPORT
                    </button>
                  </div>

                  {/* Findings Cards List */}
                  <div className="findings-container">
                    <h3>
                      Detailed Code Findings ({displayedRepoFindings.length} shown)
                    </h3>

                    {displayedRepoFindings.length === 0 ? (
                      <div className="empty-state">
                        🎉 No code issues found matching this filter!
                      </div>
                    ) : (
                      displayedRepoFindings.map((finding, idx) => (
                        <div
                          key={idx}
                          className={`finding-card severity-${finding.severity.toLowerCase()}`}
                        >
                          <div className="finding-header">
                            <span
                              className={`severity-badge sev-${finding.severity.toLowerCase()}`}
                            >
                              {finding.severity}
                            </span>
                            <span className="category-tag">{finding.category}</span>
                            <h4 className="finding-title">{finding.title}</h4>
                            <span className="potential-tag">
                              {finding.is_potential
                                ? "Heuristic Pattern"
                                : "Confirmed Error"}
                            </span>
                          </div>

                          <div className="finding-location">
                            📍 <strong>{finding.file}</strong> &bull; Line {finding.line} (Col {finding.column})
                          </div>

                          {finding.evidence && (
                            <div className="code-block-wrapper">
                              <span className="code-label">Offending Code</span>
                              <pre className="code-block">
                                <code>{finding.evidence}</code>
                              </pre>
                            </div>
                          )}

                          <div className="finding-explanation">
                            <strong>Why this is a problem:</strong>
                            <p>{finding.explanation}</p>
                          </div>

                          {finding.ai_explanation && (
                            <div className="ai-explanation-box">
                              <span className="ai-badge">🤖 AI Explanation</span>
                              <p>{finding.ai_explanation}</p>
                            </div>
                          )}

                          {finding.proposed_fix && (
                            <div className="proposed-fix-box">
                              <div className="fix-header">
                                <span className="fix-label">
                                  Proposed Fix (Syntax Validated)
                                </span>
                                <button
                                  type="button"
                                  className="btn-copy-fix"
                                  onClick={() =>
                                    handleCopyFix(finding.proposed_fix, `repo-${idx}`)
                                  }
                                >
                                  {copiedIndex === `repo-${idx}`
                                    ? "✓ Copied!"
                                    : "📋 Copy Fixed Code"}
                                </button>
                              </div>
                              <pre className="code-block fix-code">
                                <code>{finding.proposed_fix}</code>
                              </pre>
                            </div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: INTERACTIVE PYTHON SANDBOX */}
          {activeTab === "sandbox" && (
            <div className="tab-content sandbox-layout">
              <div className="sandbox-editor-panel">
                <div className="panel-header">
                  <h3>Python Code Sandbox</h3>
                  <span className="panel-hint">
                    Type or paste any Python snippet to test our AST bug detection live.
                  </span>
                </div>

                <textarea
                  className="code-textarea"
                  value={sandboxCode}
                  onChange={(e) => setSandboxCode(e.target.value)}
                  placeholder="Paste Python code here..."
                  rows={16}
                  spellCheck={false}
                />

                <div className="sandbox-actions">
                  <button
                    className="btn-primary"
                    onClick={handleAnalyzeSnippet}
                    disabled={isAnalyzingSandbox}
                  >
                    {isAnalyzingSandbox ? "Analyzing Snippet..." : "⚡ Analyze Code Snippet"}
                  </button>

                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setSandboxCode(SAMPLE_BUGGY_CODE)}
                  >
                    Load Sample Buggy Code
                  </button>
                </div>

                {sandboxError && <div className="error-banner">{sandboxError}</div>}
              </div>

              <div className="sandbox-results-panel">
                <div className="panel-header">
                  <h3>Analysis Results</h3>
                  {sandboxAnalysis && (
                    <span className="results-count">
                      {sandboxAnalysis.findings_count} issue(s) detected across{" "}
                      {sandboxAnalysis.total_lines} lines
                    </span>
                  )}
                </div>

                {!sandboxAnalysis ? (
                  <div className="empty-state">
                    Click <strong>"Analyze Code Snippet"</strong> to run AST static inspection.
                  </div>
                ) : sandboxAnalysis.findings_count === 0 ? (
                  <div className="clean-state">
                    🎉 <strong>Clean Code!</strong> No syntax errors or bug patterns found.
                  </div>
                ) : (
                  <div className="sandbox-findings-list">
                    {sandboxAnalysis.findings.map((finding, idx) => (
                      <div
                        key={idx}
                        className={`finding-card severity-${finding.severity.toLowerCase()}`}
                      >
                        <div className="finding-header">
                          <span
                            className={`severity-badge sev-${finding.severity.toLowerCase()}`}
                          >
                            {finding.severity}
                          </span>
                          <span className="category-tag">{finding.category}</span>
                          <h4 className="finding-title">{finding.title}</h4>
                        </div>

                        <div className="finding-location">
                          Line {finding.line} (Col {finding.column})
                        </div>

                        {finding.evidence && (
                          <pre className="code-block">
                            <code>{finding.evidence}</code>
                          </pre>
                        )}

                        <p className="finding-explanation-text">
                          {finding.explanation}
                        </p>

                        {finding.proposed_fix && (
                          <div className="proposed-fix-box">
                            <div className="fix-header">
                              <span className="fix-label">Suggested Fix</span>
                              <button
                                type="button"
                                className="btn-copy-fix"
                                onClick={() =>
                                  handleCopyFix(finding.proposed_fix, `sandbox-${idx}`)
                                }
                              >
                                {copiedIndex === `sandbox-${idx}`
                                  ? "✓ Copied!"
                                  : "📋 Copy Fixed Code"}
                              </button>
                            </div>
                            <pre className="code-block fix-code">
                              <code>{finding.proposed_fix}</code>
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: ACCOUNT & SESSION */}
          {activeTab === "account" && (
            <div className="tab-content account-tab">
              <div className="account-card">
                <div className="account-icon">✓</div>
                <h3>Active Developer Session</h3>
                <p>Your session cookie is authenticated with FastAPI and MongoDB.</p>

                <div className="account-info-grid">
                  <div>
                    <span className="info-label">User ID</span>
                    <strong className="info-val">{user.user_id}</strong>
                  </div>
                  <div>
                    <span className="info-label">Email</span>
                    <strong className="info-val">{email || "Authenticated User"}</strong>
                  </div>
                  <div>
                    <span className="info-label">Role</span>
                    <strong className="info-val">{user.role || "Developer"}</strong>
                  </div>
                  <div>
                    <span className="info-label">Engine Module</span>
                    <strong className="info-val">AST Static Analyzer v1.0</strong>
                  </div>
                </div>

                <button
                  className="btn-signout-main"
                  onClick={() => {
                    setUser(null);
                    setRepoAnalysis(null);
                  }}
                >
                  Sign Out of Session
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      <footer className="page-footer">
        <span>© 2026 RepoGuide &bull; Automated Code Quality & Onboarding</span>
        <span>Built with Python AST Static Analysis & React</span>
      </footer>
    </main>
  );
}

export default App;
