import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import CreateAccountForm from './components/CreateAccountForm';
import TransactionImportPreview from './components/TransactionImportPreview';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [csvFile, setCsvFile] = useState(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [previewTransactions, setPreviewTransactions] = useState([]);

  const categories = ['Food', 'Auto', 'Rent', 'Other'];

  // Fetch accounts
  useEffect(() => {
    const fetchAccounts = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/accounts/`);
        setAccounts(response.data);
      } catch (error) {
        console.error('Error fetching accounts:', error);
      }
    };
    fetchAccounts();
  }, []);

  // Fetch transactions when account is selected
  useEffect(() => {
    const fetchTransactions = async () => {
      if (selectedAccount) {
        try {
          const response = await axios.get(`${API_BASE_URL}/accounts/${selectedAccount.id}/transactions/`);
          setTransactions(response.data);
        } catch (error) {
          console.error('Error fetching transactions:', error);
        }
      }
    };
    fetchTransactions();
  }, [selectedAccount]);

  // Create a new account
  const handleCreateAccount = async (accountName) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/accounts/`, { name: accountName });
      setAccounts([...accounts, response.data]);
      setIsModalOpen(false);
    } catch (error) {
      console.error('Error creating account:', error);
    }
  };

  // Upload CSV transactions
  const handleCsvUpload = async (e) => {
    e.preventDefault();
    if (!selectedAccount || !csvFile) return;

    const formData = new FormData();
    formData.append('file', csvFile);

    try {
      // First, get the preview of transactions
      const response = await axios.post(
        `${API_BASE_URL}/preview-transactions/${selectedAccount.id}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      setPreviewTransactions(response.data);
      setIsPreviewMode(true);
      setCsvFile(null);
    } catch (error) {
      console.error('Error previewing transactions:', error);
    }
  };


 // this is ca comment
  const handleConfirmImport = async (selectedTransactions) => {
    try {
      const formattedTransactions = selectedTransactions.map(transaction => ({
        date: transaction.date,
        description: transaction.description,
        credit: transaction.credit,
        debit: transaction.debit,
        category: transaction.category,
        account_id: selectedAccount.id
      }));

      const response = await axios.post(
        `${API_BASE_URL}/import-transactions/${selectedAccount.id}`,
        { transactions: formattedTransactions }
      );
      
      // Update the account in the accounts list with the new balance
      const updatedAccounts = accounts.map(account => 
        account.id === response.data.id ? response.data : account
      );
      setAccounts(updatedAccounts);
      
      // Update selected account if it's the one that was modified
      if (selectedAccount.id === response.data.id) {
        setSelectedAccount(response.data);
      }
      
      // Refresh transactions
      const transactionsResponse = await axios.get(
        `${API_BASE_URL}/accounts/${selectedAccount.id}/transactions/`
      );
      setTransactions(transactionsResponse.data);
      
      // Exit preview mode
      setIsPreviewMode(false);
    } catch (error) {
      console.error('Error importing transactions:', error);
    }
  };

  // Update transaction category
  const handleCategoryChange = async (transactionId, category) => {
    try {
      await axios.patch(`${API_BASE_URL}/transactions/${transactionId}`, { category });
      setTransactions(transactions.map(transaction =>
        transaction.id === transactionId ? { ...transaction, category } : transaction
      ));
    } catch (error) {
      console.error('Error updating transaction category:', error);
    }
  };

  const fetchCategoryBreakdown = async () => {
    if (!selectedAccount) return;
    try {
      const response = await axios.get(`${API_BASE_URL}/accounts/${selectedAccount.id}/category-breakdown`);
      setCategoryBreakdown(response.data.totals);
    } catch (error) {
      console.error('Error fetching category breakdown:', error);
    }
  };

  if (isPreviewMode) {
    return (
      <TransactionImportPreview
        transactions={previewTransactions}
        onConfirm={handleConfirmImport}
        onCancel={() => setIsPreviewMode(false)}
      />
    );
  }

  return (
    <div className="App">
      <h1>Personal Finance Tracker</h1>

      {/* Account List */}
      <div className="account-section">
        <div className="account-header">
          <h2>Accounts</h2>
          <button onClick={() => setIsModalOpen(true)} className="create-account-btn">
            Create Account
          </button>
        </div>
        <div className="account-list">
          {accounts.map(account => (
            <div 
              key={account.id} 
              className={`account-item ${selectedAccount?.id === account.id ? 'selected' : ''}`}
              onClick={() => setSelectedAccount(account)}
            >
              {account.name}
            </div>
          ))}
        </div>
      </div>

      {/* Create Account Modal */}
        <CreateAccountForm 
          isOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateAccount}
        />

      {/* Selected Account Transactions */}
      {selectedAccount && (
        <div className="account-details">
          <h2>{selectedAccount.name} Transactions</h2>
          
          {/* CSV Upload Form */}
          <form onSubmit={handleCsvUpload}>
            <input 
              type="file" 
              accept=".csv" 
              onChange={(e) => setCsvFile(e.target.files[0])} 
            />
            <button type="submit" disabled={!csvFile}>Upload Transactions</button>
          </form>

          {/* Transactions Table */}
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Credit</th>
                <th>Debit</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(transaction => (
                <tr key={transaction.id}>
                  <td>{new Date(transaction.date).toLocaleDateString()}</td>
                  <td>{transaction.description}</td>
                  <td>{transaction.credit}</td>
                  <td>{transaction.debit}</td>
                  <td>
                    <select
                      value={transaction.category || 'Other'}
                      onChange={(e) => handleCategoryChange(transaction.id, e.target.value)}
                    >
                      {categories.map(category => (
                        <option key={category} value={category}>
                          {category}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Category Breakdown Button and Display */}
          <div className="category-breakdown">
            <button onClick={fetchCategoryBreakdown}>
              Show Category Breakdown
            </button>
            {categoryBreakdown && (
              <div className="breakdown-display">
                <h3>Spending by Category</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Total Spent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryBreakdown.map(item => (
                      <tr key={item.category}>
                        <td>{item.category}</td>
                        <td>${item.total.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
