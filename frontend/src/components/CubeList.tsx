import React, { useState, useEffect } from 'react';
import { CubeSummary } from '../types/cube';
import { getAllCubes } from '../services/api';
import './CubeList.css';

interface CubeListProps {
  onCubeSelect: (cubeId: string) => void;
}

const CubeList: React.FC<CubeListProps> = ({ onCubeSelect }) => {
  const [cubes, setCubes] = useState<CubeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');

  const ITEMS_PER_PAGE = 20;

  useEffect(() => {
    const fetchCubes = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getAllCubes();
        setCubes(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cubes');
      } finally {
        setLoading(false);
      }
    };

    fetchCubes();
  }, []);

  // Filter cubes based on search query
  const filteredCubes = cubes.filter(cube =>
    cube.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cube.shortId.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Calculate pagination
  const totalPages = Math.ceil(filteredCubes.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const currentCubes = filteredCubes.slice(startIndex, endIndex);

  // Reset to page 1 when search query changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderPagination = () => {
    if (totalPages <= 1) return null;

    const pages: (number | string)[] = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show smart pagination with ellipsis
      pages.push(1);

      if (currentPage > 3) {
        pages.push('...');
      }

      for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
        if (i !== 1 && i !== totalPages) {
          pages.push(i);
        }
      }

      if (currentPage < totalPages - 2) {
        pages.push('...');
      }

      pages.push(totalPages);
    }

    return (
      <div className="pagination">
        <button
          className="pagination-button"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </button>

        {pages.map((page, index) => (
          typeof page === 'number' ? (
            <button
              key={index}
              className={`pagination-button ${currentPage === page ? 'active' : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </button>
          ) : (
            <span key={index} className="pagination-ellipsis">
              {page}
            </span>
          )
        ))}

        <button
          className="pagination-button"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </button>
      </div>
    );
  };

  if (loading) {
    return <div className="cube-list-loading">Loading cubes...</div>;
  }

  if (error) {
    return <div className="cube-list-error">Error: {error}</div>;
  }

  return (
    <div className="cube-list-container">
      <div className="cube-list-header">
        <h2>All Cubes</h2>
        <div className="cube-list-stats">
          {filteredCubes.length} {filteredCubes.length === 1 ? 'cube' : 'cubes'}
          {searchQuery && ` matching "${searchQuery}"`}
        </div>
      </div>

      <div className="cube-list-search">
        <input
          type="text"
          placeholder="Search cubes by name or ID..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="cube-list-grid">
        {currentCubes.map((cube) => (
          <div
            key={cube.shortId}
            className="cube-list-item"
            onClick={() => onCubeSelect(cube.shortId)}
          >
            <div className="cube-item-name">{cube.name}</div>
            <div className="cube-item-id">{cube.shortId}</div>
          </div>
        ))}
      </div>

      {currentCubes.length === 0 && (
        <div className="cube-list-empty">
          {searchQuery ? `No cubes found matching "${searchQuery}"` : 'No cubes available'}
        </div>
      )}

      {renderPagination()}

      <div className="cube-list-page-info">
        Page {currentPage} of {totalPages} •
        Showing {startIndex + 1}-{Math.min(endIndex, filteredCubes.length)} of {filteredCubes.length}
      </div>
    </div>
  );
};

export default CubeList;
