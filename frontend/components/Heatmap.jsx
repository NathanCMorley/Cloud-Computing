/* HeatMap.jsx */
import React, { useEffect, useRef, useState } from 'react';
import './HeatMap.css';

import initSqlJs from 'sql.js';

const fetchNO2Data = async () => {
  // Initialize sql.js
  const SQL = await initSqlJs({
    locateFile: file => `https://sql.js.org/dist/${file}`
  });
  
  // Fetch the database file
  const response = await fetch('/tempo_no2.db');
  const buffer = await response.arrayBuffer();
  
  // Load the database
  const db = new SQL.Database(new Uint8Array(buffer));
  
  // Query the data
  const result = db.exec('SELECT latitude, longitude, value FROM no2_data');
  
  // Close the database
  db.close();
  
  // Transform to list of lists: [[lat, lon, intensity], ...]
  if (result.length === 0) {
    return [];
  }
  
  const rows = result[0].values;

  return rows;
};

// Usage:
// const data = await fetchNO2Data();
// data will be: [[lat1, lon1, intensity1], [lat2, lon2, intensity2], ...]

export default function HeatMap({ mapChoice }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [intensity, setIntensity] = useState(0.5);

  useEffect(() => {
    // Prevent double initialization
    if (mapInstanceRef.current) return;

    // Load Leaflet CSS
    if (!document.querySelector('link[href*="leaflet.css"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css';
      document.head.appendChild(link);
    }

    // Load Leaflet JS
    const loadLeaflet = () => {
      if (window.L && window.L.heatLayer) {
        initMap();
        return;
      }

      if (!document.querySelector('script[src*="leaflet.js"]')) {
        const script1 = document.createElement('script');
        script1.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js';
        script1.onload = () => {
          const script2 = document.createElement('script');
          script2.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet.heat/0.2.0/leaflet-heat.js';
          script2.onload = initMap;
          document.body.appendChild(script2);
        };
        document.body.appendChild(script1);
      }
    };

function initMap() {
  if (!mapRef.current || mapInstanceRef.current) return;

  setTimeout(async () => {  // Make this async
    if (!mapRef.current) return;

    const L = window.L;
    
    const newMap = L.map(mapRef.current).setView([37.7749, -122.4194], 12);
    newMap.setMaxZoom(100);
    newMap.setMinZoom(3);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(newMap);

    setTimeout(() => {
      newMap.invalidateSize();
    }, 100);

    // Fetch the data from SQLite
    const hotspots = await fetchNO2Data();  // This replaces your hardcoded hotspots

    // Add heat layer after map is fully initialized
    setTimeout(() => {
      const heat = L.heatLayer(hotspots, {
        radius: 5,
        blur: 0,

        minOpacity:1,
        gradient: {
          0.0: 'rgba(0, 0, 0, 0)',        // Transparent
          0.1: 'rgba(0, 0, 255, 0.4)',    // Light blue
          0.2: 'rgba(0, 100, 255, 0.6)',  // Blue
          0.3: 'rgba(0, 150, 255, 0.7)',  // Bright blue
          0.4: 'rgba(0, 200, 200, 0.75)', // Cyan
          0.5: 'rgba(0, 255, 100, 0.8)',  // Lime
          0.6: 'rgba(100, 255, 0, 0.85)', // Yellow-green
          0.7: 'rgba(200, 255, 0, 0.9)',  // Yellow
          0.8: 'rgba(255, 200, 0, 0.9)',  // Orange-yellow
          0.9: 'rgba(255, 100, 0, 0.95)', // Orange
          1.0: 'rgba(255, 0, 0, 1)'       // Red
        }
      }).addTo(newMap);


      newMap.heatLayer = heat;
      newMap.heatData = hotspots;  // Store the fetched data
    }, 200);

    mapInstanceRef.current = newMap;
  }, 150);
      
    }

    loadLeaflet();

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <h1>Interactive Heat Map {mapChoice}</h1>
      </div>
      <div ref={mapRef} className="page-content" />
    </div>
  );
}
