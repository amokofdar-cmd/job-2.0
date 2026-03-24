export type Job = {
  id: number;
  source: string;
  company: string;
  title: string;
  location: string;
  url: string;
  tier: string;
  score: number;
  applied: boolean;
};

export type Metrics = {
  total_jobs: number;
  applied_jobs: number;
  pending_jobs: number;
  attempts_total: number;
  success_rate: number;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/v1";

export async function getMetrics(): Promise<Metrics> {
  const res = await fetch(`${API_BASE}/dashboard/metrics`);
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function getJobs(): Promise<Job[]> {
  const res = await fetch(`${API_BASE}/jobs?limit=100`);
  if (!res.ok) throw new Error("Failed to fetch jobs");
  return res.json();
}

export async function triggerAutopilot(): Promise<{ applied_this_cycle: number }> {
  const res = await fetch(`${API_BASE}/autopilot/run-once`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger autopilot");
  return res.json();
}
