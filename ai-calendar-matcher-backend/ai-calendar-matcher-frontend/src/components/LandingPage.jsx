import React from "react";
import { signInWithGoogle } from "./firebase.js"; // adjust path if needed
import "./LandingPage.css"; // we'll move the CSS here

export default function LandingPage({ onLogin }) {
  const handleLogin = async () => {
    try {
      const user = await signInWithGoogle();
      if (user) onLogin({ user, token: user.accessToken || "" });
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  return (
    <div>
      <header className="header">
        <div className="logo">rendAlvous</div>
        <div className="auth-buttons">
          <button className="btn btn-login" onClick={handleLogin}>Log In</button>
          <button className="btn btn-signup" onClick={handleLogin}>Sign Up</button>
        </div>
      </header>

      <main>
        <section className="hero">
          <h1>making spontaneous connections easy again.</h1>
          <p>
            rendAlvous is a platform that makes connecting with your friends easier
            by leveraging AI tools to coordinate availability and inspire meaningful
            moments to share.
          </p>
        </section>

        <section className="features">
          <div className="feature-card">
            <div className="feature-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <h3 className="feature-title">Smart Scheduling</h3>
            <p className="feature-description">
              Sync Google Calendars and let AI find the perfect times when everyone's free.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">T</div>
            <h3 className="feature-title">AI Suggestions</h3>
            <p className="feature-description">
              <span className="highlight-box">
                Get personalized activity ideas based on weather, time, preferences, and budget.
              </span>
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <h3 className="feature-title">Stay Connected</h3>
            <p className="feature-description">
              Receive smart reminders to reconnect with friends you haven't seen in a while.
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
