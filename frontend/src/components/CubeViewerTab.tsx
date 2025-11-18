import React from 'react';
import CubeViewer from './CubeViewer';
import { CardData } from './Card';

const CubeViewerTab: React.FC = () => {
  // Example cards with various mana costs for testing
  const exampleCards: CardData[] = [
    {
      name: 'Lightning Bolt',
      manaCost: '{R}',
      type: 'Instant',
      text: 'Lightning Bolt deals 3 damage to any target.',
      imageUrl: 'https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg',
      set: 'M11',
      rarity: 'Common',
    },
    {
      name: 'Counterspell',
      manaCost: '{U}{U}',
      type: 'Instant',
      text: 'Counter target spell.',
      imageUrl: 'https://cards.scryfall.io/normal/front/4/f/4f616706-ec97-4923-bb1e-11a69fbaa1f8.jpg',
      set: 'MH2',
      rarity: 'Common',
    },
    {
      name: 'Birds of Paradise',
      manaCost: '{G}',
      type: 'Creature — Bird',
      text: 'Flying\n{T}: Add one mana of any color.',
      power: '0',
      toughness: '1',
      imageUrl: 'https://cards.scryfall.io/normal/front/f/e/feefe9f0-24a6-461c-9ef1-86c5a6f33b83.jpg',
      set: 'M11',
      rarity: 'Rare',
    },
    {
      name: 'Mox Diamond',
      manaCost: '{0}',
      type: 'Artifact',
      text: 'If Mox Diamond would enter the battlefield, you may discard a land card instead. If you do, put Mox Diamond onto the battlefield.\n{T}: Add one mana of any color.',
      imageUrl: 'https://cards.scryfall.io/normal/front/b/f/bf9fecfd-d122-422f-bd0a-5bf69b434dfe.jpg',
      set: 'STH',
      rarity: 'Rare',
    },
    {
      name: 'Sol Ring',
      manaCost: '{1}',
      type: 'Artifact',
      text: '{T}: Add {C}{C}.',
      imageUrl: 'https://cards.scryfall.io/normal/front/1/9/199cde21-5bc3-49cd-acd4-bae3af6e5881.jpg',
      set: 'C21',
      rarity: 'Uncommon',
    },
    {
      name: 'Thragtusk',
      manaCost: '{4}{G}',
      type: 'Creature — Beast',
      text: 'When Thragtusk enters the battlefield, you gain 5 life.\nWhen Thragtusk leaves the battlefield, create a 3/3 green Beast creature token.',
      power: '5',
      toughness: '3',
      imageUrl: 'https://cards.scryfall.io/normal/front/d/9/d9a8459b-4dea-4dc9-8b95-a3748472f699.jpg',
      set: 'M13',
      rarity: 'Rare',
    },
    {
      name: 'Wrath of God',
      manaCost: '{2}{W}{W}',
      type: 'Sorcery',
      text: 'Destroy all creatures. They can\'t be regenerated.',
      imageUrl: 'https://cards.scryfall.io/normal/front/6/6/664e6656-36a3-4635-9f33-9f8901afd397.jpg',
      set: 'M10',
      rarity: 'Rare',
    },
    {
      name: 'Mana Leak',
      manaCost: '{1}{U}',
      type: 'Instant',
      text: 'Counter target spell unless its controller pays {3}.',
      imageUrl: 'https://cards.scryfall.io/normal/front/2/4/247939d9-87e9-4f01-b223-fb4cfa7dbbe1.jpg',
      set: 'M12',
      rarity: 'Common',
    },
    {
      name: 'Dark Ritual',
      manaCost: '{B}',
      type: 'Instant',
      text: 'Add {B}{B}{B}.',
      imageUrl: 'https://cards.scryfall.io/normal/front/9/5/95f27eeb-6f14-4db3-adb9-9be5ed76b34b.jpg',
      set: 'A25',
      rarity: 'Common',
    },
    {
      name: 'Path to Exile',
      manaCost: '{W}',
      type: 'Instant',
      text: 'Exile target creature. Its controller may search their library for a basic land card, put that card onto the battlefield tapped, then shuffle.',
      imageUrl: 'https://cards.scryfall.io/normal/front/e/9/e9d36855-c38a-4bba-a642-cff3f81e057e.jpg',
      set: 'MH2',
      rarity: 'Uncommon',
    },
    {
      name: 'Brainstorm',
      manaCost: '{U}',
      type: 'Instant',
      text: 'Draw three cards, then put two cards from your hand on top of your library in any order.',
      imageUrl: 'https://cards.scryfall.io/normal/front/4/8/48070245-1370-4cf1-be15-d4e8a8b92ba8.jpg',
      set: 'STA',
      rarity: 'Uncommon',
    },
    {
      name: 'Jace, the Mind Sculptor',
      manaCost: '{2}{U}{U}',
      type: 'Legendary Planeswalker — Jace',
      text: '+2: Look at the top card of target player\'s library. You may put that card on the bottom of that player\'s library.\n0: Draw three cards, then put two cards from your hand on top of your library in any order.\n-1: Return target creature to its owner\'s hand.\n-12: Exile all cards from target player\'s library, then that player shuffles their hand into their library.',
      imageUrl: 'https://cards.scryfall.io/normal/front/c/8/c8817585-0d32-4d56-9142-0d29512e86a9.jpg',
      set: 'WWK',
      rarity: 'Mythic',
    },
    {
      name: 'Tarmogoyf',
      manaCost: '{1}{G}',
      type: 'Creature — Lhurgoyf',
      text: 'Tarmogoyf\'s power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.',
      power: '*',
      toughness: '*+1',
      imageUrl: 'https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg',
      set: 'MH2',
      rarity: 'Mythic',
    },
    {
      name: 'Primeval Titan',
      manaCost: '{4}{G}{G}',
      type: 'Creature — Giant',
      text: 'Trample\nWhenever Primeval Titan enters the battlefield or attacks, you may search your library for up to two land cards, put them onto the battlefield tapped, then shuffle.',
      power: '6',
      toughness: '6',
      imageUrl: 'https://cards.scryfall.io/normal/front/6/d/6d5537da-112e-4679-a113-b5d7ce32a66b.jpg',
      set: 'M11',
      rarity: 'Mythic',
    },
    {
      name: 'Delver of Secrets',
      manaCost: '{U}',
      type: 'Creature — Human Wizard',
      text: 'At the beginning of your upkeep, look at the top card of your library. You may reveal that card. If an instant or sorcery card is revealed this way, transform Delver of Secrets.',
      power: '1',
      toughness: '1',
      imageUrl: 'https://cards.scryfall.io/normal/front/a/b/abff6c81-65a4-48fa-ba8f-580f87b0344a.jpg',
      set: 'ISD',
      rarity: 'Common',
    },
  ];

  return (
    <div className="cube-viewer-tab">
      <CubeViewer cards={exampleCards} />
    </div>
  );
};

export default CubeViewerTab;
