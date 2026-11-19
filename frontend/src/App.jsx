import { useEffect, useState } from 'react';
import {
  ArrowRight, BarChart3, Building2, ChevronLeft, CircleHelp, LockKeyhole,
  LogOut, Menu, MessageCircle, Network, ShieldCheck, Sparkles, UserRound,
  UsersRound, X,
} from 'lucide-react';

import { api } from './api.js';
import ChatWindow from './components/ChatWindow.jsx';
import Overview from './components/Overview.jsx';
import ManageUsers from './components/ManageUsers.jsx';

function Entrance({ onLogin, onDemo, busy, error }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  function submit(event) {
    event.preventDefault();
    onLogin(username, password);
  }

  return (
    <main className="entrance">
      <section className="entrance-hero">
        <div className="brand"><span className="brand-icon"><Network size={22}/></span>STOREBRIDGE <b>MCP</b></div>
        <div className="hero-main">
          <span className="hero-label"><Sparkles size={15}/> THE SMARTER WAY TO RUN RETAIL</span>
          <h1>Every branch.<br/><em>One clear picture.</em></h1>
          <p>Meet Walk & Talk Assistant. Your intelligent companion for stock, prices, sales, profit, and store performance across three locations.</p>
          <div className="hero-points"><span><Building2 size={16}/> 3 connected branches</span><span><ShieldCheck size={16}/> Secure read-only insights</span></div>
        </div>
        <div className="hero-bottom">A portfolio project · All business data is synthetic</div>
      </section>
      <section className="entrance-form-area"><div className="login-card">
        <div className="login-logo"><Network size={29}/></div>
        <div className="eyebrow">WALK & TALK</div>
        <h2>Welcome back.</h2>
        <p>Sign in to your business workspace.</p>
        <form onSubmit={submit} className="login-form">
          <label>Username<input required value={username} onChange={event => setUsername(event.target.value)} placeholder="Enter your username" autoComplete="username" /></label>
          <label>Password<input required type="password" value={password} onChange={event => setPassword(event.target.value)} placeholder="Enter your password" autoComplete="current-password" /></label>
          {error && <div className="error-banner">{error}</div>}
          <button className="primary-button full" disabled={busy}><LockKeyhole size={17}/> Sign in <ArrowRight size={17}/></button>
        </form>
        <div className="divider-label">or explore the experience</div>
        <button className="outline-button full" disabled={busy} onClick={onDemo}><Sparkles size={17}/> Try Demo <ArrowRight size={17}/></button>
        <p className="login-caption">Recruiters can access all read-only business reporting using fictional records. Manager accounts are created by the owner.</p>
      </div></section>
    </main>
  );
}

function Profile({ user, onLogout }) {
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [notice, setNotice] = useState('');
  const [error, setError] = useState('');

  async function change(event) {
    event.preventDefault();
    setError('');

    try {
      await api('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify({ current_password: oldPassword, new_password: newPassword }),
      });
      setNotice('Password updated. Sign in again with your new password.');
      setTimeout(onLogout, 1000);
    } catch (reason) {
      setError(reason.message);
    }
  }

  return <div className="page-wrap profile-page">
    <div className="page-header"><div className="eyebrow">MY ACCOUNT</div><h1>Profile & Security</h1><p>Manage your signed-in account.</p></div>
    <section className="panel profile-card"><div className="profile-avatar"><UserRound size={30}/></div><h2>{user.name}</h2><p>@{user.username} · {user.role === 'admin' ? 'Owner' : user.role === 'manager' ? 'Branch Manager' : 'Demo Visitor'}</p>
      {user.branch && <p>Assigned branch: {user.branch.replace('_', ' ')}</p>}
    </section>
    {user.role !== 'demo' && <form className="panel password-form" onSubmit={change}>
      <h2>Change password</h2>
      {user.must_change_password && <p className="warning-text">Please change your temporary password now.</p>}
      <label>Current password<input required type="password" value={oldPassword} onChange={e => setOldPassword(e.target.value)}/></label>
      <label>New password<input required type="password" minLength={8} value={newPassword} onChange={e => setNewPassword(e.target.value)}/></label>
      {error && <div className="error-banner">{error}</div>}{notice && <div className="success-banner">{notice}</div>}
      <button className="primary-button">Update password</button>
    </form>}
  </div>;
}

