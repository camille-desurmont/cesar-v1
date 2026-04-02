import type { EstimateParams } from "./api_client";

const TYPE_OPTIONS = [
  "Appartement",
  "Maison",
  "Dépendance",
  "Local industriel. commercial ou assimilé",
] as const;

export type ParamsChangeCallback = (params: EstimateParams) => void;

export function mountForm(container: HTMLElement, onParamsChange: ParamsChangeCallback): void {
  const form = document.createElement("form");
  form.innerHTML = `
    <label>Surface (m²) <input type="number" name="surface" min="1" step="0.1" value="50" /></label>
    <label>Rooms <input type="number" name="pieces" min="0" step="1" value="3" /></label>
    <label>Department <input type="text" name="departement" maxlength="3" value="75" /></label>
    <label>Type <select name="type_local"></select></label>
    <button type="submit">Estimate</button>
  `;
  const select = form.querySelector<HTMLSelectElement>("select[name='type_local']");
  if (select) {
    TYPE_OPTIONS.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      select.appendChild(opt);
    });
  }
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const params: EstimateParams = {
      surface_reelle_bati: Number((fd.get("surface") as string) || 50),
      nombre_pieces_principales: Number((fd.get("pieces") as string) || 3),
      code_departement: String(fd.get("departement") || "75").trim().slice(0, 3),
      type_local: String(fd.get("type_local") || TYPE_OPTIONS[0]),
    };
    onParamsChange(params);
  });
  container.appendChild(form);
}
