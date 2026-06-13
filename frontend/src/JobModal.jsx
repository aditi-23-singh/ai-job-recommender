import { useState } from 'react'
import client from './api'

export default function JobModal({ job, onClose }) {
    const [saved, setSaved] = useState(false)
    const [saving, setSaving] = useState(false)
    const [gap, setGap] = useState(null)
    const [gapLoading, setGapLoading] = useState(false)

    const jid = job.id || job.job_id

    async function toggleSave() {
        setSaving(true)
        try {
            const res = await client.post(`/api/jobs/${jid}/save`)
            setSaved(res.data.saved)
        } catch { } finally { setSaving(false) }
    }

    async function loadGap() {
        setGapLoading(true)
        try {
            const res = await client.get(`/api/skill-gap/${jid}`)
            setGap(res.data)
        } catch { } finally { setGapLoading(false) }
    }

    return (
        <div onClick={e => e.target === e.currentTarget && onClose()} style={{
            position: 'fixed', inset: 0, background: '#000000cc', zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20,
        }}>
            <div style={{
                background: '#1E293B', border: '1px solid #334155', borderRadius: 16,
                padding: 28, maxWidth: 600, width: '100%', maxHeight: '85vh', overflowY: 'auto',
            }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                    <div>
                        <h2 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>{job.title}</h2>
                        <div style={{ color: '#64748B', fontSize: 13, marginTop: 4 }}>
                            🏢 {job.company} · 📍 {job.location}
                        </div>
                    </div>
                    <button onClick={onClose} style={{
                        background: 'none', border: 'none',
                        color: '#64748B', cursor: 'pointer', fontSize: 20
                    }}>✕</button>
                </div>

                {/* Badges */}
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
                    {[job.experience_level, job.industry, job.job_type].filter(Boolean).map(b => (
                        <span key={b} style={{
                            background: '#0F172A', border: '1px solid #334155',
                            color: '#94A3B8', padding: '3px 10px', borderRadius: 999, fontSize: 12
                        }}>
                            {b}
                        </span>
                    ))}
                    {job.remote && <span style={{
                        background: '#134E4A', color: '#5EEAD4',
                        padding: '3px 10px', borderRadius: 999, fontSize: 12
                    }}>Remote</span>}
                </div>

                {/* Description */}
                <p style={{ color: '#CBD5E1', fontSize: 14, lineHeight: 1.7, marginBottom: 16 }}>{job.description}</p>

                {/* Skills */}
                <div style={{ marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 8 }}>Required Skills</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {(job.required_skills || []).map(s => (
                            <span key={s} style={{
                                background: '#312E81', color: '#A5B4FC',
                                padding: '2px 10px', borderRadius: 999, fontSize: 12
                            }}>{s}</span>
                        ))}
                    </div>
                </div>

                {/* Quick skill gap */}
                {gap && (
                    <div style={{ background: '#0F172A', borderRadius: 8, padding: '14px 16px', marginBottom: 16 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <span style={{ fontWeight: 600, fontSize: 13 }}>Your Gap Analysis</span>
                            <span style={{
                                color: gap.match_score >= 80 ? '#22C55E' : gap.match_score >= 60 ? '#14B8A6' : '#F59E0B',
                                fontWeight: 700
                            }}>{gap.match_score.toFixed(0)}% — {gap.readiness_label}</span>
                        </div>
                        <div style={{ background: '#334155', borderRadius: 999, height: 5, marginBottom: 10 }}>
                            <div style={{
                                width: `${gap.match_score}%`, background: 'linear-gradient(90deg,#6366F1,#14B8A6)',
                                borderRadius: 999, height: '100%'
                            }} />
                        </div>
                        {gap.missing_required?.length > 0 && (
                            <div style={{ fontSize: 12, color: '#64748B' }}>
                                Missing: {gap.missing_required.map(s => (
                                    <span key={s} style={{
                                        background: '#450A0A', color: '#FCA5A5', padding: '1px 8px',
                                        borderRadius: 999, marginLeft: 4
                                    }}>{s}</span>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {/* Salary */}
                {(job.salary_min || job.salary_max) && (
                    <div style={{ color: '#64748B', fontSize: 13, marginBottom: 16 }}>
                        💰 Salary: ₹{((job.salary_min || 0) / 100000).toFixed(0)}L – ₹{((job.salary_max || 0) / 100000).toFixed(0)}L
                    </div>
                )}

                {/* Actions */}
                <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                    <button onClick={toggleSave} disabled={saving} style={{
                        background: saved ? '#14B8A6' : 'transparent',
                        color: saved ? '#fff' : '#6366F1',
                        border: `1px solid ${saved ? '#14B8A6' : '#6366F1'}`,
                        borderRadius: 8, padding: '9px 18px', fontWeight: 600, cursor: 'pointer', fontSize: 14,
                    }}>
                        {saving ? 'Saving...' : saved ? '✓ Saved' : '⭐ Save Job'}
                    </button>
                    <button onClick={loadGap} disabled={gapLoading} style={{
                        background: 'transparent', color: '#94A3B8', border: '1px solid #334155',
                        borderRadius: 8, padding: '9px 18px', fontWeight: 600, cursor: 'pointer', fontSize: 14,
                    }}>
                        {gapLoading ? 'Analysing...' : '📊 Analyse Gap'}
                    </button>
                </div>
            </div>
        </div>
    )
}