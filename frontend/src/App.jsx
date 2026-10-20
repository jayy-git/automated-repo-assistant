import { useState } from "react";
import "./App.css";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  const API_URL = "http://localhost:8000";

  async function handleLogin(event) {
    event.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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
        setMessage(
          "Login succeeded, but the session was not recognized. Check your backend cookie configuration.",
        );
        return;
      }

      setUser(sessionData);
      setMessage("You're successfully logged in!");
    } catch (error) {
      console.error("Login error:", error);
      setMessage(
        error.message === "Failed to fetch"
          ? "Cannot connect to the backend. Check that FastAPI is running and CORS allows this frontend."
          : error.message,
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="hackloop">
      <nav className="navbar">
        <a className="brand" href="/">
          <span className="brand-icon">H</span>
          Hackloop<span className="brand-dot">.</span>
        </a>

        <span className="nav-label">Developer workspace</span>
      </nav>

      <section className="login-layout">
        <div className="welcome-panel">
          <span className="eyebrow">YOUR NEXT BUILD STARTS HERE</span>

          <h1>
            Build together.
            <br />
            <span>Ship smarter.</span>
          </h1>

          <p className="welcome-text">
            Your space to collaborate, explore code, and turn ideas into
            something real.
          </p>

          <div className="feature-list">
            <div className="feature">
              <span className="feature-icon">⌘</span>
              <div>
                <strong>One workspace</strong>
                <p>Keep your projects and workflow together.</p>
              </div>
            </div>

            <div className="feature">
              <span className="feature-icon">↗</span>
              <div>
                <strong>Built for builders</strong>
                <p>Focus on creating, learning, and shipping.</p>
              </div>
            </div>
          </div>

          <div className="welcome-footer">
            MADE FOR THE NEXT GENERATION OF DEVELOPERS
          </div>
        </div>

        <div className="form-panel">
          {!user ? (
            <>
              <div className="form-heading">
                <span className="form-kicker">WELCOME BACK</span>
                <h2>Sign in to Hackloop</h2>
                <p>Enter your account details to continue.</p>
              </div>

              <form onSubmit={handleLogin}>
                <label htmlFor="email">Email address</label>
                <input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="email"
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
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                />

                <button className="login-button" type="submit" disabled={loading}>
                  {loading ? "Signing in..." : "Sign in"}
                  {!loading && <span aria-hidden="true"> →</span>}
                </button>
              </form>

              {message && (
                <p className="status-message" role="status" aria-live="polite">
                  {message}
                </p>
              )}

              <p className="security-note">
                Your account is protected by session-based authentication.
              </p>
            </>
          ) : (
            <div className="signed-in">
              <span className="success-icon">✓</span>
              <span className="form-kicker">AUTHENTICATED</span>
              <h2>You're in!</h2>
              <p>Your session is working correctly.</p>

              <div className="account-details">
                <span>Account ID</span>
                <strong>{user.user_id}</strong>
                <span>Role</span>
                <strong>{user.role}</strong>
              </div>

              <button
                className="login-button"
                onClick={() => {
                  setUser(null);
                  setEmail("");
                  setPassword("");
                  setMessage("");
                }}
              >
                Back to sign in
              </button>
            </div>
          )}
        </div>
      </section>

      <footer className="page-footer">
        <span>© 2026 Hackloop</span>
        <span>Built for people who build.</span>
      </footer>
    </main>
  );
}

export default App;