const ExpenseItem = ({ expense, onDelete }) => {
    return (
        <div className="expense-list-item">
            <div className="expense-item-main">
                <h3>{expense.description}</h3>
                <p>
                    <span>${Number(expense.amount).toFixed(2)}</span>
                    {expense.category && <span className="tag-chip">{expense.category}</span>}
                    <span className="expense-date">{expense.date}</span>
                </p>
            </div>
            <button className="expense-delete-btn" onClick={() => onDelete(expense.id)} aria-label="Delete expense">
                &times;
            </button>
        </div>
    )
}

export default ExpenseItem
