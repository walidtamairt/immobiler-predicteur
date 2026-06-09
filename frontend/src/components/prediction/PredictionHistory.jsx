import ChartCard from "../common/ChartCard";
import { formatHouseStyle, formatPrice, formatSurface } from "../../utils/display";

export default function PredictionHistory({ history }) {
  return (
    <ChartCard title="Historique des predictions" subtitle="Dernieres predictions utilisateur journalisees par l'API." wide>
      <div className="history-grid">
        {history.length ? history.map((item) => (
          <article key={item.id} className="history-card">
            <div className="history-card-top">
              <strong>{item.neighborhood}</strong>
              <span>{formatHouseStyle(item.house_style)}</span>
            </div>
            <div className="history-card-metrics">
              <p>Surface habitable : {formatSurface(item.gr_liv_area)}</p>
              <p>Prix estime : {formatPrice(item.predicted_price)}</p>
              <p>Version du modele : {item.model_version}</p>
            </div>
          </article>
        )) : (
          <p className="empty-copy">Aucune prediction recente disponible.</p>
        )}
      </div>
    </ChartCard>
  );
}
