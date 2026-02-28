/** Shared TypeScript interfaces for API data. */

export interface Category {
  id: number;
  name: string;
  created_at: string;
}

export interface Expense {
  id: number;
  amount: number;
  description: string;
  date: string;
  category_id: number;
  category_name: string;
  created_at: string;
}

export interface ExpenseSummary {
  category: string;
  total: number;
  count: number;
}

export interface ApiError {
  error: string;
  code: string;
  details?: Record<string, string[]>;
}

/** Form data for creating/updating an expense. */
export interface ExpenseFormData {
  amount: string;
  description: string;
  date: string;
  category_id: string;
}