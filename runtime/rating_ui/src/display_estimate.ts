import { fetchEstimate, getApiBase } from "./api_client";
import type { EstimateParams } from "./api_client";

function renderResult(container: HTMLElement, value: number, low?: number, high?: number): void {
  let html = `<p><strong>Estimated value:</strong> ${Math.round(value).toLocaleString("en-GB")} €</p>`;
  if (low != null && high != null) {
    html += `<p>Range: ${Math.round(low).toLocaleString("en-GB")} – ${Math.round(high).toLocaleString("en-GB")} €</p>`;
  }
  container.innerHTML = html;
}

function renderError(container: HTMLElement, message: string): void {
  container.innerHTML = `<p style="color:red">Error: ${message}</p>`;
}

function renderLoading(container: HTMLElement): void {
  container.innerHTML = "<p>Loading…</p>";
}

export function mountDisplay(container: HTMLElement): void {
  window.addEventListener("cesar-params-change", async (e: Event) => {
    const params = (e as CustomEvent<EstimateParams>).detail;
    renderLoading(container);
    try {
      const base = getApiBase();
      const result = await fetchEstimate(base, params);
      renderResult(
        container,
        result.estimated_value_eur,
        result.value_low_eur,
        result.value_high_eur
      );
    } catch (err) {
      renderError(container, err instanceof Error ? err.message : String(err));
    }
  });
}
