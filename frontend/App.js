import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';
import logo from './corn.png'; 

function App() {
  const [cornData, setCornData] = useState([]);
  const [newCorn, setNewCorn] = useState({ name: '', characteristics: '' });

  useEffect(() => {
    fetchCornData();
  }, []);

  const fetchCornData = () => {
    axios.get('/api/corn')
      .then(response => {
        console.log(response.data); // Log the response data
        setCornData(response.data.corn_entries);
      })
      .catch(error => {
        console.error('Error fetching corn data:', error);
      });
  };

  const handleAddCorn = () => {
    axios.post('/api/corn', newCorn)
      .then(response => {
        console.log(response.data);
        fetchCornData();
        setNewCorn({ name: '', characteristics: '' });
      })
      .catch(error => {
        console.error('Error adding corn entry:', error);
      });
  };

  const handleDeleteCorn = (id) => {
    axios.delete(`/api/corn/${id}`)
      .then(response => {
        console.log(response.data);
        fetchCornData();
      })
      .catch(error => {
        console.error('Error deleting corn entry:', error);
      });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to CornHub! The Hub of all Corn</h1>
      </header>
      <div className="Corn-form">
        <input
          type="text"
          placeholder="Name"
          value={newCorn.name}
          onChange={(e) => setNewCorn({ ...newCorn, name: e.target.value })}
        />
        <input
          type="text"
          placeholder="Description"
          value={newCorn.characteristics}
          onChange={(e) => setNewCorn({ ...newCorn, characteristics: e.target.value })}
        />
        <button onClick={handleAddCorn}>Add Corn</button>
      </div>
      <table className="Corn-table">
        <thead>
          <tr>
            <th>Sort</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {cornData.length > 0 ? (
            cornData.map(corn => (
              <tr key={corn.id}>
                <td>{corn.name}</td>
                <td>{corn.characteristics}</td>
                <td>
                  <button onClick={() => handleDeleteCorn(corn.id)}>Delete</button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3">No data available</td>
            </tr>
          )}
        </tbody>
      </table>
      <img src={logo} className="App-logo" alt="logo" /> {/* Add the logo below the table */}
    </div>
  );
}

export default App;