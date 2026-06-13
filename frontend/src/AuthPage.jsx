import { useState } from 'react'
import client from './api'

export default function AuthPage({ onLogin }) {
    const [mode, setMode] = useState('login')
    const [form, setForm] = useState({ email: '', password: '', username: '', full_name: '' })
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

    async function submit(e) {
        e.preventDefault()
        setError(''); setLoading(true)
        try {
            if (mode === 'login') {
                const params = new URLSearchParams({ username: form.email, password: form.password })
                const res = await client.post('/api/auth/login', params,
                    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
                localStorage.setItem('jwt', res.data.access_token)
                onLogin(res.data.user)
            } else {
                const res = await client.post('/api/auth/register', form)
                localStorage.setItem('jwt', res.data.access_token)
                onLogin(res.data.user)
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong')
        } finally { setLoading(false) }
    }

    const inp = {
        width: '100%', padding: '10px 14px', background: '#0F172A',
        border: '1px solid #334155', borderRadius: 8, color: '#F1F5F9',
        fontSize: 14, outline: 'none', marginTop: 4,
    }

    return (
        <div style={{
            minHeight: '100vh', display: 'flex', alignItems: 'center',
            justifyContent: 'center', padding: 20
        }}>
            <div style={{ width: '100%', maxWidth: 400 }}>

                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: 32 }}>
                    <div style={{ fontSize: 40, marginBottom: 8 }}>⚡</div>
                    <h1 style={{ fontSize: 26, fontWeight: 700 }}>CareerMatch AI</h1>
                    <p style={{ color: '#64748B', marginTop: 6 }}>ML-powered job recommendations</p>
                </div>

                {/* Card */}
                <div style={{
                    background: '#1E293B', border: '1px solid #334155',
                    borderRadius: 12, padding: 28
                }}>

                    {/* Tabs */}
                    <div style={{
                        display: 'flex', background: '#0F172A', borderRadius: 8,
                        padding: 4, marginBottom: 24
                    }}>
                        {['login', 'register'].map(m => (
                            <button key={m} onClick={() => setMode(m)} style={{
                                flex: 1, padding: '8px 0', borderRadius: 6, border: 'none',
                                cursor: 'pointer', fontWeight: 600, fontSize: 14,
                                background: mode === m ? '#6366F1' : 'transparent',
                                color: mode === m ? '#fff' : '#64748B',
                                transition: 'all .2s',
                            }}>
                                {m === 'login' ? 'Sign In' : 'Register'}
                            </button>
                        ))}
                    </div>

                    <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        {mode === 'register' && <>
                            <div>
                                <label style={{ color: '#CBD5E1', fontSize: 13 }}>Full Name</label>
                                <input style={inp} placeholder="Aditi Singh"
                                    value={form.full_name} onChange={e => update('full_name', e.target.value)} />
                            </div>
                            <div>
                                <label style={{ color: '#CBD5E1', fontSize: 13 }}>Username</label>
                                <input style={inp} placeholder="aditi23"
                                    value={form.username} onChange={e => update('username', e.target.value)} required />
                            </div>
                        </>}

                        <div>
                            <label style={{ color: '#CBD5E1', fontSize: 13 }}>Email</label>
                            <input style={inp} type="email" placeholder="aditi@example.com"
                                value={form.email} onChange={e => update('email', e.target.value)} required />
                        </div>
                        <div>
                            <label style={{ color: '#CBD5E1', fontSize: 13 }}>Password</label>
                            <input style={inp} type="password" placeholder="••••••••"
                                value={form.password} onChange={e => update('password', e.target.value)} required />
                        </div>

                        {error && (
                            <div style={{
                                background: '#450A0A', border: '1px solid #7F1D1D',
                                borderRadius: 8, padding: '10px 14px', color: '#FCA5A5', fontSize: 13
                            }}>
                                {error}
                            </div>
                        )}

                        <button type="submit" disabled={loading} style={{
                            background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8,
                            padding: '11px 0', fontWeight: 600, fontSize: 15, cursor: 'pointer',
                            opacity: loading ? 0.7 : 1, marginTop: 4,
                        }}>
                            {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
                        </button>
                    </form>

                    <p style={{ color: '#64748B', fontSize: 12, textAlign: 'center', marginTop: 16 }}>
                        Demo: register with any email, then upload your resume.
                    </p>
                </div>
            </div>
        </div>
    )
}