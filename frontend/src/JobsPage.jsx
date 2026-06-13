import { useState, useEffect, useCallback } from 'react'
import client from './api'

export default function JobsPage({ onSelectJob }) {
    const [jobs, setJobs] = useState([])
    const [total, setTotal] = useState(0)
    const [loading, setLoading] = useState(false)
    const [q, setQ] = useState('')
    const [industry, setIndustry] = useState('')
    const [page, setPage] = useState(1)
    const PAGE = 15

    const load = useCallback(async () => {
        setLoading(true)
        try {
            const params = new URLSearchParams({ page, page_size: PAGE })
            if (q) params.set('q', q)
            if (industry) params.set('industry', industry)
            const res = await client.get(`/api/jobs/?${params}`)
            setJobs(res.data.jobs || [])
            setTotal(res.data.total || 0)
        } catch { } finally { setLoading(false) }
    }, [q, industry, page])

    useEffect(() => { load() }, [load])

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 8 }}>
                <div>
                    <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Browse Jobs</h2>
                    <p style={{ color: '#64748B', fontSize: 13, marginTop: 4 }}>{total} positions available</p>
                </div>
            </div>

            {/* Search */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
                <input value={q} onChange={e => setQ(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && load()}
                    placeholder="Search jobs, companies..."
                    style={{
                        flex: 1, minWidth: 200, background: '#1E293B', border: '1px solid #334155',
                        color: '#F1F5F9', borderRadius: 8, padding: '10px 14px', fontSize: 14, outline: 'none'
                    }} />
                <input value={industry} onChange={e => setIndustry(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && load()}
                    placeholder="Industry..."
                    style={{
                        background: '#1E293B', border: '1px solid #334155', color: '#F1F5F9',
                        borderRadius: 8, padding: '10px 14px', fontSize: 14, outline: 'none', width: 160
                    }} />
                <button onClick={() => { setPage(1); load() }} style={{
                    background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8,
                    padding: '10px 18px', fontWeight: 600, cursor: 'pointer', fontSize: 14,
                }}>Search</button>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: 60, color: '#64748B' }}>Loading...</div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {jobs.map(job => (
                        <div key={job.id} onClick={() => onSelectJob(job)}
                            style={{
                                background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                                padding: '16px 20px', cursor: 'pointer', transition: 'border-color .2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.borderColor = '#6366F1'}
                            onMouseLeave={e => e.currentTarget.style.borderColor = '#334155'}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
                                        <span style={{ fontWeight: 600, fontSize: 15 }}>{job.title}</span>
                                        {job.remote && <span style={{
                                            background: '#134E4A', color: '#5EEAD4',
                                            padding: '1px 8px', borderRadius: 999, fontSize: 11
                                        }}>Remote</span>}
                                    </div>
                                    <div style={{ color: '#64748B', fontSize: 13, marginBottom: 8 }}>
                                        🏢 {job.company} · 📍 {job.location} · ⏱ {job.experience_level}
                                    </div>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                        {(job.required_skills || []).slice(0, 5).map(s => (
                                            <span key={s} style={{
                                                background: '#0F172A', border: '1px solid #334155',
                                                color: '#94A3B8', padding: '1px 8px', borderRadius: 999, fontSize: 11
                                            }}>
                                                {s}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                {(job.salary_min || job.salary_max) && (
                                    <div style={{ color: '#64748B', fontSize: 13 }}>
                                        💰 ₹{((job.salary_min || 0) / 100000).toFixed(0)}–{((job.salary_max || 0) / 100000).toFixed(0)}L
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {jobs.length === 0 && (
                        <div style={{ textAlign: 'center', color: '#64748B', padding: 48 }}>No jobs found.</div>
                    )}
                </div>
            )}

            {/* Pagination */}
            {total > PAGE && (
                <div style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: 24 }}>
                    <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{
                        background: 'transparent', border: '1px solid #334155', color: '#94A3B8',
                        borderRadius: 8, padding: '8px 16px', cursor: 'pointer',
                    }}>← Prev</button>
                    <span style={{ color: '#64748B', padding: '8px 14px' }}>
                        Page {page} of {Math.ceil(total / PAGE)}
                    </span>
                    <button onClick={() => setPage(p => p + 1)} disabled={page >= Math.ceil(total / PAGE)} style={{
                        background: 'transparent', border: '1px solid #334155', color: '#94A3B8',
                        borderRadius: 8, padding: '8px 16px', cursor: 'pointer',
                    }}>Next →</button>
                </div>
            )}
        </div>
    )
}