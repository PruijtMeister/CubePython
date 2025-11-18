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
      {card.imageUrl && (
        <div className="card-image">
          <img src={card.imageUrl} alt={card.name} />
        </div>
      )}
    </div>
  );
};

export default Card;
