import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import ChartCard from "../common/ChartCard";
import KpiCard from "../common/KpiCard";

function formatDate(value) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("fr-FR");
}

export default function ModelHealthSection({ latest, history }) {
  return (
    <ChartCard
      title="Sante du modele"
      subtitle="Monitorage visuel des performances et du dernier entrainement."
      wide
    >
      <div className="kpi-row model-health-grid">
        <KpiCard label="Version" value={latest?.model_version || "N/A"} />
        <KpiCard label="MAE" value={latest?.mae?.toFixed?.(2) ?? "N/A"} />
        <KpiCard label="RMSE" value={latest?.rmse?.toFixed?.(2) ?? "N/A"} />
        <KpiCard label="R2" value={latest?.r2?.toFixed?.(3) ?? "N/A"} />
        <KpiCard label="Lignes train" value={latest?.train_rows ?? "N/A"} />
        <KpiCard label="Variables" value={latest?.feature_count ?? "N/A"} />
        <KpiCard label="Dernier entrainement" value={formatDate(latest?.created_at)} />
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart
          data={(history || []).map((item) => ({
            version: item.model_version,
            mae: item.mae,
            rmse: item.rmse,
            r2: item.r2,
          }))}
        >
          <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" strokeDasharray="3 3" />
          <XAxis dataKey="version" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip />
          <Line type="monotone" dataKey="mae" stroke="#8b5cf6" strokeWidth={2} />
          <Line type="monotone" dataKey="rmse" stroke="#60a5fa" strokeWidth={2} />
          <Line type="monotone" dataKey="r2" stroke="#c084fc" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
