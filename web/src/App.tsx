import { useState } from "react";
import { DashboardScreen } from "./screens/DashboardScreen";
import { JobsScreen } from "./screens/JobsScreen";

export function App() {
  const [tab, setTab] = useState<"dashboard" | "jobs">("dashboard");

  return (
    <main className="container">
      <h1>job-2.0 Operator Console</h1>
      <nav>
        <button onClick={() => setTab("dashboard")}>Dashboard</button>
        <button onClick={() => setTab("jobs")}>Jobs</button>
      </nav>
      {tab === "dashboard" ? <DashboardScreen /> : <JobsScreen />}
    </main>
  );
}
