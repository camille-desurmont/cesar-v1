import { mountForm } from "./form_property_params";
import { mountMap } from "./map_france";
import { mountDisplay } from "./display_estimate";

function main(): void {
  const app = document.getElementById("app");
  if (!app) return;

  const formContainer = document.createElement("div");
  formContainer.id = "form-container";
  const mapContainer = document.createElement("div");
  mapContainer.id = "map-container";
  mapContainer.style.height = "400px";
  mapContainer.style.marginTop = "1rem";
  const displayContainer = document.createElement("div");
  displayContainer.id = "estimate-display";

  app.append(formContainer, mapContainer, displayContainer);

  mountForm(formContainer, (params) => {
    window.dispatchEvent(new CustomEvent("cesar-params-change", { detail: params }));
  });
  mountMap(mapContainer);
  mountDisplay(displayContainer);
}

main();
