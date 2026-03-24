import { useEffect, useState } from "react";
import { getMetrics, triggerAutopilot, type Metrics } from "../api";
import { MetricCard } from "../components/MetricCard";

export function DashboardScreen() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [busy, setBusy] = useState(false);

  async function refresh() {
    setMetrics(await getMetrics());
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function runNow() {
    setBusy(true);
    try {
      await triggerAutopilot();
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="grid">
        <MetricCard title="Total Jobs" value={String(metrics?.total_jobs ?? "-")} />
        <MetricCard title="Applied" value={String(metrics?.applied_jobs ?? "-")} />
        <MetricCard title="Pending" value={String(metrics?.pending_jobs ?? "-")} />
        <MetricCard title="Attempts" value={String(metrics?.attempts_total ?? "-")} />
        <MetricCard title="Success Rate" value={`${((metrics?.success_rate ?? 0) * 100).toFixed(1)}%`} />
      </div>
      <button onClick={runNow} disabled={busy}>{busy ? "Running..." : "Run Autopilot Once"}</button>
    </div>
  );
}
