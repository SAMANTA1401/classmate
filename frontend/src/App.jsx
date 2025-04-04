// App.jsx
import React, { useState, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
// import { EventSourcePolyfill } from 'eventsource-polyfill';
import EventSourcePolyfill from 'eventsource-polyfill';

const App = () => {
  const [prompt, setPrompt] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const sessionIdRef = useRef(uuidv4());

  const handleSubmit = async (e) => {
    e.preventDefault();
    setChatLog([...chatLog, { sender: "user", message: prompt }]);
    const eventSource = new EventSourcePolyfill("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, session_id: sessionIdRef.current }),
    });

    eventSource.onmessage = (event) => {
      setChatLog((prev) => [...prev, { sender: "bot", message: event.data }]);
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    setPrompt("");
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">AI Chatbot</h1>
      <div className="chat-box mb-4 border p-4 h-64 overflow-y-auto">
        {chatLog.map((entry, idx) => (
          <div key={idx} className="mb-2">
            <strong>{entry.sender}:</strong> {entry.message}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="flex-1 border p-2"
          placeholder="Type your prompt"
        />
        <button type="submit" className="bg-blue-500 text-white p-2">
          Send
        </button>
      </form>
    </div>
  );
};

export default App;
