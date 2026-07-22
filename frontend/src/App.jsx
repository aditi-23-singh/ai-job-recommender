import { useState, useEffect } from 'react'
import AuthPage from './AuthPage'
import Dashboard from './Dashboard'
import ResumePage from './ResumePage'
import RecommendationsPage from './RecommendationsPage'
import JobsPage from './JobsPage'
import SkillGapPage from './SkillGapPage'
import SavedJobsPage from './SavedJobsPage'
import JobModal from './JobModal'
import client from './api'

const NAV = [
  { id: 'dashboard', label: 'Dashboard', emoji: '🏠' },
  { id: 'resume', label: 'Resume', emoji: '📄' },
  { id: 'recommendations', label: 'Recommendations', emoji: '🎯' },
  { id: 'jobs', label: 'Browse Jobs', emoji: '💼' },
  { id: 'skill-gap', label: 'Skill Gap', emoji: '📊' },
  { id: 'saved', label: 'Saved Jobs', emoji: '⭐' },
]

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState('dashboard')
  const [selectedJob, setSelectedJob] = useState(null)
  const [collapsed, setCollapsed] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('jwt')
    if (!token) { setLoading(false); return }
    client.get('/api/auth/me')
      .then(r => setUser(r.data))
      .catch(() => localStorage.removeItem('jwt'))
      .finally(() => setLoading(false))
  }, [])

  function logout() { localStorage.removeItem('jwt'); setUser(null) }

  if (loading) return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', color: '#64748B'
    }}>
      Loading...
    </div>
  )

  if (!user) return <AuthPage onLogin={u => setUser(u)} />

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>

      {/* Sidebar */}
      <div style={{
        width: collapsed ? 60 : 220, background: '#1E293B',
        borderRight: '1px solid #334155', display: 'flex',
        flexDirection: 'column', height: '100vh', position: 'sticky', top: 0,
        flexShrink: 0, transition: 'width .2s',
      }}>
        {/* Logo */}
        <div style={{
          padding: collapsed ? '18px 12px' : '18px 20px',
          borderBottom: '1px solid #334155', display: 'flex',
          alignItems: 'center', gap: 10
        }}>
          <span style={{ fontSize: 24 }}>⚡</span>
          {!collapsed && <span style={{ fontWeight: 700, fontSize: 15, whiteSpace: 'nowrap' }}>
            CareerMatch AI
          </span>}
        </div>

        {/* Nav */}
        <nav style={{
          flex: 1, padding: '12px 8px', display: 'flex',
          flexDirection: 'column', gap: 2
        }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: collapsed ? '10px 12px' : '10px 14px',
              borderRadius: 8, border: 'none', cursor: 'pointer',
              background: page === n.id ? '#6366F120' : 'transparent',
              color: page === n.id ? '#6366F1' : '#64748B',
              fontWeight: page === n.id ? 600 : 400,
              fontSize: 14, width: '100%', transition: 'all .15s',
              whiteSpace: 'nowrap',
            }}>
              <span style={{ fontSize: 16 }}>{n.emoji}</span>
              {!collapsed && n.label}
            </button>
          ))}
        </nav>

        {/* User + logout */}
        <div style={{ padding: '12px 8px', borderTop: '1px solid #334155' }}>
          {!collapsed && (
            <div style={{ padding: '6px 14px', marginBottom: 6 }}>
              <div style={{ fontWeight: 600, fontSize: 13 }}>{user.full_name || user.username}</div>
              <div style={{ color: '#64748B', fontSize: 12 }}>{user.email}</div>
            </div>
          )}
          <button onClick={logout} style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: collapsed ? '10px 12px' : '10px 14px',
            borderRadius: 8, border: 'none', cursor: 'pointer',
            background: 'transparent', color: '#64748B', fontSize: 14, width: '100%',
          }}>
            <span>🚪</span>{!collapsed && 'Sign Out'}
          </button>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {/* Topbar */}
        <div style={{
          borderBottom: '1px solid #334155', padding: '14px 24px',
          display: 'flex', alignItems: 'center', gap: 12,
          background: '#1E293B', position: 'sticky', top: 0, zIndex: 10
        }}>
          <button onClick={() => setCollapsed(c => !c)} style={{
            background: 'none', border: 'none', color: '#64748B',
            cursor: 'pointer', fontSize: 18,
          }}>☰</button>
          <span style={{ color: '#64748B', fontSize: 13 }}>
            {NAV.find(n => n.id === page)?.label}
          </span>
        </div>

        <div style={{ padding: '24px 28px' }}>
          {page === 'dashboard' && <Dashboard user={user} onNavigate={setPage} />}
          {page === 'resume' && <ResumePage />}
          {page === 'recommendations' && <RecommendationsPage onSelectJob={setSelectedJob} />}
          {page === 'jobs' && <JobsPage onSelectJob={setSelectedJob} />}
          {page === 'skill-gap' && <SkillGapPage />}
          {page === 'saved' && <SavedJobsPage onSelectJob={setSelectedJob} />}
        </div>
      </div>

      {selectedJob && <JobModal job={selectedJob} onClose={() => setSelectedJob(null)} />}
    </div>
  )
}