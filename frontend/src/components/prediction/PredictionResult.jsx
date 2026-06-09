import ChartCard from "../common/ChartCard";
import { formatPrice } from "../../utils/display";

function buildInterpretation(result, marketKpis) {
  if (!result) return "Soumettez un bien pour obtenir une estimation interpretable.";
  if (!marketKpis) return "La prediction est disponible. Les indicateurs de marche se chargent encore.";

  if (result.predicted_price > marketKpis.averagePrice * 1.15) {
    return "Ce bien parait au-dessus de la moyenne du marche pour le jeu de donnees actuel.";
  }
  if (result.predicted_price < marketKpis.averagePrice * 0.85) {
    return "Ce bien semble plus abordable que la moyenne du marche pour son profil.";
  }
  return "Ce bien semble dans la moyenne du marche au regard des donnees observees.";
}

export default function PredictionResult({ result, marketKpis }) {
  return (
    <ChartCard title="Resultat de prediction" subtitle="Sortie du modele, fourchette de prix et interpretation metier.">
      {result ? (
        <div className="result-stack">
          <div className="result-hero">
            <span>Prix estime</span>
            <strong>{formatPrice(result.predicted_price)}</strong>
          </div>
          <div className="result-grid">
            <div className="result-item">
              <span>Borne basse</span>
              <strong>{formatPrice(result.lower_bound)}</strong>
            </div>
            <div className="result-item">
              <span>Borne haute</span>
              <strong>{formatPrice(result.upper_bound)}</strong>
            </div>
            <div className="result-item">
              <span>Version du modele</span>
              <strong>{result.model_version}</strong>
            </div>
          </div>
          <p className="insight-copy">{buildInterpretation(result, marketKpis)}</p>
        </div>
      ) : (
        <p className="empty-copy">Le resultat apparaitra ici apres une prediction.</p>
      )}
    </ChartCard>
  );
}
