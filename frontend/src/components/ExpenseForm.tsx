import React, { useState } from 'react';
import { Category, ExpenseFormData, ApiError } from '../types';
import { createExpense } from '../api/client';

interface Props {
  categories: Category[];
  onExpenseCreated: () => void;
}

const INITIAL_FORM: ExpenseFormData = {
  amount: '',
  description: '',
  date: new Date().toISOString().split('T')[0],
  category_id: '',
};

export function ExpenseForm({ categories, onExpenseCreated }: Props) {
  const [form, setForm] = useState<ExpenseFormData>(INITIAL_FORM);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await createExpense({
        amount: parseFloat(form.amount),
        description: form.description.trim(),
        date: form.date,
        category_id: parseInt(form.category_id, 10),
      });
      setForm(INITIAL_FORM);
      onExpenseCreated();
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr.details) {
        const messages = Object.values(apiErr.details).flat().join(', ');
        setError(messages);
      } else {
        setError(apiErr.error || 'Failed to create expense.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="expense-form">
      <h2>Add Expense</h2>
      {error && <div className="error-message">{error}</div>}

      <div className="form-row">
        <label htmlFor="amount">Amount ($)</label>
        <input
          id="amount"
          name="amount"
          type="number"
          step="0.01"
          min="0.01"
          value={form.amount}
          onChange={handleChange}
          required
          placeholder="0.00"
        />
      </div>

      <div className="form-row">
        <label htmlFor="description">Description</label>
        <input
          id="description"
          name="description"
          type="text"
          maxLength={200}
          value={form.description}
          onChange={handleChange}
          required
          placeholder="What did you spend on?"
        />
      </div>

      <div className="form-row">
        <label htmlFor="date">Date</label>
        <input
          id="date"
          name="date"
          type="date"
          max={new Date().toISOString().split('T')[0]}
          value={form.date}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-row">
        <label htmlFor="category_id">Category</label>
        <select
          id="category_id"
          name="category_id"
          value={form.category_id}
          onChange={handleChange}
          required
        >
          <option value="">Select a category</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      <button type="submit" disabled={submitting}>
        {submitting ? 'Adding...' : 'Add Expense'}
      </button>
    </form>
  );
}