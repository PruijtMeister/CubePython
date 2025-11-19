import React, { useState, useEffect } from 'react';
import { Cube } from '../types/cube';
import { getCubeById } from '../services/api';
import './CubeDetail.css';

interface CubeDetailProps {
  cubeId: string;
  onBackToList: () => void;
}

const CubeDetail: React.FC<CubeDetailProps> = ({ cubeId, onBackToList }) => {
  const [cube, setCube] = useState<Cube | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCube = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getCubeById(cubeId);
        setCube(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load cube');
      } finally {
        setLoading(false);
      }
    };

    fetchCube();
  }, [cubeId]);

  if (loading) {
    return (
      <div className="cube-detail-container">
        <div className="breadcrumb">
          <button onClick={onBackToList} className="breadcrumb-link">
            All Cubes
          </button>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">Loading...</span>
        </div>
        <div className="cube-detail-loading">Loading cube details...</div>
      </div>
    );
  }

  if (error || !cube) {
    return (
      <div className="cube-detail-container">
        <div className="breadcrumb">
          <button onClick={onBackToList} className="breadcrumb-link">
            All Cubes
          </button>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">Error</span>
        </div>
        <div className="cube-detail-error">
          {error || 'Cube not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="cube-detail-container">
      <div className="breadcrumb">
        <button onClick={onBackToList} className="breadcrumb-link">
          All Cubes
        </button>
        <span className="breadcrumb-separator">/</span>
        <span className="breadcrumb-current">{cube.name}</span>
      </div>

      <div className="cube-detail-content">
        <div className="cube-detail-header">
          <h2>{cube.name}</h2>
          <div className="cube-id-badge">{cube.shortId}</div>
        </div>

        <div className="cube-detail-grid">
          <div className="cube-detail-section">
            <h3>Overview</h3>
            <div className="cube-detail-info">
              <div className="info-row">
                <span className="info-label">Owner:</span>
                <span className="info-value">{cube.owner || 'Unknown'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Card Count:</span>
                <span className="info-value">{cube.cardCount}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Category:</span>
                <span className="info-value">{cube.categoryOverride || 'N/A'}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Visibility:</span>
                <span className="info-value">
                  {cube.isPrivate ? 'Private' : 'Public'}
                  {cube.isListed && !cube.isPrivate && ' (Listed)'}
                </span>
              </div>
              {cube.dateUpdated && (
                <div className="info-row">
                  <span className="info-label">Last Updated:</span>
                  <span className="info-value">
                    {new Date(cube.dateUpdated).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>

          {cube.description && (
            <div className="cube-detail-section">
              <h3>Description</h3>
              <p className="cube-description">{cube.description}</p>
            </div>
          )}

          {cube.tags.length > 0 && (
            <div className="cube-detail-section">
              <h3>Tags</h3>
              <div className="cube-tags">
                {cube.tags.map((tag, index) => (
                  <span key={index} className="cube-tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {cube.categoryPrefixes.length > 0 && (
            <div className="cube-detail-section">
              <h3>Category Prefixes</h3>
              <div className="cube-tags">
                {cube.categoryPrefixes.map((prefix, index) => (
                  <span key={index} className="cube-tag category-prefix">
                    {prefix}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="cube-detail-section full-width">
            <h3>Cards ({cube.cards.length})</h3>
            {cube.cards.length > 0 ? (
              <div className="cube-cards-info">
                <p>This cube contains {cube.cards.length} cards.</p>
                {/* Card list can be expanded here in the future */}
              </div>
            ) : (
              <p className="no-cards">No cards in this cube.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CubeDetail;
