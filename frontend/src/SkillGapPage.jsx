import { useState, useEffect } from 'react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, Tooltip, ResponsiveContainer } from 'recharts'
import client from './api'

export default function SkillGapPage() {
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    async function load() {
        setLoading(true); setError('')
        try {
            const res = await client.get('/api/skill-gap/bulk/top?limit=5')
            setData(res.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load')
        } finally { setLoading(false) }
    }

    useEffect(() => { load() }, [])

    function color(label) {
        if (label === 'Ready') return '#22C55E'
        if (label === 'Almost Ready') return '#14B8A6'
        if (label === 'Needs Work') return '#F59E0B'
        return '#EF4444'
    }

    const card = { background: '#1E293B', border: '1px solid #334155', borderRadius: 12, padding: '20px 24px', marginBottom: 16 }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <div>
                    <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Skill Gap Analysis</h2>
                    <p style={{ color: '#64748B', fontSize: 13, marginTop: 4 }}>Compare your skills against top recommended jobs.</p>
                </div>
                <button onClick={load} style={{
                    background: 'transparent', border: '1px solid #334155', color: '#94A3B8',
                    borderRadius: 8, padding: '8px 14px', cursor: 'pointer', fontSize: 13,
                }}>↻ Refresh</button>
            </div>

            {error && <div style={{ ...card, borderColor: '#EF4444' }}>
                <span style={{ color: '#FCA5A5' }}>⚠ {error}</span>
            </div>}

            {loading ? (
                <div style={{ textAlign: 'center', padding: 60, color: '#64748B' }}>Analysing skill gaps...</div>
            ) : data?.analyses ? (<>

                {/* Radar chart */}
                {data.analyses.length >= 3 && (
                    <div style={card}>
                        <h4 style={{ marginBottom: 16, fontSize: 14, fontWeight: 600 }}>Match Score Radar</h4>
                        <ResponsiveContainer width="100%" height={240}>
                            <RadarChart data={data.analyses.map(a => ({
                                subject: a.target_job_title.slice(0, 18),
                                score: Math.round(a.match_score),
                            }))}>
                                <PolarGrid stroke="#334155" />
                                <PolarAngleAxis dataKey="subject" tick={{ fill: '#CBD5E1', fontSize: 11 }} />
                                <Radar dataKey="score" stroke="#6366F1" fill="#6366F1" fillOpacity={0.25} />
                                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8 }}
                                    formatter={v => [`${v}%`]} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {/* Per-job analysis */}
                {data.analyses.map((a, i) => (
                    <div key={i} style={card}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
                            <div>
                                <span style={{ fontWeight: 600, fontSize: 15 }}>{a.target_job_title}</span>
                                <span style={{
                                    background: color(a.readiness_label) + '20', color: color(a.readiness_label),
                                    padding: '2px 10px', borderRadius: 999, fontSize: 12, marginLeft: 10, fontWeight: 500
                                }}>
                                    {a.readiness_label}
                                </span>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: 24, fontWeight: 700, color: color(a.readiness_label) }}>
                                    {a.match_score.toFixed(0)}%
                                </div>
                                <div style={{ color: '#64748B', fontSize: 11 }}>match score</div>
                            </div>
                        </div>

                        {/* Progress bar */}
                        <div style={{ background: '#334155', borderRadius: 999, height: 6, marginBottom: 14 }}>
                            <div style={{
                                width: `${a.match_score}%`, background: 'linear-gradient(90deg,#6366F1,#14B8A6)',
                                borderRadius: 999, height: '100%', transition: 'width 0.8s'
                            }} />
                        </div>

                        {/* Skills */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
                            <div>
                                <div style={{ color: '#22C55E', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
                                    ✓ You have ({a.present_skills?.length})
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                    {(a.present_skills || []).map(s => (
                                        <span key={s} style={{
                                            background: '#14532D', color: '#86EFAC',
                                            padding: '2px 8px', borderRadius: 999, fontSize: 11
                                        }}>{s}</span>
                                    ))}
                                    {(a.present_skills || []).length === 0 && <span style={{ color: '#64748B', fontSize: 12 }}>None matched</span>}
                                </div>
                            </div>
                            <div>
                                <div style={{ color: '#EF4444', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
                                    ✗ Missing ({a.missing_required?.length})
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                    {(a.missing_required || []).map(s => (
                                        <span key={s} style={{
                                            background: '#450A0A', color: '#FCA5A5',
                                            padding: '2px 8px', borderRadius: 999, fontSize: 11
                                        }}>{s}</span>
                                    ))}
                                    {(a.missing_required || []).length === 0 && (
                                        <span style={{ color: '#22C55E', fontSize: 12 }}>None — you're ready! 🎉</span>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Courses */}
                        {a.course_suggestions?.length > 0 && (
                            <div>
                                <div style={{
                                    color: '#64748B', fontSize: 11, fontWeight: 600, textTransform: 'uppercase',
                                    letterSpacing: 1, marginBottom: 10
                                }}>Suggested Courses</div>
                                {a.course_suggestions.slice(0, 3).map((sg, j) => (
                                    <div key={j} style={{ background: '#0F172A', borderRadius: 8, padding: '10px 14px', marginBottom: 8 }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                                            <span style={{ fontWeight: 600, fontSize: 13 }}>{sg.skill}</span>
                                            <span style={{
                                                background: sg.priority === 'Required' ? '#450A0A' : '#451A03',
                                                color: sg.priority === 'Required' ? '#FCA5A5' : '#FDE68A',
                                                padding: '1px 8px', borderRadius: 999, fontSize: 11,
                                            }}>{sg.priority}</span>
                                        </div>
                                        {sg.courses?.slice(0, 2).map((c, k) => (
                                            <div key={k} style={{
                                                display: 'flex', justifyContent: 'space-between',
                                                padding: '5px 0', borderTop: k === 0 ? '1px solid #1E293B' : 'none'
                                            }}>
                                                <div>
                                                    <span style={{ color: '#CBD5E1', fontSize: 12 }}>{c.title}</span>
                                                    <span style={{ color: '#64748B', fontSize: 11, marginLeft: 8 }}>· {c.platform}</span>
                                                </div>
                                                <a href={c.url} target="_blank" rel="noreferrer"
                                                    style={{ color: '#6366F1', fontSize: 12, textDecoration: 'none' }}>
                                                    View →
                                                </a>
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </>) : !error && (
                <div style={{
                    background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                    padding: 40, textAlign: 'center', color: '#64748B'
                }}>
                    <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
                    <div>Get recommendations first, then skill gap analysis will appear here.</div>
                </div>
            )}
        </div>
    )
}