import React, { useState } from 'react';
import Modal from './Modal';

function CreateAccountForm({ isOpen, onClose, onSubmit }) {
  const [newAccountName, setNewAccountName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(newAccountName);
    setNewAccountName('');
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Account">
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={newAccountName} 
          onChange={(e) => setNewAccountName(e.target.value)}
          placeholder="Account Name" 
          required 
        />
        <div className="modal-buttons">
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="submit">Create Account</button>
        </div>
      </form>
    </Modal>
  );
}

export default CreateAccountForm;
