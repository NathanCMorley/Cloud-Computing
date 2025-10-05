// Home.jsx
import React, { useState } from 'react';
import HeatMap from '../components/Heatmap.jsx';
import '../styles/Map.css';

export default function Home() {
  const [mapChoice, setMapChoice] = useState("NO2");

  return (
    <div className="page-content">
      <div className="button-container">
        <button className="NO2" onClick={() => setMapChoice("NO2")}>NO₂</button>
        <button className="Formaldehyde" onClick={() => setMapChoice("Formaldehyde")}>Formaldehyde</button>
        <button className="AerosolIndex" onClick={() => setMapChoice("Aerosol_Index")}>Aerosol Index</button>
        <button className="ParticulateMatter" onClick={() => setMapChoice("Particulate_Matter")}>Particulate Matter</button>
        <button className="ParticulateMatter" onClick={() => setMapChoice("Ozone")}>Ozone</button>

      </div>
      <div className='map-container'>
        <HeatMap mapChoice={mapChoice} />
      </div>
    </div>
  );
}