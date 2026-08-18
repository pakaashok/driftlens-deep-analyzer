const getApiUrl = (): string => {
  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;
    if (hostname === "localhost" ||
        hostname === "127.0.0.1") {
      return "http://localhost:8001";
    }
    return `http://${hostname}:8001`;
  }
  return "http://localhost:8001";
};

export interface ValueDiff {
  value_a: string;
  value_b: string;
  numeric_a: number;
  numeric_b: number;
  change_pct: number;
  direction: string;
}

export interface DeepAnalysis {
  environment_a: string;
  environment_b: string;
  total_keys_a: number;
  total_keys_b: number;
  noise_filtered: boolean;
  analysis: {
    jaccard: {
      score: number;
      similarity_percentage: number;
      key_drift_percentage: number;
      only_in_a: string[];
      only_in_b: string[];
      common_keys: string[];
    };
    cosine: {
      score: number;
      similarity_percentage: number;
      value_drift_percentage: number;
      value_differences: Record<string, ValueDiff>;
    };
    combined: {
      score: number;
      similarity_percentage: number;
      overall_drift_percentage: number;
      drift_level: string;
      recommendation: string;
    };
  };
}

export interface MatrixResult {
  environments: string[];
  matrix: Record<string, Record<string, {
    jaccard_score?: number;
    cosine_score?: number;
    combined_score: number;
    drift_level: string;
  }>>;
}

export interface DriftResults {
  environment_a: string;
  environment_b: string;
  timestamp: string;
  commit: string;
  triggered_by: string;
  commit_message: string;
  total_keys_a: number;
  total_keys_b: number;
  analysis: DeepAnalysis["analysis"];
  status?: string;
  message?: string;
}

export async function fetchEnvironments(): Promise<{
  environments: string[];
  count: number;
}> {
  const res = await fetch(
    `${getApiUrl()}/api/environments`
  );
  if (!res.ok) throw new Error(
    "Failed to fetch environments"
  );
  return res.json();
}

export async function analyzeEnvironments(
  envA: string,
  envB: string
): Promise<DeepAnalysis> {
  const res = await fetch(
    `${getApiUrl()}/api/analyze?env_a=${envA}&env_b=${envB}`
  );
  if (!res.ok) throw new Error("Analysis failed");
  return res.json();
}

export async function fetchMatrix(): Promise<MatrixResult> {
  const res = await fetch(
    `${getApiUrl()}/api/analyze/matrix`
  );
  if (!res.ok) throw new Error("Matrix failed");
  return res.json();
}

export async function fetchDriftResults(): Promise<DriftResults> {
  const res = await fetch(
    `${getApiUrl()}/api/drift-results?t=${Date.now()}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error(
    "Failed to fetch drift results"
  );
  return res.json();
}
