'use client';
import { useEffect, useState } from 'react';

type CreditTransaction = {
  type: string;
  amount: number;
  description: string;
  timestamp: string;
};

export default function CreditPage() {
  const [credits, setCredits] = useState(0);
  const [transactions, setTransactions] = useState<CreditTransaction[]>([]);

  useEffect(() => {
    fetch('/api/credits/history')
      .then(res => res.json())
      .then(data => {
        setCredits(data.credits);
        setTransactions(data.transactions);
      });
  }, []);

  const handleRefill = async () => {
    await fetch('/api/credits/refill', { method: 'POST' });
    location.reload();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">💳 Credits</h1>

      <div className="mb-6">
        <p className="text-lg text-gray-700 dark:text-gray-200">Current Balance: <strong>{credits}</strong> credits</p>
        <button
          onClick={handleRefill}
          className="mt-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded shadow"
        >
          Add 100 Dev Credits
        </button>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Transaction History</h2>
        <table className="w-full border dark:border-gray-700">
          <thead>
            <tr className="bg-gray-100 dark:bg-neutral-700 text-left text-sm">
              <th className="p-2">Type</th>
              <th className="p-2">Amount</th>
              <th className="p-2">Description</th>
              <th className="p-2">Date</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx, i) => (
              <tr key={i} className="border-t dark:border-gray-700 text-sm">
                <td className="p-2">{tx.type}</td>
                <td className="p-2">{tx.amount}</td>
                <td className="p-2">{tx.description}</td>
                <td className="p-2">{new Date(tx.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
