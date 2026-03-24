import type { PropsWithChildren } from "react";

export function MetricCard({ children, title, value }: PropsWithChildren<{ title: string; value: string }>) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p className="metric">{value}</p>
      {children}
    </div>
  );
}
