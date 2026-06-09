import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "../common/ChartCard";
import { formatMonth, formatPrice } from "../../utils/display";

export default function SeasonalityChart({ data, wide = false }) {
  return (
    <ChartCard title="Saisonnalite des prix" subtitle="Evolution du prix moyen par mois de vente." wide={wide}>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" strokeDasharray="3 3" />
          <XAxis dataKey="sale_month" stroke="#94a3b8" tickFormatter={(value) => formatMonth(value)} />
          <YAxis stroke="#94a3b8" tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
          <Tooltip
            formatter={(value) => [formatPrice(value), "Prix moyen"]}
            labelFormatter={(label) => `Mois de vente : ${formatMonth(label)}`}
          />
          <Line type="monotone" dataKey="avg_price" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
