import React, { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    setChat((prev) => [...prev, { from: "user", text: question }]);

    try {
      const res = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();

      setChat((prev) => [...prev, { from: "bot", text: data.answer }]);
    } catch (error) {
      setChat((prev) => [...prev, { from: "bot", text: "Error: Could not reach backend." }]);
    }

    setQuestion("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendQuestion();
  };

  return (
    <div style={{ maxWidth: 600, margin: "30px auto", fontFamily: "Arial, sans-serif" }}>
      <h2>Alzheimer Research Chatbot</h2>

      <div style={{ border: "1px solid #ddd", padding: 10, height: 400, overflowY: "auto", marginBottom: 10 }}>
        {chat.map((msg, i) => (
          <div
            key={i}
            style={{
              textAlign: msg.from === "user" ? "right" : "left",
              marginBottom: 10,
            }}
          >
            <span
              style={{
                background: msg.from === "user" ? "#daf1da" : "#eee",
                padding: 8,
                borderRadius: 5,
                display: "inline-block",
                maxWidth: "80%",
                whiteSpace: "pre-wrap",
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
      </div>

      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder="Ask a question..."
        style={{ width: "100%", padding: 10, fontSize: 16 }}
      />

      <button onClick={sendQuestion} style={{ marginTop: 10, padding: "10px 20px", fontSize: 16 }}>
        Send
      </button>
    </div>
  );
}

export default App;
