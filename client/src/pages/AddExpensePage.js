import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const todayISO = () => new Date().toISOString().slice(0, 10)

const AddExpensePage = () => {
    const navigate = useNavigate()
    const [mode, setMode] = useState('quick') // 'quick' | 'manual'

    // Quick-add (AI) state
    const [text, setText] = useState('')
    const [quickSubmitting, setQuickSubmitting] = useState(false)
    const [quickError, setQuickError] = useState(null)

    // Manual state
    const [amount, setAmount] = useState('')
    const [description, setDescription] = useState('')
    const [category, setCategory] = useState('')
    const [date, setDate] = useState(todayISO())
    const [manualSubmitting, setManualSubmitting] = useState(false)
    const [manualError, setManualError] = useState(null)

    const handleQuickAdd = async (e) => {
        e.preventDefault()
        if (!text.trim() || quickSubmitting) return
        setQuickSubmitting(true)
        setQuickError(null)
        try {
            const res = await fetch('/api/expenses/quick-add/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            })
            const data = await res.json()
            if (!res.ok) {
                setQuickError(data.error || 'Quick-add unavailable')
                return
            }
            navigate('/')
        } catch (err) {
            setQuickError('Network error')
        } finally {
            setQuickSubmitting(false)
        }
    }

    const handleManualAdd = async (e) => {
        e.preventDefault()
        if (!amount || !description || manualSubmitting) return
        setManualSubmitting(true)
        setManualError(null)
        try {
            const res = await fetch('/api/expenses/create/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount, description, category, date })
            })
            const data = await res.json()
            if (!res.ok) {
                setManualError(JSON.stringify(data))
                return
            }
            navigate('/')
        } catch (err) {
            setManualError('Network error')
        } finally {
            setManualSubmitting(false)
        }
    }

    return (
        <div className="add-expense-page">
            <div className="note-header">
                <h3>Add Expense</h3>
                <Link to="/" className="ask-back-link">Cancel</Link>
            </div>

            <div className="mode-toggle">
                <button className={mode === 'quick' ? 'mode-active' : ''} onClick={() => setMode('quick')}>
                    Quick Add (AI)
                </button>
                <button className={mode === 'manual' ? 'mode-active' : ''} onClick={() => setMode('manual')}>
                    Manual
                </button>
            </div>

            {mode === 'quick' && (
                <form className="add-expense-form" onSubmit={handleQuickAdd}>
                    <p className="ask-empty">
                        Describe the expense in your own words &mdash; e.g. "spent $12.50 on coffee this morning"
                        &mdash; and AI will fill in the amount, category, and date.
                    </p>
                    <textarea
                        className="quick-add-textarea"
                        placeholder="What did you spend on?"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        disabled={quickSubmitting}
                        rows={4}
                    />
                    {quickError && <p className="ai-error">{quickError}</p>}
                    <button type="submit" disabled={quickSubmitting || !text.trim()} className="primary-btn">
                        {quickSubmitting ? 'Adding...' : 'Add Expense'}
                    </button>
                </form>
            )}

            {mode === 'manual' && (
                <form className="add-expense-form" onSubmit={handleManualAdd}>
                    <label>
                        Amount
                        <input type="number" step="0.01" min="0" value={amount}
                            onChange={(e) => setAmount(e.target.value)} disabled={manualSubmitting} required />
                    </label>
                    <label>
                        Description
                        <input type="text" value={description}
                            onChange={(e) => setDescription(e.target.value)} disabled={manualSubmitting} required />
                    </label>
                    <label>
                        Category (leave blank to let AI categorize it later)
                        <input type="text" value={category}
                            onChange={(e) => setCategory(e.target.value)} disabled={manualSubmitting} />
                    </label>
                    <label>
                        Date
                        <input type="date" value={date}
                            onChange={(e) => setDate(e.target.value)} disabled={manualSubmitting} required />
                    </label>
                    {manualError && <p className="ai-error">{manualError}</p>}
                    <button type="submit" disabled={manualSubmitting} className="primary-btn">
                        {manualSubmitting ? 'Saving...' : 'Save Expense'}
                    </button>
                </form>
            )}
        </div>
    )
}

export default AddExpensePage
