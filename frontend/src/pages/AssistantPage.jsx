import { useEffect, useState } from "react";
import ChatWindow from "../components/assistant/ChatWindow";
import QuickQuestions from "../components/assistant/QuickQuestions";
import KpiCard from "../components/common/KpiCard";
import PageContainer from "../components/layout/PageContainer";
import { getMarketDashboard, sendChatMessage } from "../services/api";
import { formatPrice } from "../utils/display";

export default function AssistantPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Bonjour. Posez-moi une question sur le marche immobilier, les quartiers, la qualite ou les tendances de prix.",
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("pret");
  const [marketKpis, setMarketKpis] = useState(null);

  useEffect(() => {
    getMarketDashboard().then((dashboard) => setMarketKpis(dashboard.kpis)).catch(() => undefined);
  }, []);

  async function submitMessage(content) {
    if (!content.trim() || loading) return;
    const nextMessages = [...messages, { role: "user", content: content.trim() }];
    setMessages(nextMessages);
    setLoading(true);
    try {
      const response = await sendChatMessage(
        nextMessages
          .filter((message) => message.role === "user" || message.role === "assistant")
          .map((message) => ({ role: message.role, content: message.content }))
      );
      setMode(response.mode || "pret");
      setMessages([...nextMessages, { role: "assistant", content: response.answer }]);
    } catch {
      setMessages([
        ...nextMessages,
        { role: "assistant", content: "Impossible de recuperer une reponse pour le moment." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageContainer
      title="Assistant IA"
      subtitle="Interpretez le marche, confrontez vos hypotheses et obtenez des reponses contextualisees a partir des donnees disponibles."
    >
      <div className="assistant-layout">
        <aside className="assistant-sidebar">
          <QuickQuestions onSelect={submitMessage} />
          <section className="chart-card assistant-support-card">
            <div className="card-header">
              <h3>Role de l'assistant</h3>
              <p>Il synthese les tendances du marche, aide a lire les KPIs et reformule les insights utiles pour la decision.</p>
            </div>
          </section>
          <section className="chart-card assistant-support-card">
            <div className="card-header">
              <h3>Resume marche</h3>
              <p>Quelques reperes cles pour situer rapidement le niveau de marche courant.</p>
            </div>
            <div className="assistant-kpis">
              <KpiCard label="Prix moyen" value={formatPrice(marketKpis?.averagePrice)} />
              <KpiCard label="Prix median" value={formatPrice(marketKpis?.medianPrice)} />
              <KpiCard label="Biens" value={marketKpis?.totalProperties || 0} />
            </div>
          </section>
        </aside>
        <ChatWindow messages={messages} loading={loading} mode={mode} onSend={submitMessage} />
      </div>
    </PageContainer>
  );
}
