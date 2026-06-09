import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import ChartCard from "../common/ChartCard";
import { formatPrice, formatSurface } from "../../utils/display";

export default function PriceVsSurfaceChart({ data }) {
  return (
    <ChartCard title="Prix vs surface habitable" subtitle="Comparaison entre la surface habitable et le prix de vente.">
      <ResponsiveContainer width="100%" height={320}>
        <ScatterChart>
          <CartesianGrid stroke="rgba(148, 163, 184, 0.14)" />
          <XAxis
            type="number"
            dataKey="gr_liv_area"
            name="Surface habitable"
            stroke="#94a3b8"
            tickFormatter={(value) => `${Math.round(value)}`}
          />
          <YAxis
            type="number"
            dataKey="sale_price"
            name="Prix"
            stroke="#94a3b8"
            tickFormatter={(value) => `${Math.round(value / 1000)}k`}
          />
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            formatter={(value, name) => [
              name === "sale_price" ? formatPrice(value) : formatSurface(value),
              name === "sale_price" ? "Prix de vente" : "Surface habitable",
            ]}
          />
          <Scatter data={data} fill="#60a5fa" />
        </ScatterChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
