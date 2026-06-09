import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import AssistantPage from "./pages/AssistantPage";
import MarketPage from "./pages/MarketPage";
import PredictionPage from "./pages/PredictionPage";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="content-shell">
        <Routes>
          <Route path="/" element={<Navigate to="/market" replace />} />
          <Route path="/market" element={<MarketPage />} />
          <Route path="/prediction" element={<PredictionPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="*" element={<Navigate to="/market" replace />} />
        </Routes>
      </main>
    </div>
  );
}
