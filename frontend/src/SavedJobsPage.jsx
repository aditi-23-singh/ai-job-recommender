import { useState, useEffect } from 'react'
import client from './api'

export default function SavedJobsPage({ onSelectJob }) {
    const [jobs, setJobs] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        client.get('/api/jobs/saved/all')
            .then(r => setJobs(r.data))
            .catch(() => { })
            .finally(() => setLoading(false))
    }, [])

    return (
        <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 20 }}>Saved Jobs ⭐</h2>
            {loading ? (
                <div style={{ textAlign: 'center', padding: 60, color: '#64748B' }}>Loading...</div>
            ) : jobs.length === 0 ? (
                <div style={{
                    background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                    padding: 40, textAlign: 'center', color: '#64748B'
                }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>⭐</div>
                    <div>No saved jobs yet. Click a job and save it to see it here.</div>
                </div>
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
                            <div style={{ fontWeight: 600, marginBottom: 4 }}>{job.title}</div>
                            <div style={{ color: '#64748B', fontSize: 13 }}>
                                🏢 {job.company} · 📍 {job.location}
                            </div>
                            <div style={{ color: '#64748B', fontSize: 12, marginTop: 6 }}>
                                Saved: {new Date(job.saved_at).toLocaleDateString()}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}