import React, { useState } from 'react'
import { Link } from 'react-router-dom'

const AskPage = () => {
    let [question, setQuestion] = useState('')
    let [history, setHistory] = useState([]) // {question, answer, citedExpenses}
    let [asking, setAsking] = useState(false)
    let [error, setError] = useState(null)

    let handleAsk = async (e) => {
        e.preventDefault()
        if (!question.trim() || asking) return
        let askedQuestion = question
        setAsking(true)
        setError(null)
        try {
            let response = await fetch('/api/expenses/ask/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: askedQuestion })
            })
            let data = await response.json()
            if (!response.ok) {
                setError(data.error || 'Ask unavailable')
                return
            }
            setHistory([...history, {
                question: askedQuestion,
                answer: data.answer,
                citedExpenses: data.cited_expenses || []
            }])
            setQuestion('')
        } catch (e) {
            setError('Network error')
        } finally {
            setAsking(false)
        }
    }

    return (
        <div className='ask-page'>
            <div className="notes-header">
                <h2 className="notes-title">Ask your expenses</h2>
                <Link to="/" className="ask-back-link">Back</Link>
            </div>

            <div className="ask-history">
                {history.length === 0 && !asking && (
                    <p className="ask-empty">Ask things like "how much did I spend on food last month?"</p>
                )}
                {history.map((exchange, i) => (
                    <div className="ask-exchange" key={i}>
                        <p className="ask-question">{exchange.question}</p>
                        <p className="ask-answer">{exchange.answer}</p>
                        {exchange.citedExpenses.length > 0 && (
                            <div className="ask-citations">
                                {exchange.citedExpenses.map((exp) => (
                                    <span className="tag-chip" key={exp.id}>
                                        {exp.description} (${Number(exp.amount).toFixed(2)})
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
                {asking && <p className="ask-status">Thinking...</p>}
            </div>

            {error && <p className="ai-error">{error}</p>}

            <form className="ask-form" onSubmit={handleAsk}>
                <input
                    type="text"
                    placeholder="Ask a question..."
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    disabled={asking}
                />
                <button type="submit" disabled={asking || !question.trim()}>Ask</button>
            </form>
        </div>
    )
}

export default AskPage
