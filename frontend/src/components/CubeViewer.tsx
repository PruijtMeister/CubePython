import React, { useState, useEffect } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
} from '@dnd-kit/core';
import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
  arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import Card, { CardData } from './Card';
import './CubeViewer.css';

interface CubeViewerProps {
  cards: CardData[];
}

interface Pile {
  id: string;
  label: string;
  cards: CardData[];
}

// Helper function to extract mana cost value for sorting
const getManaCostValue = (manaCost?: string): number => {
  if (!manaCost) return 0;

  // Extract numbers from mana cost string like "{2}{U}{U}"
  const matches = manaCost.match(/\d+/);
  const genericCost = matches ? parseInt(matches[0]) : 0;

  // Count colored mana symbols
  const coloredSymbols = (manaCost.match(/\{[WUBRG]\}/g) || []).length;

  return genericCost + coloredSymbols;
};

// Sortable card component for drag and drop
interface SortableCardProps {
  card: CardData;
  id: string;
  index: number;
}

const SortableCard: React.FC<SortableCardProps> = ({ card, id, index }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 1000 : index,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="sortable-card"
    >
      <Card card={card} />
    </div>
  );
};

// Droppable pile container component
interface DroppablePileProps {
  pileId: string;
  cards: CardData[];
  getCardId: (card: CardData) => string;
}

const DroppablePile: React.FC<DroppablePileProps> = ({ pileId, cards, getCardId }) => {
  const { setNodeRef, isOver } = useDroppable({
    id: pileId,
  });

  return (
    <SortableContext
      items={cards.map(getCardId)}
      strategy={verticalListSortingStrategy}
    >
      <div
        ref={setNodeRef}
        className={`pile-content ${isOver ? 'pile-over' : ''}`}
      >
        {cards.map((card, index) => (
          <SortableCard
            key={getCardId(card)}
            id={getCardId(card)}
            card={card}
            index={index}
          />
        ))}
        {cards.length === 0 && (
          <div className="empty-pile">Drop cards here</div>
        )}
      </div>
    </SortableContext>
  );
};

