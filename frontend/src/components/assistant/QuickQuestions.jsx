const quickQuestions = [
  "Quels sont les quartiers les plus chers ?",
  "La qualite influence-t-elle beaucoup le prix ?",
  "La surface ou le quartier a-t-il le plus d'impact ?",
  "Comment interpreter une prediction elevee ?",
  "Y a-t-il une saison ou les prix augmentent ?",
];

export default function QuickQuestions({ onSelect }) {
  return (
    <section className="chart-card quick-panel">
      <div className="card-header">
        <h3>Questions rapides</h3>
        <p>Lancez une question type pour guider la demonstration de l'assistant.</p>
      </div>
      <div className="quick-question-list">
        {quickQuestions.map((question) => (
          <button key={question} type="button" className="quick-question" onClick={() => onSelect(question)}>
            {question}
          </button>
        ))}
      </div>
    </section>
  );
}
