/* HeatMap.jsx */
import React, { useEffect, useRef, useState } from 'react';
import './HeatMap.css';

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

      // Wait for container to have proper dimensions
      setTimeout(() => {
        if (!mapRef.current) return;

        const L = window.L;
        
        // Force invalidate size after a moment
        const newMap = L.map(mapRef.current).setView([37.7749, -122.4194], 12);
        newMap.setMaxZoom(100);
        newMap.setMinZoom(3);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(newMap);

        // Force map to recognize its size
        setTimeout(() => {
          newMap.invalidateSize();
        }, 100);

        // Generate sample heat data points (lat, lng, intensity)
        const heatData = [];
        for (let i = 0; i < 200; i++) {
          const lat = 37.7749 + (Math.random() - 0.5) * 0.1;
          const lng = -122.4194 + (Math.random() - 0.5) * 0.1;
          const intensity = Math.random();
          heatData.push([lat, lng, intensity]);
        }

        // Add some hotspots
        const hotspots = [
          [37.7849, -122.4094],
          [37.7649, -122.4294],
          [37.7749, -122.4394]
        ];

        hotspots.forEach(spot => {
          for (let i = 0; i < 30; i++) {
            const lat = spot[0] + (Math.random() - 0.5) * 0.01;
            const lng = spot[1] + (Math.random() - 0.5) * 0.01;
            heatData.push([lat, lng, 0.8 + Math.random() * 0.2]);
          }
        });

        // Add heat layer after map is fully initialized
        setTimeout(() => {
          const heat = L.heatLayer(heatData, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
            max: 1.0,
            gradient: {
              0.0: 'blue',
              0.5: 'lime',
              0.7: 'yellow',
              1.0: 'red'
            }
          }).addTo(newMap);

          newMap.heatLayer = heat;
          newMap.heatData = heatData;
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

  useEffect(() => {
    const map = mapInstanceRef.current;
    if (map && map.heatLayer && map.heatData) {
      map.heatLayer.setOptions({
        radius: 25,
        blur: 15,
        maxZoom: 17,
        max: intensity,
        gradient: {
          0.0: 'blue',
          0.5: 'lime',
          0.7: 'yellow',
          1.0: 'red'
        }
      });
    }
  }, [intensity]);

  return (
    <div className="heatmap-container">
      <div className="heatmap-header">
        <h1>Interactive Heat Map</h1>
        <div className="controls">
          <label htmlFor="intensity-slider">Heat Intensity:</label>
          <input
            id="intensity-slider"
            type="range"
            min="0.1"
            max="2"
            step="0.1"
            value={intensity}
            onChange={(e) => setIntensity(parseFloat(e.target.value))}
          />
          <span className="intensity-value">{intensity.toFixed(1)}</span>
        </div>
      </div>
      <div ref={mapRef} className="page-content" />
    </div>
  );
}