const CubeViewer: React.FC<CubeViewerProps> = ({ cards }) => {
  const [piles, setPiles] = useState<Pile[]>([]);
  const [activeCard, setActiveCard] = useState<CardData | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  // Initialize piles based on mana cost
  useEffect(() => {
    // Create map to organize cards by mana cost
    const pileMap = new Map<number, CardData[]>();

    cards.forEach((card) => {
      const manaCost = getManaCostValue(card.manaCost);
      // Cards with mana cost 7+ go into pile 7
      const pileCost = manaCost >= 7 ? 7 : manaCost;

      if (!pileMap.has(pileCost)) {
        pileMap.set(pileCost, []);
      }
      pileMap.get(pileCost)!.push(card);
    });

    // Always create exactly 8 piles (0-6 and 7+)
    const sortedPiles: Pile[] = [];
    for (let cost = 0; cost <= 7; cost++) {
      sortedPiles.push({
        id: `pile-${cost}`,
        label: cost === 0 ? '0 Mana' : cost === 7 ? '7+ Mana' : `${cost} Mana`,
        cards: pileMap.get(cost) || [],
      });
    }

    setPiles(sortedPiles);
  }, [cards]);

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const card = findCardById(active.id as string);
    setActiveCard(card);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) {
      setActiveCard(null);
      return;
    }

    const activeId = active.id as string;
    const overId = over.id as string;

    // Find source pile and card index
    let sourcePileIndex = -1;
    let activeCardIndex = -1;

    piles.forEach((pile, pileIdx) => {
      const idx = pile.cards.findIndex((c) => getCardId(c) === activeId);
      if (idx !== -1) {
        sourcePileIndex = pileIdx;
        activeCardIndex = idx;
      }
    });

    if (sourcePileIndex === -1) {
      setActiveCard(null);
      return;
    }

    // Determine destination pile and position
    let destPileIndex = -1;
    let overCardIndex = -1;

    if (overId.startsWith('pile-')) {
      // Dropped on pile container (empty area)
      destPileIndex = piles.findIndex((p) => p.id === overId);
      overCardIndex = -1; // Will add to end
    } else {
      // Dropped on a card
      piles.forEach((pile, pileIdx) => {
        const idx = pile.cards.findIndex((c) => getCardId(c) === overId);
        if (idx !== -1) {
          destPileIndex = pileIdx;
          overCardIndex = idx;
        }
      });
    }

    if (destPileIndex === -1) {
      setActiveCard(null);
      return;
    }

    const newPiles = [...piles];

    if (sourcePileIndex === destPileIndex) {
      // Moving within the same pile - use arrayMove
      if (overCardIndex !== -1) {
        newPiles[sourcePileIndex].cards = arrayMove(
          newPiles[sourcePileIndex].cards,
          activeCardIndex,
          overCardIndex
        );
      }
    } else {
      // Moving between different piles
      const [movedCard] = newPiles[sourcePileIndex].cards.splice(activeCardIndex, 1);

      if (overCardIndex === -1) {
        // Dropped on empty area - add to end
        newPiles[destPileIndex].cards.push(movedCard);
      } else {
        // Dropped on a card - insert before it
        newPiles[destPileIndex].cards.splice(overCardIndex, 0, movedCard);
      }
    }

    setPiles(newPiles);
    setActiveCard(null);
  };

  const findCardById = (id: string): CardData | null => {
    for (const pile of piles) {
      const card = pile.cards.find((c) => getCardId(c) === id);
      if (card) return card;
    }
    return null;
  };

  const getCardId = (card: CardData): string => {
    return `${card.name}-${card.manaCost || 'no-cost'}`;
  };

  // Placeholder recommendations data with actual card objects
  const placeholderRecommendations: CardData[] = [
    {
      name: 'Swords to Plowshares',
      manaCost: '{W}',
      type: 'Instant',
      text: 'Exile target creature. Its controller gains life equal to its power.',
      imageUrl: 'https://cards.scryfall.io/normal/front/8/0/80f46b80-0728-49bf-9d54-801eaa10b9b2.jpg',
      set: '2X2',
      rarity: 'Uncommon',
    },
    {
      name: 'Mana Drain',
      manaCost: '{U}{U}',
      type: 'Instant',
      text: 'Counter target spell. At the beginning of your next main phase, add an amount of {C} equal to that spell\'s mana value.',
      imageUrl: 'https://cards.scryfall.io/normal/front/3/c/3c429c40-2389-41e5-8681-4bb274e25eba.jpg',
      set: 'IMA',
      rarity: 'Mythic',
    },
    {
      name: 'Ragavan, Nimble Pilferer',
      manaCost: '{R}',
      type: 'Legendary Creature — Monkey Pirate',
      text: 'Whenever Ragavan, Nimble Pilferer deals combat damage to a player, create a Treasure token and exile the top card of that player\'s library. Until end of turn, you may cast that card.',
      power: '2',
      toughness: '1',
      imageUrl: 'https://cards.scryfall.io/normal/front/a/9/a9738cda-adb1-47fb-9f4c-ecd930228c4d.jpg',
      set: 'MH2',
      rarity: 'Mythic',
    },
    {
      name: 'Oko, Thief of Crowns',
      manaCost: '{1}{G}{U}',
      type: 'Legendary Planeswalker — Oko',
      text: '+2: Create a Food token.\n+1: Target artifact or creature loses all abilities and becomes a green Elk creature with base power and toughness 3/3.\n-5: Exchange control of target artifact or creature you control and target creature an opponent controls with power 3 or less.',
      imageUrl: 'https://cards.scryfall.io/normal/front/3/4/3462a3d0-5552-49fa-9eb7-100960c55891.jpg',
      set: 'ELD',
      rarity: 'Mythic',
    },
    {
      name: 'Sheoldred, the Apocalypse',
      manaCost: '{2}{B}{B}',
      type: 'Legendary Creature — Phyrexian Praetor',
      text: 'Deathtouch\nWhenever you draw a card, you gain 2 life.\nWhenever an opponent draws a card, they lose 2 life.',
      power: '4',
      toughness: '5',
      imageUrl: 'https://cards.scryfall.io/normal/front/d/6/d67be074-cdd4-41d9-ac89-0a0456c4e4b2.jpg',
      set: 'DMU',
      rarity: 'Mythic',
    },
    {
      name: 'The One Ring',
      manaCost: '{4}',
      type: 'Legendary Artifact',
      text: 'When The One Ring enters the battlefield, if you cast it, you gain protection from everything until your next turn.\nAt the beginning of your upkeep, you lose 1 life for each burden counter on The One Ring.\n{T}: Put a burden counter on The One Ring, then draw a card for each burden counter on The One Ring.',
      imageUrl: 'https://cards.scryfall.io/normal/front/d/5/d5806e68-1054-458e-866d-1f2470f682b2.jpg',
      set: 'LTR',
      rarity: 'Mythic',
    },
  ];

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="cube-viewer-container">
        <h2>Cube Viewer</h2>
        <div className="cube-viewer-main">
          <div className="cube-viewer-piles">
            <div className="piles-grid">
              {piles.map((pile) => (
                <div key={pile.id} className="pile" data-pile-id={pile.id}>
                  <h3 className="pile-header">{pile.label}</h3>
                  <div className="pile-count">{pile.cards.length} cards</div>
                  <DroppablePile
                    pileId={pile.id}
                    cards={pile.cards}
                    getCardId={getCardId}
                  />
                </div>
              ))}
            </div>
          </div>
          <div className="cube-viewer-recommendations">
            <h3>Recommendations</h3>
            <div className="recommendations-grid">
              {placeholderRecommendations.map((card, index) => (
                <div key={index} className="recommendation-card">
                  <Card card={card} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <DragOverlay>
        {activeCard ? (
          <div className="drag-overlay">
            <Card card={activeCard} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
};

export default CubeViewer;
