import ChartCard from "../common/ChartCard";
import KpiCard from "../common/KpiCard";

function formatDate(value) {
  if (!value) return "N/A";
  return new Date(value).toLocaleString("fr-FR");
}

export default function ModelHealthSection({ latest }) {
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
    </ChartCard>
  );
}
