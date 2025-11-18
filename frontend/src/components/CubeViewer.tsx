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

  // Placeholder recommendations data
  const placeholderRecommendations = [
    'Recommendation 1',
    'Recommendation 2',
    'Recommendation 3',
    'Recommendation 4',
    'Recommendation 5',
    'Recommendation 6',
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
        <p className="instruction-text">Drag and drop cards to reorganize them between piles</p>
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
              {placeholderRecommendations.map((rec, index) => (
                <div key={index} className="recommendation-card">
                  {rec}
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
