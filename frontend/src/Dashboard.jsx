export default function Dashboard({ user, onNavigate }) {
    const cards = [
        { label: 'Total Jobs', value: '525+', color: '#6366F1', emoji: '💼' },
        { label: 'Upload Resume', value: 'Get started →', color: '#14B8A6', emoji: '📄' },
        { label: 'Recommendations', value: 'AI-powered', color: '#F59E0B', emoji: '🎯' },
        { label: 'Skill Gap', value: 'Find gaps', color: '#22C55E', emoji: '📊' },
    ]

    return (
        <div>
            <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 6 }}>
                Welcome{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}! 👋
            </h2>
            <p style={{ color: '#64748B', marginBottom: 28 }}>
                Upload your resume to get AI-powered job matches instantly.
            </p>

            {/* Stat cards */}
            <div style={{
                display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px,1fr))',
                gap: 16, marginBottom: 28
            }}>
                {cards.map((c, i) => (
                    <div key={i} style={{
                        background: '#1E293B', border: '1px solid #334155',
                        borderRadius: 12, padding: '18px 20px'
                    }}>
                        <div style={{ fontSize: 28, marginBottom: 8 }}>{c.emoji}</div>
                        <div style={{ color: '#94A3B8', fontSize: 13 }}>{c.label}</div>
                        <div style={{ color: c.color, fontWeight: 700, fontSize: 18, marginTop: 4 }}>{c.value}</div>
                    </div>
                ))}
            </div>

            {/* How it works */}
            <div style={{
                background: '#1E293B', border: '1px solid #334155',
                borderRadius: 12, padding: '20px 24px', marginBottom: 20
            }}>
                <h3 style={{ marginBottom: 16, fontSize: 15, fontWeight: 600 }}>How it works</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 16 }}>
                    {[
                        { n: '1', t: 'Upload Resume', d: 'PDF or DOCX — skills extracted automatically', e: '📤' },
                        { n: '2', t: 'AI Matching', d: 'TF-IDF + Semantic embeddings rank 525+ jobs', e: '🤖' },
                        { n: '3', t: 'Skill Gap Report', d: 'See exactly what to learn for each job', e: '📈' },
                        { n: '4', t: 'Save & Apply', d: 'Star favourites and track your progress', e: '⭐' },
                    ].map(s => (
                        <div key={s.n}>
                            <div style={{ fontSize: 24, marginBottom: 6 }}>{s.e}</div>
                            <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{s.t}</div>
                            <div style={{ color: '#64748B', fontSize: 12, lineHeight: 1.5 }}>{s.d}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ display: 'flex', gap: 12 }}>
                <button onClick={() => onNavigate('resume')} style={{
                    background: '#6366F1', color: '#fff', border: 'none', borderRadius: 8,
                    padding: '10px 22px', fontWeight: 600, cursor: 'pointer', fontSize: 14,
                }}>📤 Upload Resume</button>
                <button onClick={() => onNavigate('jobs')} style={{
                    background: 'transparent', color: '#6366F1', border: '1px solid #6366F1',
                    borderRadius: 8, padding: '10px 22px', fontWeight: 600, cursor: 'pointer', fontSize: 14,
                }}>💼 Browse Jobs</button>
            </div>
        </div>
    )
}