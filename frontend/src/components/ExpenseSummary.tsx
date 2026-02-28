import React from 'react';
import { ExpenseSummary as SummaryData } from '../types';

interface Props {
  summary: SummaryData[];
}

export function ExpenseSummary({ summary }: Props) {
  if (summary.length === 0) {
    return null;
  }

  const total = summary.reduce((sum, item) => sum + item.total, 0);

  return (
    <div className="expense-summary">
      <h2>Spending Summary</h2>
      <div className="summary-cards">
        {summary.map((item) => (
          <div key={item.category} className="summary-card">
            <div className="summary-category">{item.category}</div>
            <div className="summary-total">${item.total.toFixed(2)}</div>
            <div className="summary-count">
              {item.count} expense{item.count !== 1 ? 's' : ''}
            </div>
            <div className="summary-bar">
              <div
                className="summary-bar-fill"
                style={{ width: `${(item.total / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="summary-total-row">
        <strong>Total: ${total.toFixed(2)}</strong>
      </div>
    </div>
  );
}