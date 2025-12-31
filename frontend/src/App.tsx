import { useEffect, useState } from "react";

type Metric = { label: string; value: string };

function StatCard({ title, value }: { title: string; value: string }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-value">{value}</div>
    </div>
  );
}

export function App() {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [instances, setInstances] = useState<string[]>([]);

  useEffect(() => {
    fetch("/api/status", { headers: { Authorization: "Bearer owner-token" } })
      .then((res) => res.json())
      .then((data) => {
        setMetrics([
          { label: "Players", value: String(data.players ?? 0) },
          { label: "TPS", value: String(data.tps ?? 0) },
          { label: "MSPT", value: String(data.mspt ?? 0) },
          { label: "CPU", value: `${data.cpu_usage ?? 0}%` },
          { label: "Memory", value: `${data.memory_usage ?? 0}%` },
          { label: "Disk", value: `${data.disk_usage ?? 0}%` },
        ]);
      })
      .catch(() => {});
    fetch("/api/instances", { headers: { Authorization: "Bearer owner-token" } })
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data.instances)) {
          setInstances(data.instances.map((item: any) => item.name || item.path));
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="page">
      <header className="header">
        <h1>MC Panel</h1>
        <div className="actions">
          <button className="btn">Dark / Light</button>
          <button className="btn">中文 / EN</button>
        </div>
      </header>
      <section className="section">
        <h2>Dashboard</h2>
        <div className="grid">
          {metrics.map((m) => (
            <StatCard key={m.label} title={m.label} value={m.value} />
          ))}
        </div>
      </section>
      <section className="section">
        <h2>Instances</h2>
        <ul>
          {instances.map((name) => (
            <li key={name}>{name}</li>
          ))}
        </ul>
      </section>
      <section className="section">
        <h2>Logs</h2>
        <div className="console">Connect to /api/logs/ws with token in query</div>
      </section>
    </div>
  );
}
