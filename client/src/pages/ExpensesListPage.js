import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import ExpenseItem from '../components/ExpenseItem'

const ExpensesListPage = () => {
    const [expenses, setExpenses] = useState([])
    const [loading, setLoading] = useState(true)

    const loadExpenses = () => {
        setLoading(true)
        fetch('/api/expenses/')
            .then(res => res.json())
            .then(data => {
                setExpenses(data)
                setLoading(false)
            })
    }

    useEffect(() => {
        loadExpenses()
    }, [])

    const handleDelete = async (id) => {
        await fetch(`/api/expenses/${id}/delete/`, { method: 'DELETE' })
        setExpenses(expenses.filter(e => e.id !== id))
    }

    const total = expenses.reduce((sum, e) => sum + Number(e.amount), 0)

    return (
        <div className="expenses-page">
            <div className="notes-header">
                <h2 className="notes-title">Your Expenses</h2>
                <span className="notes-count">${total.toFixed(2)}</span>
            </div>

            <div className="expenses-list">
                {loading && <p className="ask-empty">Loading...</p>}
                {!loading && expenses.length === 0 && (
                    <p className="ask-empty">No expenses yet. Add your first one.</p>
                )}
                {expenses.map(expense => (
                    <ExpenseItem key={expense.id} expense={expense} onDelete={handleDelete} />
                ))}
            </div>

            <Link to="/add" className="floating-button" aria-label="Add expense">+</Link>
        </div>
    )
}

export default ExpensesListPage
