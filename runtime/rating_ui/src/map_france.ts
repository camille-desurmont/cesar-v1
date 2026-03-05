import L from "leaflet";

// Ideas: add GeoJSON for departments and dispatch event on click with code_departement.

export function mountMap(container: HTMLElement): void {
  const map = L.map(container).setView([46.6, 2.4], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
  }).addTo(map);
}
