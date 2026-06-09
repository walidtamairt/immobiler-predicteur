import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "../common/ChartCard";
import { formatPrice, formatQuality } from "../../utils/display";

export default function PriceByQualityChart({ data }) {
  return (
    <ChartCard title="Prix moyen par qualite" subtitle="Visualisation de l'effet de la qualite globale sur le prix moyen.">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" strokeDasharray="3 3" />
          <XAxis dataKey="overall_qual" stroke="#94a3b8" tickFormatter={(value) => `${value}`} />
          <YAxis stroke="#94a3b8" tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
          <Tooltip
            formatter={(value) => [formatPrice(value), "Prix moyen"]}
            labelFormatter={(label) => formatQuality(label)}
          />
          <Bar dataKey="avg_price" fill="#a78bfa" radius={[10, 10, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
