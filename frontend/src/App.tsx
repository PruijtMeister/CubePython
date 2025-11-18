import React from 'react';
import './App.css';
import Tabs from './components/Tabs';
import CubeTab from './components/CubeTab';
import CardTab from './components/CardTab';
import CardPilesTab from './components/CardPilesTab';

function App() {
  const tabs = [
    {
      id: 'cube',
      label: 'Cube',
      content: <CubeTab />
    },
    {
      id: 'card',
      label: 'Card',
      content: <CardTab />
    },
    {
      id: 'piles',
      label: 'Card Piles',
      content: <CardPilesTab />
    }
  ];

  return (
    <div className="App">
      <header className="App-header">
        <h1>CubePython Tools</h1>
      </header>
      <Tabs tabs={tabs} />
    </div>
  );
}

export default App;
