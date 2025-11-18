import React from 'react';
import './Card.css';

export interface CardData {
  name: string;
  manaCost?: string;
  type?: string;
  text?: string;
  power?: string;
  toughness?: string;
  imageUrl?: string;
  set?: string;
  rarity?: string;
}

interface CardProps {
  card: CardData;
}

const Card: React.FC<CardProps> = ({ card }) => {
  return (
    <div className="magic-card">
      <div className="card-header">
        <h3 className="card-name">{card.name}</h3>
        {card.manaCost && <span className="mana-cost">{card.manaCost}</span>}
      </div>

      {card.imageUrl && (
        <div className="card-image">
          <img src={card.imageUrl} alt={card.name} />
        </div>
      )}

      <div className="card-details">
        {card.type && (
          <div className="card-type">
            <strong>Type:</strong> {card.type}
          </div>
        )}

        {card.text && (
          <div className="card-text">
            <p>{card.text}</p>
          </div>
        )}

        {(card.power || card.toughness) && (
          <div className="card-stats">
            <strong>P/T:</strong> {card.power}/{card.toughness}
          </div>
        )}

        <div className="card-footer">
          {card.set && <span className="card-set">{card.set}</span>}
          {card.rarity && <span className="card-rarity">{card.rarity}</span>}
        </div>
      </div>
    </div>
  );
};

export default Card;
