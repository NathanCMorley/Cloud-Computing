// Home.jsx
import React from 'react';
import HeatMap from '../components/Heatmap.jsx'
import '../styles/Map.css';

export default function Home() {
    var mapChoice;
  return (
    <div className="map-container">
        <div className="buttonContainer">
            <button className="N02" onClick={mapchoice = "NO2"}></button>
            <button className="Formaldehyde" onClick={mapchoice = "Formaldehyde"}></button>
            <button className="Aerosol Index" onClick={mapchoice = "Aerosol_Index"}></button>
            <button className='Particulate Matter' onClick={mapchoice = "Particulate_Matter"}></button>
        </div>
        
      <HeatMap mapChoice={mapChoice}/>
    </div>
  );
}
