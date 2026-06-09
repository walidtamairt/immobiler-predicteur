export default function ChartCard({ title, subtitle, children, wide = false }) {
  return (
    <article className={`chart-card${wide ? " chart-wide" : ""}`}>
      <div className="card-header">
        <h3>{title}</h3>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      <div className="card-content">{children}</div>
    </article>
  );
}
