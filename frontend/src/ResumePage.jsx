import { useState, useEffect } from 'react'
import client from './api'

export default function ResumePage() {
    const [file, setFile] = useState(null)
    const [parsed, setParsed] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [drag, setDrag] = useState(false)

    useEffect(() => {
        client.get('/api/resume/parsed').then(r => setParsed(r.data)).catch(() => { })
    }, [])

    async function upload() {
        if (!file) return
        setLoading(true); setError('')
        const form = new FormData()
        form.append('file', file)
        try {
            const res = await client.post('/api/resume/upload', form,
                { headers: { 'Content-Type': 'multipart/form-data' } })
            setParsed(res.data); setFile(null)
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed')
        } finally { setLoading(false) }
    }

    const card = { background: '#1E293B', border: '1px solid #334155', borderRadius: 12, padding: '20px 24px' }
    const badge = (text, color = '#312E81', tc = '#A5B4FC') => (
        <span style={{
            background: color, color: tc, padding: '2px 10px', borderRadius: 999,
            fontSize: 12, fontWeight: 500
        }}>{text}</span>
    )

    return (
        <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 6 }}>Resume Analysis</h2>
            <p style={{ color: '#64748B', marginBottom: 24, fontSize: 14 }}>
                Upload PDF or DOCX — skills, experience and education extracted automatically.
            </p>

            {/* Upload zone */}
            <div style={{ ...card, marginBottom: 24 }}>
                <div
                    onDragOver={e => { e.preventDefault(); setDrag(true) }}
                    onDragLeave={() => setDrag(false)}
                    onDrop={e => { e.preventDefault(); setDrag(false); setFile(e.dataTransfer.files[0]) }}
                    style={{
                        border: `2px dashed ${drag || file ? '#6366F1' : '#334155'}`,
                        borderRadius: 10, padding: '32px 20px', textAlign: 'center',
                        background: drag ? '#6366F108' : 'transparent', transition: 'all .2s',
                    }}
                >
                    <div style={{ fontSize: 36, marginBottom: 8 }}>📄</div>
                    <div style={{ fontWeight: 600, color: file ? '#F1F5F9' : '#64748B', marginBottom: 6 }}>
                        {file ? file.name : 'Drag & drop your resume here'}
                    </div>
                    <div style={{ color: '#64748B', fontSize: 13, marginBottom: 16 }}>PDF or DOCX, max 5MB</div>
                    <label style={{
                        background: '#6366F1', color: '#fff', padding: '9px 20px', borderRadius: 8,
                        fontWeight: 600, fontSize: 14, cursor: 'pointer',
                    }}>
                        Choose File
                        <input type="file" accept=".pdf,.docx" style={{ display: 'none' }}
                            onChange={e => setFile(e.target.files[0])} />
                    </label>
                </div>

                {error && <div style={{
                    marginTop: 12, color: '#FCA5A5', background: '#450A0A',
                    borderRadius: 8, padding: '10px 14px', fontSize: 13
                }}>{error}</div>}

                {file && (
                    <div style={{ marginTop: 16, display: 'flex', gap: 10 }}>
                        <button onClick={upload} disabled={loading} style={{
                            background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8,
                            padding: '9px 18px', fontWeight: 600, cursor: 'pointer',
                        }}>
                            {loading ? 'Parsing...' : '🔍 Parse Resume'}
                        </button>
                        <button onClick={() => setFile(null)} style={{
                            background: 'transparent', color: '#64748B', border: 'none', cursor: 'pointer',
                        }}>Clear</button>
                    </div>
                )}
            </div>

            {/* Parsed results */}
            {parsed && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 18 }}>✅</span>
                        <span style={{ color: '#22C55E', fontWeight: 600 }}>
                            Parsed: {parsed.filename} — {parsed.parsed?.skills?.length || 0} skills detected
                        </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                        {/* Contact */}
                        <div style={card}>
                            <h4 style={{ marginBottom: 12, fontSize: 14, fontWeight: 600 }}>Contact Info</h4>
                            {[
                                ['Name', parsed.parsed?.name],
                                ['Email', parsed.parsed?.email],
                                ['Phone', parsed.parsed?.phone],
                                ['LinkedIn', parsed.parsed?.linkedin],
                                ['GitHub', parsed.parsed?.github],
                                ['Experience', parsed.parsed?.experience_years ? `${parsed.parsed.experience_years} yrs` : null],
                            ].filter(r => r[1]).map(([label, val]) => (
                                <div key={label} style={{ display: 'flex', gap: 8, marginBottom: 6, fontSize: 13 }}>
                                    <span style={{ color: '#64748B', minWidth: 75 }}>{label}</span>
                                    <span style={{ color: '#CBD5E1', wordBreak: 'break-all' }}>{val}</span>
                                </div>
                            ))}
                        </div>

                        {/* Education */}
                        <div style={card}>
                            <h4 style={{ marginBottom: 12, fontSize: 14, fontWeight: 600 }}>Education</h4>
                            {(parsed.parsed?.education || []).slice(0, 3).map((e, i) => (
                                <div key={i} style={{ marginBottom: 8 }}>
                                    {badge(e.degree, '#134E4A', '#5EEAD4')}
                                    {e.context && <p style={{ color: '#64748B', fontSize: 12, marginTop: 4 }}>
                                        {e.context.slice(0, 80)}
                                    </p>}
                                </div>
                            ))}
                            {(parsed.parsed?.certifications || []).length > 0 && <>
                                <h4 style={{ margin: '14px 0 10px', fontSize: 14, fontWeight: 600 }}>Certifications</h4>
                                {parsed.parsed.certifications.slice(0, 3).map((c, i) => (
                                    <div key={i} style={{ marginBottom: 6 }}>{badge(c.slice(0, 50), '#451A03', '#FDE68A')}</div>
                                ))}
                            </>}
                        </div>
                    </div>

                    {/* Skills */}
                    <div style={card}>
                        <h4 style={{ marginBottom: 14, fontSize: 14, fontWeight: 600 }}>
                            Detected Skills ({parsed.parsed?.skills?.length || 0})
                        </h4>
                        {Object.entries(parsed.parsed?.skills_by_category || {}).map(([cat, skills]) => (
                            <div key={cat} style={{ marginBottom: 14 }}>
                                <div style={{
                                    color: '#64748B', fontSize: 11, textTransform: 'uppercase',
                                    letterSpacing: 1, marginBottom: 6
                                }}>{cat}</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                                    {skills.map(s => <span key={s} style={{
                                        background: '#312E81', color: '#A5B4FC',
                                        padding: '2px 10px', borderRadius: 999, fontSize: 12,
                                    }}>{s}</span>)}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}