/**
 * API client — all HTTP calls to the backend live here.
 * Components never call fetch directly.
 */

import { Category, Expense, ExpenseSummary, ApiError } from '../types';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api';

/** Parse response or throw structured error. */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      error: 'Network error',
      code: 'NETWORK_ERROR',
    }));
    throw error;
  }
  return response.json();
}

// ── Categories ──────────────────────────────────────────────

export async function fetchCategories(): Promise<Category[]> {
  const response = await fetch(`${BASE_URL}/categories`);
  return handleResponse<Category[]>(response);
}

export async function createCategory(name: string): Promise<Category> {
  const response = await fetch(`${BASE_URL}/categories`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  return handleResponse<Category>(response);
}

export async function deleteCategory(id: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/categories/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      error: 'Failed to delete category',
      code: 'DELETE_FAILED',
    }));
    throw error;
  }
}

// ── Expenses ────────────────────────────────────────────────

export async function fetchExpenses(): Promise<Expense[]> {
  const response = await fetch(`${BASE_URL}/expenses`);
  return handleResponse<Expense[]>(response);
}

export async function createExpense(data: {
  amount: number;
  description: string;
  date: string;
  category_id: number;
}): Promise<Expense> {
  const response = await fetch(`${BASE_URL}/expenses`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<Expense>(response);
}

export async function deleteExpense(id: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/expenses/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      error: 'Failed to delete expense',
      code: 'DELETE_FAILED',
    }));
    throw error;
  }
}

// ── Summary ─────────────────────────────────────────────────

export async function fetchSummary(): Promise<ExpenseSummary[]> {
  const response = await fetch(`${BASE_URL}/expenses/summary`);
  return handleResponse<ExpenseSummary[]>(response);
}