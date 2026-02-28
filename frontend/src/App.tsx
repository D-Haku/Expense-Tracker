import React, { useState, useEffect, useCallback } from 'react';
import { Category, Expense, ExpenseSummary as SummaryData } from './types';
import { fetchCategories, fetchExpenses, fetchSummary } from './api/client';
import { ExpenseForm } from './components/ExpenseForm';
import { ExpenseList } from './components/ExpenseList';
import { ExpenseSummary } from './components/ExpenseSummary';
import './App.css';

function App() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [summary, setSummary] = useState<SummaryData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setError(null);
      const [cats, exps, sum] = await Promise.all([
        fetchCategories(),
        fetchExpenses(),
        fetchSummary(),
      ]);
      setCategories(cats);
      setExpenses(exps);
      setSummary(sum);
    } catch {
      setError('Failed to load data. Is the backend running on port 5000?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return <div className="app-loading">Loading...</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>💰 Expense Tracker</h1>
      </header>

      {error && <div className="app-error">{error}</div>}

      <main className="app-main">
        <section className="app-form-section">
          <ExpenseForm categories={categories} onExpenseCreated={loadData} />
        </section>

        <section className="app-summary-section">
          <ExpenseSummary summary={summary} />
        </section>

        <section className="app-list-section">
          <ExpenseList expenses={expenses} onExpenseDeleted={loadData} />
        </section>
      </main>
    </div>
  );
}

export default App;