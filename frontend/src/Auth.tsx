import React, { useState } from 'react';
import { Bot, UserPlus, LogIn } from 'lucide-react';

const API_BASE = `http://${window.location.hostname}:8000`;

type AuthProps = {
  onAuth: (token: string, username: string) => void;
};

export default function Auth({ onAuth }: AuthProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password.');
      return;
    }
    
    setError('');
    setLoading(true);
    
    try {
      const endpoint = isLogin ? '/login' : '/register';
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }
      
      if (isLogin && data.access_token) {
        onAuth(data.access_token, data.username);
      } else if (!isLogin) {
        // Auto login after successful registration
        const loginRes = await fetch(`${API_BASE}/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        });
        const loginData = await loginRes.json();
        if (loginRes.ok && loginData.access_token) {
          onAuth(loginData.access_token, loginData.username);
        } else {
          setError('Registered successfully, but auto-login failed. Please log in.');
          setIsLogin(true);
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container" style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div 
        className="auth-card" 
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
          <div
            className="robot-mascot"
            style={{
              position: 'relative',
              right: 'auto',
              top: 'auto',
              background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)',
              border: '2px solid rgba(255,255,255,0.2)',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Bot size={40} color="#fff" />
          </div>
          <h1 style={{ fontSize: '1.8rem' }}>Breakup <span>Bot</span></h1>
          <p style={{ color: '#a497bd', fontSize: '0.9rem', textAlign: 'center' }}>
            {isLogin ? 'Welcome back. I am here for you.' : 'Create an account to start healing.'}
          </p>
        </div>

        {error && (
          <div style={{ color: '#fca5a5', fontSize: '0.9rem', backgroundColor: 'rgba(239, 68, 68, 0.2)', padding: '10px', borderRadius: '8px', width: '100%', textAlign: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <div className="input-area" style={{ margin: 0, maxWidth: '100%' }}>
            <input
              type="text"
              className="chat-input"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="input-area" style={{ margin: 0, maxWidth: '100%' }}>
            <input
              type="password"
              className="chat-input"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            style={{
               width: '100%', 
               padding: '12px', 
               borderRadius: '16px', 
               border: 'none', 
               background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)', 
               color: 'white',
               fontSize: '1rem',
               fontWeight: '600',
               cursor: loading ? 'not-allowed' : 'pointer',
               opacity: loading ? 0.7 : 1,
               display: 'flex',
               justifyContent: 'center',
               alignItems: 'center',
               gap: '8px',
               marginTop: '10px'
            }}
          >
            {isLogin ? <><LogIn size={18} /> Login</> : <><UserPlus size={18} /> Create Account</>}
          </button>
        </form>

        <button 
          onClick={() => { setIsLogin(!isLogin); setError(''); }}
          style={{
            background: 'none',
            border: 'none',
            color: '#a497bd',
            fontSize: '0.9rem',
            cursor: 'pointer',
            textDecoration: 'underline',
            marginTop: '10px'
          }}
        >
          {isLogin ? "Don't have an account? Sign up" : "Already have an account? Log in"}
        </button>
      </div>
    </div>
  );
}
