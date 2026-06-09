import { useState } from "react";
import ChartCard from "../common/ChartCard";

export default function ChatWindow({ messages, loading, mode, onSend }) {
  const [input, setInput] = useState("");

  async function submit(event) {
    event.preventDefault();
    const content = input;
    setInput("");
    await onSend(content);
  }

  return (
    <ChartCard title="Conversation" subtitle={`Mode actuel : ${mode}`}>
      <div className="assistant-messages">
        {messages.map((message, index) => (
          <article key={`${message.role}-${index}`} className={`assistant-message ${message.role}`}>
            <strong>{message.role === "user" ? "Vous" : "Assistant"}</strong>
            <p>{message.content}</p>
          </article>
        ))}
        {loading ? <p className="assistant-loading">L'assistant ecrit...</p> : null}
      </div>
      <form className="assistant-form" onSubmit={submit}>
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Posez une question sur le marche immobilier."
          rows={4}
        />
        <button className="primary-button" type="submit" disabled={loading}>Envoyer</button>
      </form>
    </ChartCard>
  );
}
