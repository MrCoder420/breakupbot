import React, { useState, useRef, useEffect } from 'react';
import { Send, Copy, Bot, User, LogOut } from 'lucide-react';
import Auth from './Auth';

type Message = {
  id: string;
  role: 'user' | 'bot';
  content: string;
};

const API_BASE = 'http://localhost:8000';

const WELCOME_MSG: Message = {
  id: 'welcome',
  role: 'bot',
  content: "Hi. I'm Eleanor. I'm here for you. Take a deep breath — you can share whatever is on your mind. I'm listening.",
};

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('eleanor_jwt'));
  const [username, setUsername] = useState<string | null>(localStorage.getItem('eleanor_username'));
  const [messages, setMessages] = useState<Message[]>([WELCOME_MSG]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleAuth = (newToken: string, newUsername: string) => {
    localStorage.setItem('eleanor_jwt', newToken);
    localStorage.setItem('eleanor_username', newUsername);
    setToken(newToken);
    setUsername(newUsername);
  };

  const handleLogout = () => {
    localStorage.removeItem('eleanor_jwt');
    localStorage.removeItem('eleanor_username');
    setToken(null);
    setUsername(null);
    setMessages([WELCOME_MSG]);
    setHistoryLoaded(false);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (!token) return;

    const loadHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/history`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (res.status === 401) {
          handleLogout(); // Token expired or invalid
          return;
        }
        
        if (!res.ok) return;
        
        const data = await res.json();
        const past: Message[] = data.messages.map((m: { role: string; content: string }, i: number) => ({
          id: `history_${i}`,
          role: m.role as 'user' | 'bot',
          content: m.content,
        }));
        
        if (past.length > 0) {
          setMessages(past);
        }
      } catch {
        // API not running yet
      } finally {
        setHistoryLoaded(true);
      }
    };
    
    loadHistory();
  }, [token]);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isTyping || !token) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userMsg.content }),
      });

      if (res.status === 401) {
        handleLogout();
        throw new Error('Session expired. Please log in again.');
      }

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(err.detail || 'API Error');
      }

      const data = await res.json();
      const typingDelay = Math.min(Math.max(data.response.length * 6, 800), 2800);

      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { id: Date.now().toString(), role: 'bot', content: data.response },
        ]);
        setIsTyping(false);
      }, typingDelay);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Unknown error';
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            id: 'error_' + Date.now(),
            role: 'bot',
            content: `I couldn't process that... Error: ${msg}`,
          },
        ]);
        setIsTyping(false);
      }, 800);
    }
  };

  if (!token) {
    return <Auth onAuth={handleAuth} />;
  }

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="top-header">
        <h1>Chat With <span>Eleanor Mind!</span></h1>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          <span style={{ color: '#a497bd', fontSize: '0.9rem' }}>{username}</span>
          <button 
            onClick={handleLogout}
            style={{ 
              background: 'transparent', 
              border: 'none', 
              color: '#fca5a5', 
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            title="Log out"
          >
            <LogOut size={16} />
          </button>
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
              width: '50px',
              height: '50px'
            }}
          >
            <Bot size={25} color="#fff" />
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="messages-area">
        {!historyLoaded && (
          <div style={{ textAlign: 'center', padding: '12px', color: '#a497bd', fontSize: '13px' }}>
            Restoring your conversation...
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.role}`}>
            <div className="bubble">{msg.content}</div>
            <div className="msg-footer">
              {msg.role === 'bot' ? (
                <>
                  <Bot size={14} color="#a497bd" />
                  <span>Eleanor Mind</span>
                  <div
                    className="action-icon"
                    style={{ marginLeft: '12px', cursor: 'pointer' }}
                    onClick={() => handleCopy(msg.content)}
                    title="Copy response"
                  >
                    <Copy size={12} />
                    <span>Copy</span>
                  </div>
                </>
              ) : (
                <>
                  <User size={14} color="#a497bd" />
                  <span>You</span>
                </>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="message-wrapper bot">
            <div className="bubble">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
            <div className="msg-footer">
              <Bot size={14} color="#a497bd" />
              <span>Eleanor Mind</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="input-area">
        <form className="input-form" onSubmit={handleSend}>
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your feelings here..."
            autoFocus
            disabled={isTyping}
          />
          <button type="submit" className="send-button" disabled={!input.trim() || isTyping}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
