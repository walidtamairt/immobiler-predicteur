import { useEffect, useState } from "react";
import PageContainer from "../components/layout/PageContainer";
import PredictionForm from "../components/prediction/PredictionForm";
import PredictionHistory from "../components/prediction/PredictionHistory";
import ModelHealthSection from "../components/prediction/ModelHealthSection";
import PredictionResult from "../components/prediction/PredictionResult";
import {
  getErrorMessage,
  getLatestModelMetrics,
  getMarketFilters,
  getMarketDashboard,
  getPredictionHistory,
  predictProperty,
} from "../services/api";

export default function PredictionPage() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [marketKpis, setMarketKpis] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [neighborhoodOptions, setNeighborhoodOptions] = useState([]);
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    getPredictionHistory().then(setHistory).catch((requestError) => setLoadError(getErrorMessage(requestError)));
    getMarketDashboard().then((dashboard) => setMarketKpis(dashboard.kpis)).catch((requestError) => setLoadError(getErrorMessage(requestError)));
    getMarketFilters().then((payload) => setNeighborhoodOptions(payload.neighborhoods || [])).catch((requestError) => setLoadError(getErrorMessage(requestError)));
    getLatestModelMetrics().then(setModelMetrics).catch((requestError) => setLoadError(getErrorMessage(requestError)));
  }, []);

  async function handlePredict(payload) {
    setError("");
    try {
      const response = await predictProperty(payload);
      setResult(response);
      const updatedHistory = await getPredictionHistory();
      setHistory(updatedHistory);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <PageContainer
      title="Estimer un bien"
      subtitle="Renseignez les caracteristiques d'un bien pour obtenir une estimation exploitable, une fourchette de prix et la sante du modele."
    >
      {loadError ? <p className="error">{loadError}</p> : null}
      <div className="prediction-layout">
        <PredictionForm onPredict={handlePredict} error={error} neighborhoodOptions={neighborhoodOptions} />
        <PredictionResult result={result} marketKpis={marketKpis} />
      </div>
      <ModelHealthSection latest={modelMetrics} />
      <PredictionHistory history={history} />
    </PageContainer>
  );
}
