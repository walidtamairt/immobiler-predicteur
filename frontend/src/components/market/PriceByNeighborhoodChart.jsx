import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "../common/ChartCard";
import { formatPrice } from "../../utils/display";

export default function PriceByNeighborhoodChart({ data, wide = false }) {
  return (
    <ChartCard title="Prix moyen par quartier" subtitle="Classement des quartiers les plus chers selon le filtre courant." wide={wide}>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" strokeDasharray="3 3" />
          <XAxis type="number" stroke="#94a3b8" tickFormatter={(value) => `${Math.round(value / 1000)}k`} />
          <YAxis type="category" dataKey="neighborhood" width={90} stroke="#94a3b8" />
          <Tooltip formatter={(value) => [formatPrice(value), "Prix moyen"]} />
          <Bar dataKey="avg_price" fill="#8b5cf6" radius={[0, 10, 10, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
