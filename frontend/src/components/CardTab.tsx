import React, { useState } from 'react';
import Card, { CardData } from './Card';
import './CardTab.css';

const CardTab: React.FC = () => {
  const [cardInput, setCardInput] = useState('');
  const [currentCard, setCurrentCard] = useState<CardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cardInput.trim()) {
      setError('Please enter a card name or identifier');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Call the backend API to fetch card data
      const response = await fetch(`http://localhost:8000/api/cards/${encodeURIComponent(cardInput)}`);

      if (!response.ok) {
        throw new Error('Card not found');
      }

      const data = await response.json();

      // Map the backend response to CardData
      const cardData: CardData = {
        name: data.name,
        manaCost: data.mana_cost,
        type: data.type_line,
        text: data.oracle_text,
        power: data.power,
        toughness: data.toughness,
        imageUrl: data.image_uris?.normal || data.image_uris?.small,
        set: data.set_name,
        rarity: data.rarity,
      };

      setCurrentCard(cardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch card');
      setCurrentCard(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card-tab">
      <div className="card-search-form">
        <h2>Search for a Card</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              value={cardInput}
              onChange={(e) => setCardInput(e.target.value)}
              placeholder="Enter card name or ID..."
              className="card-input"
            />
            <button type="submit" className="submit-button" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {error && <div className="error-message">{error}</div>}
      </div>

      {currentCard && (
        <div className="card-display">
          <Card card={currentCard} />
        </div>
      )}
    </div>
  );
};

export default CardTab;
