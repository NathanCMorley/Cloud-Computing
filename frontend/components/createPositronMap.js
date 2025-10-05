import L from "leaflet";
import "leaflet/dist/leaflet.css";

/**
 * Initializes a Leaflet map with Carto Positron tiles
 * @param {HTMLElement} container - The div element for the map
 * @param {Array<number>} center - [lat, lon] for map center
 * @param {number} zoom - initial zoom level
 * @returns {L.Map} - Leaflet map instance
 */
export function createPositronMap(container, center = [0, 0], zoom = 0) {
  if (!container) {
    console.error("Invalid container element for map");
    return null;
  }

  const map = L.map(container, {
    minZoom: 0,
    maxZoom: 0,
  });

  const cartodbAttribution =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ' +
    '&copy; <a href="https://carto.com/attribution">CARTO</a>';

  L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", {
    attribution: cartodbAttribution,
  }).addTo(map);

  map.setView(center, zoom);

  return map;
}
