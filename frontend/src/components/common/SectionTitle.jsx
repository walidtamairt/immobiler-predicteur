export default function SectionTitle({ eyebrow, title, subtitle, align = "left" }) {
  return (
    <header className={`section-title section-title-${align}`}>
      {eyebrow ? <p className="section-eyebrow">{eyebrow}</p> : null}
      <h3>{title}</h3>
      {subtitle ? <p>{subtitle}</p> : null}
    </header>
  );
}
