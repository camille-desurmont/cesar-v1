const DEFAULT_BASE = "/api";

export interface EstimateParams {
  surface_reelle_bati: number;
  nombre_pieces_principales: number;
  code_departement: string;
  type_local: string;
}

export interface EstimateResult {
  estimated_value_eur: number;
  value_low_eur?: number;
  value_high_eur?: number;
}

export async function fetchEstimate(
  baseUrl: string,
  params: EstimateParams
): Promise<EstimateResult> {
  const url = `${baseUrl.replace(/\/$/, "")}/estimate/`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<EstimateResult>;
}

export function getApiBase(): string {
  return (window as unknown as { CESAR_API_BASE?: string }).CESAR_API_BASE ?? DEFAULT_BASE;
}
