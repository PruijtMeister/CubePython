/**
 * Type definitions for Cube data models
 */

export interface CubeSummary {
  shortId: string;
  name: string;
}

export interface Cube {
  shortId: string;
  name: string;
  owner: string | null;
  description: string | null;
  cardCount: number;
  categoryOverride: string | null;
  categoryPrefixes: string[];
  tags: string[];
  cards: number[];  // Array of card IDs
  isListed: boolean;
  isPrivate: boolean;
  dateUpdated: string | null;
}
