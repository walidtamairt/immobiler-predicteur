import { useEffect, useState } from "react";
import PageContainer from "../components/layout/PageContainer";
import PredictionForm from "../components/prediction/PredictionForm";
import PredictionHistory from "../components/prediction/PredictionHistory";
import ModelHealthSection from "../components/prediction/ModelHealthSection";
import PredictionResult from "../components/prediction/PredictionResult";
import {
  getLatestModelMetrics,
  getMarketDashboard,
  getModelMetricsHistory,
  getPredictionHistory,
  predictProperty,
} from "../services/api";

export default function PredictionPage() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [marketKpis, setMarketKpis] = useState(null);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [modelMetricsHistory, setModelMetricsHistory] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getPredictionHistory().then(setHistory).catch(() => undefined);
    getMarketDashboard().then((dashboard) => setMarketKpis(dashboard.kpis)).catch(() => undefined);
    getLatestModelMetrics().then(setModelMetrics).catch(() => undefined);
    getModelMetricsHistory().then((payload) => setModelMetricsHistory(payload.items || [])).catch(() => undefined);
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
      <div className="prediction-layout">
        <PredictionForm onPredict={handlePredict} error={error} />
        <PredictionResult result={result} marketKpis={marketKpis} />
      </div>
      <ModelHealthSection latest={modelMetrics} history={modelMetricsHistory} />
      <PredictionHistory history={history} />
    </PageContainer>
  );
}
