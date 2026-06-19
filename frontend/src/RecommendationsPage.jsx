import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'
import client from './api'

export default function RecommendationsPage({ onSelectJob }) {
    const [recs, setRecs] = useState([])
    const [meta, setMeta] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [topK, setTopK] = useState(10)
    const [activeTab, setActiveTab] = useState('recommendations')
    const [compareData, setCompareData] = useState(null)
    const [compareLoading, setCompareLoading] = useState(false)

    async function load() {
        setLoading(true); setError('')
        try {
            const res = await client.get(`/api/recommendations/?top_k=${topK}`)
            setRecs(res.data.recommendations || [])
            setMeta(res.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load')
        } finally { setLoading(false) }
    }

    async function loadComparison() {
        setCompareLoading(true)
        try {
            const res = await client.get(`/api/recommendations/compare?top_k=10`)
            setCompareData(res.data)
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to load comparison')
        } finally { setCompareLoading(false) }
    }

    useEffect(() => { load() }, [topK])

    const chartData = recs.slice(0, 8).map(r => ({
        name: r.title.length > 20 ? r.title.slice(0, 20) + '…' : r.title,
        Hybrid: Math.round(r.hybrid_score * 100),
        Semantic: Math.round(r.semantic_score * 100),
        TFIDF: Math.round(r.tfidf_score * 100),
    }))

    return (
        <div>
            {/* Header */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                marginBottom: 20, flexWrap: 'wrap', gap: 12
            }}>
                <div>
                    <h2 style={{ fontSize: 20, fontWeight: 700, margin: 0 }}>Recommendations</h2>
                    {meta && <p style={{ color: '#64748B', fontSize: 13, marginTop: 4 }}>
                        {meta.approach} · {meta.experience_years} yrs exp · {meta.user_skills?.length} skills
                    </p>}
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                    <select value={topK} onChange={e => setTopK(+e.target.value)} style={{
                        background: '#1E293B', border: '1px solid #334155', color: '#F1F5F9',
                        borderRadius: 8, padding: '8px 12px', fontSize: 13, outline: 'none',
                    }}>
                        {[5, 10, 15, 20].map(k => <option key={k} value={k}>Top {k}</option>)}
                    </select>
                    <button onClick={load} style={{
                        background: 'transparent', border: '1px solid #334155', color: '#94A3B8',
                        borderRadius: 8, padding: '8px 14px', cursor: 'pointer', fontSize: 13,
                    }}>↻ Refresh</button>
                </div>
            </div>

            {/* Tabs */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
                {[
                    { id: 'recommendations', label: '🎯 My Recommendations' },
                    { id: 'compare', label: '⚖️ Compare Approaches' },
                ].map(tab => (
                    <button key={tab.id} onClick={() => {
                        setActiveTab(tab.id)
                        if (tab.id === 'compare' && !compareData) loadComparison()
                    }} style={{
                        padding: '9px 18px', borderRadius: 8, cursor: 'pointer',
                        fontWeight: 600, fontSize: 14,
                        background: activeTab === tab.id ? '#6366F1' : '#1E293B',
                        color: activeTab === tab.id ? '#fff' : '#64748B',
                        border: `1px solid ${activeTab === tab.id ? '#6366F1' : '#334155'}`,
                    }}>{tab.label}</button>
                ))}
            </div>

            {/* Error */}
            {error && (
                <div style={{
                    background: '#1E293B', border: '1px solid #EF4444', borderRadius: 12,
                    padding: '20px 24px', marginBottom: 20
                }}>
                    <div style={{ color: '#FCA5A5', fontWeight: 600, marginBottom: 4 }}>⚠ {error}</div>
                    <div style={{ color: '#64748B', fontSize: 13 }}>Upload your resume first.</div>
                </div>
            )}

            {/* ── Tab 1: Recommendations ── */}
            {activeTab === 'recommendations' && (
                loading ? (
                    <div style={{ textAlign: 'center', padding: 60, color: '#64748B' }}>
                        Loading recommendations...
                    </div>
                ) : recs.length > 0 ? (
                    <>
                        {/* Score chart */}
                        <div style={{
                            background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                            padding: '20px 24px', marginBottom: 20
                        }}>
                            <h4 style={{ marginBottom: 16, fontSize: 14, fontWeight: 600 }}>
                                Score Breakdown — Top 8
                            </h4>
                            <ResponsiveContainer width="100%" height={220}>
                                <BarChart data={chartData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                    <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748B', fontSize: 11 }} />
                                    <YAxis type="category" dataKey="name" tick={{ fill: '#CBD5E1', fontSize: 11 }} width={140} />
                                    <Tooltip
                                        contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8 }}
                                        formatter={v => [`${v}%`]}
                                    />
                                    <Bar dataKey="Hybrid" fill="#6366F1" radius={[0, 4, 4, 0]} />
                                    <Bar dataKey="Semantic" fill="#14B8A6" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Job cards */}
                        {recs.map(r => (
                            <div key={r.job_id} onClick={() => onSelectJob(r)}
                                style={{
                                    background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                                    padding: '16px 20px', marginBottom: 12, cursor: 'pointer',
                                    transition: 'border-color .2s', position: 'relative'
                                }}
                                onMouseEnter={e => e.currentTarget.style.borderColor = '#6366F1'}
                                onMouseLeave={e => e.currentTarget.style.borderColor = '#334155'}
                            >
                                <div style={{
                                    position: 'absolute', top: 14, left: -8, background: '#6366F1',
                                    color: '#fff', borderRadius: '0 4px 4px 0',
                                    padding: '2px 8px', fontSize: 11, fontWeight: 700
                                }}>
                                    #{r.rank}
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
                                    <div style={{ flex: 1, minWidth: 200 }}>
                                        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4, flexWrap: 'wrap' }}>
                                            <span style={{ fontWeight: 600, fontSize: 15 }}>{r.title}</span>
                                            {r.remote && (
                                                <span style={{ background: '#134E4A', color: '#5EEAD4', padding: '1px 8px', borderRadius: 999, fontSize: 11 }}>
                                                    Remote
                                                </span>
                                            )}
                                        </div>
                                        <div style={{ color: '#64748B', fontSize: 13, marginBottom: 8 }}>
                                            🏢 {r.company} · 📍 {r.location} · ⏱ {r.experience_level}
                                        </div>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                            {(r.required_skills || []).slice(0, 5).map(s => (
                                                <span key={s} style={{
                                                    background: '#0F172A', border: '1px solid #334155',
                                                    color: '#94A3B8', padding: '1px 8px', borderRadius: 999, fontSize: 11
                                                }}>{s}</span>
                                            ))}
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: 24, fontWeight: 700, color: '#6366F1' }}>
                                            {(r.hybrid_score * 100).toFixed(0)}%
                                        </div>
                                        <div style={{ color: '#64748B', fontSize: 11 }}>match</div>
                                        <div style={{ color: '#14B8A6', fontSize: 12, marginTop: 2 }}>
                                            {r.skill_overlap_pct}% skills ✓
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </>
                ) : !error && (
                    <div style={{
                        background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                        padding: 40, textAlign: 'center', color: '#64748B'
                    }}>
                        <div style={{ fontSize: 40, marginBottom: 12 }}>🎯</div>
                        <div style={{ fontWeight: 600, marginBottom: 6, color: '#F1F5F9' }}>No recommendations yet</div>
                        <div>Upload your resume to generate personalised job matches.</div>
                    </div>
                )
            )}

            {/* ── Tab 2: Compare Approaches ── */}
            {activeTab === 'compare' && (
                compareLoading ? (
                    <div style={{ textAlign: 'center', padding: 60, color: '#64748B' }}>
                        Comparing approaches...
                    </div>
                ) : compareData ? (
                    <div>
                        {/* Approach description cards */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
                            {[compareData.approach_A, compareData.approach_B].map((ap, i) => (
                                <div key={i} style={{
                                    background: '#1E293B',
                                    border: `2px solid ${i === 0 ? '#F59E0B' : '#6366F1'}`,
                                    borderRadius: 12, padding: '16px 20px'
                                }}>
                                    <div style={{
                                        fontWeight: 700, fontSize: 15, marginBottom: 6,
                                        color: i === 0 ? '#F59E0B' : '#6366F1'
                                    }}>
                                        {i === 0 ? '🔤' : '🧠'} {ap.name}
                                    </div>
                                    <div style={{ color: '#64748B', fontSize: 13, lineHeight: 1.5 }}>
                                        {ap.description}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Side by side results */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
                            {[compareData.approach_A, compareData.approach_B].map((ap, i) => (
                                <div key={i}>
                                    <h4 style={{ color: '#F1F5F9', marginBottom: 12, fontSize: 14, fontWeight: 600 }}>
                                        {i === 0 ? '🔤' : '🧠'} {ap.name}
                                    </h4>
                                    {ap.results.map(r => (
                                        <div key={r.job_id} style={{
                                            background: '#0F172A', border: '1px solid #334155',
                                            borderRadius: 8, padding: '10px 14px', marginBottom: 8
                                        }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                                                <span style={{ color: '#F1F5F9', fontWeight: 600, fontSize: 13 }}>
                                                    #{r.rank} {r.title.length > 25 ? r.title.slice(0, 25) + '…' : r.title}
                                                </span>
                                                <span style={{
                                                    fontWeight: 700, fontSize: 13,
                                                    color: i === 0 ? '#F59E0B' : '#6366F1'
                                                }}>
                                                    {(r.score * 100).toFixed(0)}%
                                                </span>
                                            </div>
                                            <div style={{ color: '#64748B', fontSize: 12 }}>
                                                🏢 {r.company} · {r.skill_overlap}% skills ✓
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>

                        {/* Explanation */}
                        <div style={{
                            background: '#1E293B', border: '1px solid #334155',
                            borderRadius: 12, padding: '16px 20px'
                        }}>
                            <h4 style={{ color: '#F1F5F9', marginBottom: 10, fontSize: 14, fontWeight: 600 }}>
                                📊 Why do results differ?
                            </h4>
                            <p style={{ color: '#94A3B8', fontSize: 13, lineHeight: 1.8, margin: 0 }}>
                                <strong style={{ color: '#F59E0B' }}>TF-IDF + Cosine Similarity</strong> works
                                by converting job descriptions into word frequency vectors and finding the
                                closest match to your profile. It's fast and precise on exact keywords but
                                misses semantic meaning — "ML Engineer" and "Machine Learning Engineer"
                                look different to it.
                                <br /><br />
                                <strong style={{ color: '#6366F1' }}>Hybrid (TF-IDF + NLP Embeddings)</strong> adds
                                a sentence-transformer model (all-MiniLM-L6-v2) that encodes meaning into
                                384-dimensional vectors. It understands that "software developer" ≈ "software engineer",
                                making recommendations more robust across varied job descriptions.
                                The hybrid score = 0.4 × TF-IDF + 0.6 × Semantic + 0.2 × Skill Overlap.
                            </p>
                        </div>
                    </div>
                ) : (
                    <div style={{
                        background: '#1E293B', border: '1px solid #334155', borderRadius: 12,
                        padding: 40, textAlign: 'center', color: '#64748B'
                    }}>
                        <div style={{ fontSize: 40, marginBottom: 12 }}>⚖️</div>
                        <div>Upload your resume first to compare approaches.</div>
                    </div>
                )
            )}
        </div>
    )
}