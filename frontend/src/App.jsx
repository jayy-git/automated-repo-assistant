import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

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
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  const [activeTab, setActiveTab] = useState("dashboard");
  const [repoPath, setRepoPath] = useState(".");
  const [includeAi, setIncludeAi] = useState(false);
  const [repoAnalysis, setRepoAnalysis] = useState(null);
  const [isAnalyzingRepo, setIsAnalyzingRepo] = useState(false);
  const [repoError, setRepoError] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [showScoreGuide, setShowScoreGuide] = useState(false);

  const [sandboxCode, setSandboxCode] = useState(SAMPLE_BUGGY_CODE);
  const [sandboxAnalysis, setSandboxAnalysis] = useState(null);
  const [isAnalyzingSandbox, setIsAnalyzingSandbox] = useState(false);
  const [sandboxError, setSandboxError] = useState("");
  const [copiedIndex, setCopiedIndex] = useState(null);

  async function readResponse(response, fallback) {
    let data = {};
    try {
      data = await response.json();
    } catch {
      data = {};
    }
    if (!response.ok) throw new Error(data.detail || fallback);
    return data;
  }

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
      await readResponse(response, "Login failed.");
      const sessionResponse = await fetch(`${API_URL}/auth/me`, {
        credentials: "include",
      });
      const sessionData = await readResponse(sessionResponse, "Could not verify your session.");
      if (!sessionData.logged_in) {
        setUser(null);
        setMessage("Login succeeded, but your session was not recognized. Please try again.");
        return;
      }
      setUser(sessionData);
      setMessage("");
      setActiveTab("dashboard");
    } catch (error) {
      setMessage(error.message === "Failed to fetch"
        ? "Cannot connect to the backend. Make sure FastAPI is running on port 8000."
        : error.message);
    } finally {
      setLoading(false);
    }
  }

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
      await readResponse(response, "Registration failed.");
      setMessage("Account created successfully. You can now sign in.");
      setIsSignUp(false);
      setName("");
      setConfirmPassword("");
      setPassword("");
    } catch (error) {
      setMessage(error.message === "Failed to fetch"
        ? "Cannot connect to the backend. Make sure FastAPI is running on port 8000."
        : error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAnalyzeRepository(event) {
    event?.preventDefault();
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
      const data = await readResponse(response, "Failed to analyze repository.");
      setRepoAnalysis(data);
    } catch (error) {
      setRepoError(error.message === "Failed to fetch"
        ? "Cannot connect to the backend. Check that FastAPI is running on port 8000."
        : error.message);
    } finally {
      setIsAnalyzingRepo(false);
    }
  }

  async function handleAnalyzeSnippet(event) {
    event?.preventDefault();
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
      setSandboxAnalysis(await readResponse(response, "Failed to analyze code snippet."));
    } catch (error) {
      setSandboxError(error.message === "Failed to fetch"
        ? "Cannot connect to the backend. Check that FastAPI is running on port 8000."
        : error.message);
    } finally {
      setIsAnalyzingSandbox(false);
    }
  }

  async function handleSignOut() {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.warn("Sign-out request could not be completed:", error);
    } finally {
      setUser(null);
      setRepoAnalysis(null);
      setSandboxAnalysis(null);
      setActiveTab("dashboard");
      setMessage("");
      setPassword("");
    }
  }

  function handleDownloadReport() {
    if (!repoAnalysis?.report_markdown) return;
    const blob = new Blob([repoAnalysis.report_markdown], {
      type: "text/markdown;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `BUG_REPORT_${repoAnalysis.repository_name || "RepoGuide"}.md`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  async function handleCopyFix(text, index) {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      window.setTimeout(() => setCopiedIndex(null), 1800);
    } catch {
      setCopiedIndex(null);
    }
  }

  const findings = Array.isArray(repoAnalysis?.findings) ? repoAnalysis.findings : [];
  const displayedRepoFindings = findings.filter((finding) =>
    severityFilter === "ALL" ? true : finding.severity === severityFilter
  );
  const severityBreakdown = repoAnalysis?.severity_breakdown || {};
  const displayName = user?.name || user?.email || user?.user_id || "Developer";

  function SeverityPill({ severity, count }) {
    return <span className={`severity-pill severity-${severity.toLowerCase()}`}>{severity}: {count || 0}</span>;
  }

  function FindingCard({ finding, index, prefix = "repo" }) {
    const key = `${prefix}-${index}`;
    return (
      <article className={`finding-card severity-border-${(finding.severity || "low").toLowerCase()}`} key={key}>
        <div className="finding-topline">
          <span className={`severity-badge severity-${(finding.severity || "low").toLowerCase()}`}>{finding.severity || "Info"}</span>
          <span className="category-tag">{finding.category || "Code quality"}</span>
          {finding.is_potential && <span className="potential-tag">Heuristic pattern</span>}
        </div>
        <h3 className="finding-title">{finding.title || "Finding"}</h3>
        {finding.file && <p className="finding-location">📍 {finding.file} · Line {finding.line ?? "—"}{finding.column != null ? ` · Column ${finding.column}` : ""}</p>}
        {finding.evidence && <div className="code-block-wrapper"><span className="code-label">Detected code</span><pre className="code-block"><code>{finding.evidence}</code></pre></div>}
        <div className="finding-explanation"><strong>Why this matters</strong><p>{finding.explanation || "No additional explanation was provided."}</p></div>
        {finding.ai_explanation && <div className="ai-explanation-box"><strong>AI explanation</strong><p>{finding.ai_explanation}</p></div>}
        {finding.proposed_fix && <div className="proposed-fix-box">
          <div className="fix-header"><strong>Suggested fix</strong><button className="btn-copy-fix" type="button" onClick={() => handleCopyFix(finding.proposed_fix, key)}>{copiedIndex === key ? "✓ Copied" : "Copy fix"}</button></div>
          <pre className="code-block fix-code"><code>{finding.proposed_fix}</code></pre>
        </div>}
      </article>
    );
  }

  return (
    <main className="repoguide">
      <nav className="navbar">
        <a className="brand" href="/" onClick={(event) => { event.preventDefault(); if (user) setActiveTab("dashboard"); }}>
          <span className="brand-icon">R</span><span>RepoGuide<span className="brand-dot">.</span></span>
        </a>
        <div className="nav-right">
          <span className="nav-label">Code Quality &amp; Onboarding Intelligence</span>
          {user && <div className="nav-user"><span className="avatar">{String(displayName).charAt(0).toUpperCase()}</span><span>{displayName}</span><button className="btn-signout" onClick={handleSignOut}>Sign out</button></div>}
        </div>
      </nav>

      {!user ? (
        <section className="login-layout">
          <div className="welcome-panel">
            <div className="welcome-content">
              <span className="eyebrow">YOUR NEXT BUILD STARTS HERE</span>
              <h1>Understand code.<br /><span>Ship smarter.</span></h1>
              <p className="welcome-text">Your AI-powered workspace to inspect repositories, detect hidden bugs, improve code quality, and help developers onboard faster.</p>
              <div className="feature-list">
                <div className="feature"><span className="feature-icon">⌕</span><div><strong>AST static bug detection</strong><p>Catch mutable defaults, resource leaks, and syntax errors safely.</p></div></div>
                <div className="feature"><span className="feature-icon">↗</span><div><strong>Non-destructive fixes</strong><p>Preview syntax-validated code fixes before making changes.</p></div></div>
                <div className="feature"><span className="feature-icon">▤</span><div><strong>Exportable reports</strong><p>Download clear bug and code-quality reports in Markdown.</p></div></div>
              </div>
            </div>
            <div className="welcome-footer"><span className="footer-mark">R</span> BUILT FOR PEOPLE WHO BUILD</div>
          </div>

          <div className="form-panel-wrap">
            <div className="form-panel">
              <div className="form-brand-mark">R</div>
              <div className="form-heading">
                <span className="form-kicker">{isSignUp ? "CREATE YOUR WORKSPACE" : "WELCOME BACK"}</span>
                <h2>{isSignUp ? "Create your account" : "Sign in to RepoGuide"}</h2>
                <p>{isSignUp ? "Set up your account and start exploring your code." : "Enter your details to continue to your workspace."}</p>
              </div>
              <form onSubmit={isSignUp ? handleSignUp : handleLogin} className="auth-form">
                {isSignUp && <div className="field-group"><label htmlFor="name">Full name</label><input id="name" type="text" autoComplete="name" placeholder="Enter your full name" value={name} onChange={(event) => setName(event.target.value)} required /></div>}
                <div className="field-group"><label htmlFor="email">Email address</label><input id="email" type="email" autoComplete="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required /></div>
                <div className="field-group"><div className="password-label"><label htmlFor="password">Password</label>{!isSignUp && <span>Keep it secure</span>}</div><input id="password" type="password" autoComplete={isSignUp ? "new-password" : "current-password"} placeholder="Enter your password" value={password} onChange={(event) => setPassword(event.target.value)} required /></div>
                {isSignUp && <div className="field-group"><label htmlFor="confirmPassword">Confirm password</label><input id="confirmPassword" type="password" autoComplete="new-password" placeholder="Re-enter your password" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required /></div>}
                <button className="login-button" type="submit" disabled={loading}>{loading ? (isSignUp ? "Creating account…" : "Signing in…") : (isSignUp ? "Create account" : "Sign in")}<span aria-hidden="true">{loading ? "" : "→"}</span></button>
              </form>
              <div className="auth-toggle"><span>{isSignUp ? "Already have an account?" : "New to RepoGuide?"}</span><button type="button" onClick={() => { setIsSignUp(!isSignUp); setMessage(""); }}>{isSignUp ? "Sign in" : "Create an account"}</button></div>
              {message && <p className={`status-message ${/successfully/i.test(message) ? "status-success" : ""}`} role="status">{message}</p>}
              <p className="form-security-note"><span>●</span> Secure session · Your workspace, your code</p>
            </div>
          </div>
        </section>
      ) : (
        <section className="workspace-container">
          <aside className="app-sidebar">
            <div className="sidebar-brand"><div className="sidebar-logo">R</div><div><strong>RepoGuide</strong><span>Developer workspace</span></div></div>
            <span className="sidebar-section-label">WORKSPACE</span>
            <nav className="sidebar-navigation" aria-label="Workspace navigation">
              <button type="button" className={`sidebar-link ${activeTab === "dashboard" ? "active" : ""}`} onClick={() => setActiveTab("dashboard")}><span className="sidebar-icon">▦</span>Dashboard</button>
              <button type="button" className={`sidebar-link ${activeTab === "scanner" ? "active" : ""}`} onClick={() => setActiveTab("scanner")}><span className="sidebar-icon">⌕</span>Analyze repository</button>
              <button type="button" className={`sidebar-link ${activeTab === "sandbox" ? "active" : ""}`} onClick={() => setActiveTab("sandbox")}><span className="sidebar-icon">⌘</span>Code sandbox</button>
              <button type="button" className={`sidebar-link ${activeTab === "account" ? "active" : ""}`} onClick={() => setActiveTab("account")}><span className="sidebar-icon">♙</span>Account &amp; session</button>
            </nav>
            <div className="sidebar-bottom"><span className="online-dot" /><div><strong>Workspace active</strong><span>Connected to RepoGuide</span></div></div>
          </aside>

          <div className="workspace-main">
            <header className="workspace-topbar"><div><span className="breadcrumb">WORKSPACE <span>/</span> {activeTab === "scanner" ? "REPOSITORY ANALYSIS" : activeTab === "sandbox" ? "CODE SANDBOX" : activeTab === "account" ? "ACCOUNT" : "OVERVIEW"}</span><h1>{activeTab === "scanner" ? "Repository analysis" : activeTab === "sandbox" ? "Code sandbox" : activeTab === "account" ? "Account & session" : "Dashboard"}</h1></div><div className="topbar-user"><span className="avatar">{String(displayName).charAt(0).toUpperCase()}</span><div><strong>{displayName}</strong><span>{user.role || "Developer"}</span></div></div></header>

            {activeTab === "dashboard" && <div className="page-content dashboard-page">
              <div className="dashboard-welcome"><div><span className="eyebrow">YOUR DEVELOPMENT OVERVIEW</span><h2>Good to have you here 👋</h2><p>Understand your codebase, detect bugs, and improve code quality from one workspace.</p></div><button className="btn-primary" type="button" onClick={() => setActiveTab("scanner")}>＋ Analyze repository</button></div>
              <div className="dashboard-stats-grid">
                <div className="dashboard-stat-card"><div className="stat-card-top"><span className="stat-icon icon-purple">◈</span><span className="stat-caption">LATEST SCAN</span></div><span className="metric-title">Code health</span><strong className="dashboard-stat-value">{repoAnalysis ? `${repoAnalysis.health_score ?? "—"}` : "—"}<small>{repoAnalysis ? "/100" : ""}</small></strong><span className="metric-desc">{repoAnalysis ? "Latest repository score" : "Run your first scan"}</span></div>
                <div className="dashboard-stat-card"><div className="stat-card-top"><span className="stat-icon icon-coral">⌁</span><span className="stat-caption">DETECTED</span></div><span className="metric-title">Total findings</span><strong className="dashboard-stat-value">{repoAnalysis ? (repoAnalysis.total_findings ?? findings.length) : "—"}</strong><span className="metric-desc">{repoAnalysis ? "From latest scan" : "No scan data yet"}</span></div>
                <div className="dashboard-stat-card"><div className="stat-card-top"><span className="stat-icon icon-blue">▤</span><span className="stat-caption">SCANNED</span></div><span className="metric-title">Python files</span><strong className="dashboard-stat-value">{repoAnalysis ? (repoAnalysis.total_python_files ?? "—") : "—"}</strong><span className="metric-desc">{repoAnalysis ? `${(repoAnalysis.total_python_lines ?? 0).toLocaleString()} lines analyzed` : "Waiting for first scan"}</span></div>
                <div className="dashboard-stat-card"><div className="stat-card-top"><span className="stat-icon icon-amber">!</span><span className="stat-caption">NEEDS ATTENTION</span></div><span className="metric-title">Critical issues</span><strong className="dashboard-stat-value">{repoAnalysis ? (severityBreakdown.Critical ?? severityBreakdown.CRITICAL ?? 0) : "—"}</strong><span className="metric-desc">{repoAnalysis ? "From latest scan" : "No scan data yet"}</span></div>
              </div>
              <div className="section-heading"><div><h2>Your tools</h2><p>Pick up where you need to work.</p></div><span className="subtle-badge">2 tools available</span></div>
              <div className="dashboard-content-grid">
                <article className="tool-card"><div className="tool-card-icon icon-purple">⌕</div><span className="card-overline">REPOSITORY INTELLIGENCE</span><h3>Analyze your codebase</h3><p>Run the Python AST analyzer to identify potential bugs, review severity, and inspect suggested fixes.</p><button className="text-action" type="button" onClick={() => setActiveTab("scanner")}>Open repository scanner <span>→</span></button></article>
                <article className="tool-card"><div className="tool-card-icon icon-blue">⌘</div><span className="card-overline">QUICK EXPERIMENTS</span><h3>Interactive code sandbox</h3><p>Test a Python snippet independently and inspect the issues detected by the analyzer.</p><button className="text-action" type="button" onClick={() => setActiveTab("sandbox")}>Open code sandbox <span>→</span></button></article>
              </div>
              <section className="dashboard-panel"><div className="section-heading"><div><h2>{repoAnalysis ? "Latest analysis" : "Your activity"}</h2><p>{repoAnalysis ? "Summary from your most recent repository scan." : "Your repository metrics will appear here after your first scan."}</p></div>{repoAnalysis && <button className="btn-secondary" type="button" onClick={() => setActiveTab("scanner")}>View findings →</button>}</div>{repoAnalysis ? <div className="analysis-summary"><div><span className="summary-number">{repoAnalysis.total_findings ?? findings.length}</span><span>finding(s)</span></div><div><span className="summary-number">{repoAnalysis.total_python_files ?? "—"}</span><span>Python files</span></div><div><span className="summary-number">{repoAnalysis.health_score ?? "—"}{repoAnalysis.health_score != null ? "/100" : ""}</span><span>health score</span></div></div> : <div className="empty-dashboard"><span className="empty-illustration">⌁</span><div><strong>No analysis yet</strong><p>Start a repository scan to see real findings and code health data here. RepoGuide never fills your dashboard with made-up stats.</p></div><button className="btn-secondary" type="button" onClick={() => setActiveTab("scanner")}>Run first scan →</button></div>}</section>
            </div>}

            {activeTab === "scanner" && <div className="page-content">
              <div className="page-intro"><div><span className="eyebrow">STATIC ANALYSIS</span><h2>Find issues before they find you.</h2><p>Scan a local repository using RepoGuide's Python AST analysis engine.</p></div></div>
              <section className="scan-control-card"><form onSubmit={handleAnalyzeRepository} className="scan-form"><div className="input-group"><label htmlFor="repoPath">Repository directory</label><input id="repoPath" type="text" value={repoPath} onChange={(event) => setRepoPath(event.target.value)} placeholder="e.g. . or backend" /><span className="field-help">Enter a path that the backend can access.</span></div><div className="checkbox-group"><input id="includeAi" type="checkbox" checked={includeAi} onChange={(event) => setIncludeAi(event.target.checked)} /><label htmlFor="includeAi"><strong>Include AI explanations</strong><span>Requires GEMINI_API_KEY configured in backend/.env.</span></label></div><button type="submit" className="btn-primary" disabled={isAnalyzingRepo}>{isAnalyzingRepo ? <><span className="spinner" /> Analyzing repository…</> : "Run bug analysis →"}</button></form>{repoError && <div className="error-banner" role="alert">{repoError}</div>}</section>
              {repoAnalysis && <div className="results-panel">
                <div className="metrics-row"><div className="metric-card score-card"><span className="metric-title">Code health score</span><div className={`score-value ${repoAnalysis.health_score >= 80 ? "score-good" : repoAnalysis.health_score >= 50 ? "score-fair" : "score-poor"}`}>{repoAnalysis.health_score ?? "—"}<span className="score-max">/100</span></div><span className="score-label">{repoAnalysis.health_score >= 80 ? "Healthy" : repoAnalysis.health_score >= 50 ? "Room to improve" : "Needs attention"}</span><button type="button" className="btn-score-guide-toggle" onClick={() => setShowScoreGuide(!showScoreGuide)}>{showScoreGuide ? "Hide scoring guide ↑" : "How is this scored? ↓"}</button></div><div className="metric-card"><span className="metric-title">Python files</span><span className="metric-number">{repoAnalysis.total_python_files ?? "—"}</span><span className="metric-desc">{(repoAnalysis.total_python_lines ?? 0).toLocaleString()} lines analyzed</span></div><div className="metric-card"><span className="metric-title">Total findings</span><span className="metric-number">{repoAnalysis.total_findings ?? findings.length}</span><span className="metric-desc">Issues detected</span></div><div className="metric-card breakdown-card"><span className="metric-title">Severity breakdown</span><div className="pill-group"><SeverityPill severity="Critical" count={severityBreakdown.Critical ?? severityBreakdown.CRITICAL} /><SeverityPill severity="High" count={severityBreakdown.High ?? severityBreakdown.HIGH} /><SeverityPill severity="Medium" count={severityBreakdown.Medium ?? severityBreakdown.MEDIUM} /><SeverityPill severity="Low" count={severityBreakdown.Low ?? severityBreakdown.LOW} /></div></div></div>
                {showScoreGuide && <section className="score-guide-panel"><h3>How the score works</h3><p>The analyzer starts from a base score and deducts points according to the severity assigned to detected findings. Treat the score as a helpful signal, not a substitute for code review.</p><div className="guide-grid"><div><SeverityPill severity="Critical" count="Highest risk" /><p>Execution-blocking syntax or compilation failures.</p></div><div><SeverityPill severity="High" count="High risk" /><p>Potentially serious runtime hazards or resource handling problems.</p></div><div><SeverityPill severity="Medium" count="Moderate" /><p>Silent failure patterns and state leakage risks.</p></div><div><SeverityPill severity="Low" count="Lower risk" /><p>Code hygiene and correctness improvements.</p></div></div></section>}
                <div className="findings-toolbar"><div><h2>Detailed findings</h2><p>{displayedRepoFindings.length} of {findings.length} findings shown</p></div><div className="toolbar-actions"><label className="filter-label" htmlFor="severityFilter">Severity</label><select id="severityFilter" value={severityFilter} onChange={(event) => setSeverityFilter(event.target.value)}>{["ALL", "Critical", "High", "Medium", "Low"].map((severity) => <option key={severity} value={severity}>{severity === "ALL" ? "All severities" : severity}</option>)}</select><button className="btn-secondary" type="button" onClick={handleDownloadReport} disabled={!repoAnalysis.report_markdown}>↓ Download report</button></div></div>
                <div className="findings-container">{displayedRepoFindings.length === 0 ? <div className="empty-state"><span>✓</span><h3>No findings for this filter</h3><p>Try another severity or enjoy the clean result.</p></div> : displayedRepoFindings.map((finding, index) => <FindingCard key={`${finding.file || "file"}-${finding.line || index}-${index}`} finding={finding} index={index} />)}</div>
              </div>}
            </div>}

            {activeTab === "sandbox" && <div className="page-content">
              <div className="page-intro"><div><span className="eyebrow">QUICK CODE CHECK</span><h2>Try a snippet.</h2><p>Inspect Python code without running it. RepoGuide analyzes patterns; it does not execute your snippet.</p></div></div>
              <div className="sandbox-layout"><section className="sandbox-editor-panel"><div className="panel-header"><div><h2>Python editor</h2><p>Paste code or start with the sample.</p></div><span className="language-tag">PYTHON</span></div><textarea className="code-textarea" value={sandboxCode} onChange={(event) => setSandboxCode(event.target.value)} placeholder="Paste Python code here…" rows={18} spellCheck={false} aria-label="Python code editor" /><div className="sandbox-actions"><button className="btn-primary" type="button" onClick={handleAnalyzeSnippet} disabled={isAnalyzingSandbox}>{isAnalyzingSandbox ? "Analyzing snippet…" : "Analyze code →"}</button><button className="btn-secondary" type="button" onClick={() => { setSandboxCode(SAMPLE_BUGGY_CODE); setSandboxAnalysis(null); setSandboxError(""); }}>Load sample</button><button className="btn-quiet" type="button" onClick={() => { setSandboxCode(""); setSandboxAnalysis(null); setSandboxError(""); }}>Clear</button></div>{sandboxError && <div className="error-banner" role="alert">{sandboxError}</div>}</section>
                <section className="sandbox-results-panel"><div className="panel-header"><div><h2>Analysis results</h2><p>{sandboxAnalysis ? `${sandboxAnalysis.findings_count ?? sandboxAnalysis.findings?.length ?? 0} issue(s) detected` : "Results will appear here."}</p></div></div>{!sandboxAnalysis ? <div className="empty-state"><span>⌘</span><h3>Ready when you are</h3><p>Click “Analyze code” to inspect this snippet.</p></div> : (sandboxAnalysis.findings_count ?? sandboxAnalysis.findings?.length ?? 0) === 0 ? <div className="empty-state clean"><span>✓</span><h3>Looks clean</h3><p>No findings were reported by the analyzer.</p></div> : <div className="sandbox-findings-list">{(sandboxAnalysis.findings || []).map((finding, index) => <FindingCard key={`${finding.line || index}-${index}`} finding={finding} index={index} prefix="sandbox" />)}</div>}</section></div>
            </div>}

            {activeTab === "account" && <div className="page-content account-tab"><div className="page-intro"><div><span className="eyebrow">YOUR PROFILE</span><h2>Account &amp; session</h2><p>Review the account currently connected to RepoGuide.</p></div></div><section className="account-card"><div className="account-card-heading"><div className="account-icon">✓</div><div><h2>Authenticated session</h2><p>Your workspace is connected to the RepoGuide API.</p></div><span className="connected-badge"><span className="online-dot" /> Connected</span></div><div className="account-info-grid"><div><span className="info-label">Display name</span><strong className="info-val">{displayName}</strong></div><div><span className="info-label">User ID</span><strong className="info-val">{user.user_id || "Not provided"}</strong></div><div><span className="info-label">Email</span><strong className="info-val">{user.email || email || "Not provided"}</strong></div><div><span className="info-label">Role</span><strong className="info-val">{user.role || "Developer"}</strong></div><div><span className="info-label">Analysis engine</span><strong className="info-val">Python AST static analyzer</strong></div><div><span className="info-label">Session status</span><strong className="info-val">Authenticated</strong></div></div><div className="account-actions"><p>Signing out ends the local workspace session and asks the API to clear the session cookie.</p><button className="btn-danger-outline" type="button" onClick={handleSignOut}>Sign out of RepoGuide</button></div></section></div>}
          </div>
        </section>
      )}

      <footer className="page-footer"><span>© 2026 RepoGuide</span><span>Built with React · Python AST static analysis</span></footer>
    </main>
  );
}

export default App;
