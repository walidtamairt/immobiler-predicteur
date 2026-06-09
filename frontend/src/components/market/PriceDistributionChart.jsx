import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "../common/ChartCard";

export default function PriceDistributionChart({ data }) {
  return (
    <ChartCard title="Distribution des prix" subtitle="Histogramme du nombre de biens par tranche de prix.">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" strokeDasharray="3 3" />
          <XAxis dataKey="bucket" hide />
          <YAxis stroke="#94a3b8" />
          <Tooltip formatter={(value) => [value, "Nombre de biens"]} labelFormatter={(label) => `Tranche de prix : ${label} EUR`} />
          <Bar dataKey="count" fill="#7c3aed" radius={[10, 10, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
