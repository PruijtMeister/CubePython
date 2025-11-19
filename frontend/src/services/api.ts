/**
 * API service for making requests to the backend
 */

import { CubeSummary, Cube } from '../types/cube';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * Fetch all cube summaries (id and name)
 */
export async function getAllCubes(): Promise<CubeSummary[]> {
  const response = await fetch(`${API_BASE_URL}/cubes/`);
  if (!response.ok) {
    throw new Error('Failed to fetch cubes');
  }
  return response.json();
}

/**
 * Fetch a single cube by ID
 */
export async function getCubeById(cubeId: string): Promise<Cube> {
  const response = await fetch(`${API_BASE_URL}/cubes/${cubeId}`);
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Cube with ID '${cubeId}' not found`);
    }
    throw new Error('Failed to fetch cube');
  }
  return response.json();
}

/**
 * Search for cubes by name
 */
export async function searchCubes(query: string, limit: number = 10): Promise<Cube[]> {
  const response = await fetch(`${API_BASE_URL}/cubes/search/${encodeURIComponent(query)}?limit=${limit}`);
  if (!response.ok) {
    throw new Error('Failed to search cubes');
  }
  return response.json();
}

/**
 * Get total cube count
 */
export async function getCubeCount(): Promise<number> {
  const response = await fetch(`${API_BASE_URL}/cubes/stats/count`);
  if (!response.ok) {
    throw new Error('Failed to fetch cube count');
  }
  const data = await response.json();
  return data.count;
}
