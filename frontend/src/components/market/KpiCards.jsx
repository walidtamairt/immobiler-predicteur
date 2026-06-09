import KpiCard from "../common/KpiCard";
import { formatPrice, formatSurface } from "../../utils/display";

export default function KpiCards({ kpis }) {
  return (
    <div className="kpi-row">
      <KpiCard label="Nombre de biens" value={kpis ? kpis.totalProperties : 0} />
      <KpiCard label="Prix moyen" value={formatPrice(kpis?.averagePrice)} />
      <KpiCard label="Prix median" value={formatPrice(kpis?.medianPrice)} />
      <KpiCard label="Surface moyenne" value={formatSurface(kpis?.averageSurface)} />
      <KpiCard label="Prix moyen au pied carre" value={formatPrice(kpis?.averagePricePerM2)} />
    </div>
  );
}
