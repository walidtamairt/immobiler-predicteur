export default function PageContainer({ title, subtitle, children }) {
  return (
    <section className="page-container">
      <header className="page-hero">
        <p className="eyebrow">Plateforme immobiliere</p>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </header>
      <div className="page-body">{children}</div>
    </section>
  );
}
