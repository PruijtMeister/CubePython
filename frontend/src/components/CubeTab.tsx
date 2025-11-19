import React, { useState } from 'react';
import CubeList from './CubeList';
import CubeDetail from './CubeDetail';
import './CubeTab.css';

type ViewMode = 'list' | 'detail';

const CubeTab: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedCubeId, setSelectedCubeId] = useState<string | null>(null);

  const handleCubeSelect = (cubeId: string) => {
    setSelectedCubeId(cubeId);
    setViewMode('detail');
  };

  const handleBackToList = () => {
    setViewMode('list');
    setSelectedCubeId(null);
  };

  return (
    <div className="cube-tab">
      {viewMode === 'list' ? (
        <CubeList onCubeSelect={handleCubeSelect} />
      ) : (
        selectedCubeId && (
          <CubeDetail cubeId={selectedCubeId} onBackToList={handleBackToList} />
        )
      )}
    </div>
  );
};

export default CubeTab;
