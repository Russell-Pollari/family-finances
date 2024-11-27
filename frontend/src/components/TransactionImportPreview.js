import React, { useState } from 'react';

function TransactionImportPreview({ transactions, onConfirm, onCancel }) {
  const [selectedTransactions, setSelectedTransactions] = useState(
    transactions.map((t, index) => ({ ...t, selected: true, id: index }))
  );

  const handleToggleAll = (checked) => {
    setSelectedTransactions(selectedTransactions.map(t => ({ ...t, selected: checked })));
  };

  const handleToggleTransaction = (index) => {
    setSelectedTransactions(selectedTransactions.map((t, i) => 
      i === index ? { ...t, selected: !t.selected } : t
    ));
  };

  const handleEditTransaction = (index, field, value) => {
    setSelectedTransactions(selectedTransactions.map((t, i) => 
      i === index ? { ...t, [field]: value } : t
    ));
  };

  const handleConfirm = () => {
    const selectedItems = selectedTransactions.filter(t => t.selected);
    onConfirm(selectedItems);
  };

  return (
    <div className="transaction-preview">
      <h2>Review Transactions</h2>
      <div className="preview-controls">
        <label>
          <input
            type="checkbox"
            checked={selectedTransactions.every(t => t.selected)}
            onChange={(e) => handleToggleAll(e.target.checked)}
          />
          Select All
        </label>
        <div className="preview-buttons">
          <button onClick={onCancel} className="cancel-btn">Cancel</button>
          <button 
            onClick={handleConfirm} 
            className="confirm-btn"
            disabled={!selectedTransactions.some(t => t.selected)}
          >
            Import Selected ({selectedTransactions.filter(t => t.selected).length})
          </button>
        </div>
      </div>

      <div className="preview-table-container">
        <table className="preview-table">
          <thead>
            <tr>
              <th></th>
              <th>Date</th>
              <th>Description</th>
              <th>Category</th>
              <th>Credit</th>
              <th>Debit</th>
            </tr>
          </thead>
          <tbody>
            {selectedTransactions.map((transaction, index) => (
              <tr key={index} className={transaction.selected ? '' : 'deselected'}>
                <td>
                  <input
                    type="checkbox"
                    checked={transaction.selected}
                    onChange={() => handleToggleTransaction(index)}
                  />
                </td>
                <td>
                  <input
                    type="date"
                    value={transaction.date}
                    onChange={(e) => handleEditTransaction(index, 'date', e.target.value)}
                    disabled={!transaction.selected}
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={transaction.description}
                    onChange={(e) => handleEditTransaction(index, 'description', e.target.value)}
                    disabled={!transaction.selected}
                  />
                </td>
                <td>
                  <select
                    value={transaction.category || 'Other'}
                    onChange={(e) => handleEditTransaction(index, 'category', e.target.value)}
                    disabled={!transaction.selected}
                  >
                    <option value="Food">Food</option>
                    <option value="Auto">Auto</option>
                    <option value="Rent">Rent</option>
                    <option value="Other">Other</option>
                  </select>
                </td>
                <td>
                  <input
                    type="number"
                    value={transaction.credit || ''}
                    onChange={(e) => handleEditTransaction(index, 'credit', e.target.value)}
                    disabled={!transaction.selected}
                  />
                </td>
                <td>
                  <input
                    type="number"
                    value={transaction.debit || ''}
                    onChange={(e) => handleEditTransaction(index, 'debit', e.target.value)}
                    disabled={!transaction.selected}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TransactionImportPreview;
