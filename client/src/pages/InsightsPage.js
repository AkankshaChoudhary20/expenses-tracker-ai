import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const PERIODS = [
    { value: 'week', label: 'This week' },
    { value: 'month', label: 'This month' },
    { value: 'all', label: 'All time' },
]

const InsightsPage = () => {
    const [period, setPeriod] = useState('month')
    const [data, setData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        setLoading(true)
        setError(null)
        fetch(`/api/expenses/insights/?period=${period}`)
            .then(async (res) => {
                const body = await res.json()
                if (!res.ok) {
                    setError(body.error || 'Insights unavailable')
                    setData(null)
                    return
                }
                setData(body)
            })
            .catch(() => setError('Network error'))
            .finally(() => setLoading(false))
    }, [period])

    return (
        <div className="insights-page">
            <div className="notes-header">
                <h2 className="notes-title">Spending Insights</h2>
                <Link to="/" className="ask-back-link">Back</Link>
            </div>

            <div className="mode-toggle">
                {PERIODS.map(p => (
                    <button
                        key={p.value}
                        className={period === p.value ? 'mode-active' : ''}
                        onClick={() => setPeriod(p.value)}
                    >
                        {p.label}
                    </button>
                ))}
            </div>

            <div className="ai-panel" style={{ margin: '16px' }}>
                {loading && <p className="ask-status">Analyzing your spending...</p>}
                {!loading && error && <p className="ai-error">{error}</p>}
                {!loading && data && (
                    <>
                        <p className="ai-panel-label">
                            {data.expense_count} expenses &middot; ${data.total.toFixed(2)} total
                        </p>
                        <p className="ai-suggestion-text">{data.summary}</p>
                    </>
                )}
            </div>
        </div>
    )
}

export default InsightsPage
