import React from 'react';
import { Expense, ApiError } from '../types';
import { deleteExpense } from '../api/client';

interface Props {
  expenses: Expense[];
  onExpenseDeleted: () => void;
}

export function ExpenseList({ expenses, onExpenseDeleted }: Props) {
  const handleDelete = async (id: number) => {
    try {
      await deleteExpense(id);
      onExpenseDeleted();
    } catch (err) {
      const apiErr = err as ApiError;
      alert(apiErr.error || 'Failed to delete expense.');
    }
  };

  if (expenses.length === 0) {
    return <p className="empty-state">No expenses yet. Add one above!</p>;
  }

  return (
    <div className="expense-list">
      <h2>Expenses</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th className="amount-col">Amount</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{expense.date}</td>
              <td>{expense.description}</td>
              <td>
                <span className="category-badge">{expense.category_name}</span>
              </td>
              <td className="amount-col">${expense.amount.toFixed(2)}</td>
              <td>
                <button
                  className="delete-btn"
                  onClick={() => handleDelete(expense.id)}
                  title="Delete expense"
                >
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}