export default function App() {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);
  const [page, setPage] = useState('chat');
  const [menuOpen, setMenuOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api('/auth/me').then(identity => {
      setUser(identity);
      setPage(identity.role === 'manager' ? 'chat' : 'overview');
    }).catch(() => {}).finally(() => setReady(true));
  }, []);

  async function login(username, password) {
    setBusy(true);
    setError('');
    try {
      const identity = await api('/auth/login', {
        method: 'POST', body: JSON.stringify({ username, password }),
      });
      setUser(identity);
      setPage(identity.role === 'manager' ? 'chat' : 'overview');
    } catch (reason) {
      setError(reason.message);
    } finally {
      setBusy(false);
    }
  }

  async function demo() {
    setBusy(true);
    setError('');
    try {
      const identity = await api('/auth/demo', { method: 'POST' });
      setUser(identity);
      setPage('overview');
    } catch (reason) {
      setError(reason.message);
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    try { await api('/auth/logout', { method: 'POST' }); } catch { /* Clear local session anyway */ }
    setUser(null);
    setMessages([]);
    setPage('chat');
    setMenuOpen(false);
  }

  async function ask(text) {
    if (busy) return;
    const outgoing = [...messages, { role: 'user', content: text }];
    setMessages(outgoing);
    setBusy(true);
    setError('');

    try {
      const result = await api('/chat', {
        method: 'POST',
        body: JSON.stringify({
          messages: outgoing.map(({ role, content }) => ({ role, content })).slice(-18),
        }),
      });
      setMessages([...outgoing, { role: 'assistant', content: result.answer, chart: result.chart, tools_used: result.tools_used }]);
    } catch (reason) {
      setError(reason.message);
    } finally {
      setBusy(false);
    }
  }

  if (!ready) return <div className="startup">Loading Walk & Talk Assistant...</div>;
  if (!user) return <Entrance onLogin={login} onDemo={demo} busy={busy} error={error}/>;

  const navigation = [
    ...(user.role !== 'manager' ? [{ id: 'overview', title: 'Overview', icon: BarChart3 }] : []),
    { id: 'chat', title: 'AI Assistant', icon: MessageCircle },
    ...(user.role === 'admin' ? [{ id: 'users', title: 'Manage Users', icon: UsersRound }] : []),
  ];

  return <div className="workspace">
    {menuOpen && <button className="mobile-backdrop" aria-label="Close menu" onClick={() => setMenuOpen(false)} />}
    <aside className={`sidebar ${menuOpen ? 'open' : ''}`}>
      <div className="side-brand"><span className="brand-icon"><Network size={21}/></span><span>STOREBRIDGE <b>MCP</b><small>WALK & TALK</small></span><button className="mobile-close" onClick={() => setMenuOpen(false)}><X size={20}/></button></div>
      <div className="side-section-label">WORKSPACE</div>
      <nav>{navigation.map(item => <button key={item.id} className={`nav-item ${page === item.id ? 'selected' : ''}`} onClick={() => {setPage(item.id);setMenuOpen(false);}}><item.icon size={19}/>{item.title}</button>)}</nav>
      <div className="side-branches"><div className="side-section-label">CONNECTED LOCATIONS</div><p><span/> Liberty Plaza</p><p><span/> One Galle Face Mall</p><p><span/> Pettah Main Street</p></div>
      <div className="side-bottom"><button className={`nav-item ${page === 'profile' ? 'selected' : ''}`} onClick={() => {setPage('profile');setMenuOpen(false);}}><UserRound size={19}/> My Profile</button><button className="nav-item" onClick={logout}><LogOut size={19}/> Sign out</button>
        <div className="signed-user"><div className="user-avatar">{user.name?.[0] || 'W'}</div><div><strong>{user.name}</strong><span>{user.role === 'admin' ? 'Owner / Admin' : user.role === 'manager' ? 'Branch Manager' : 'Demo Visitor'}</span></div></div>
      </div>
    </aside>
    <main className="main-content">
      <div className="mobile-topbar"><button onClick={() => setMenuOpen(true)}><Menu size={22}/></button><strong>Walk & Talk Assistant</strong><span className="online-dot"/></div>
      {page === 'overview' && user.role !== 'manager' && <Overview onChat={() => setPage('chat')} />}
      <div style={{ display: page === 'chat' ? 'flex' : 'none', minHeight: 0, flex: 1 }}><ChatWindow user={user} messages={messages} setMessages={setMessages} ask={ask} busy={busy} error={error}/></div>
      {page === 'users' && user.role === 'admin' && <ManageUsers />}
      {page === 'profile' && <Profile user={user} onLogout={logout} />}
    </main>
  </div>;
}
