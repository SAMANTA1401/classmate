import React, { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { FiSend } from "react-icons/fi";
import { FaRobot, FaUser } from "react-icons/fa"; // More icons

const App = () => {
  const [prompt, setPrompt] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const sessionIdRef = useRef(uuidv4());
  const chatBoxRef = useRef(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatLog]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    setChatLog((prev) => [...prev, { sender: "user", message: prompt }]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, session_id: sessionIdRef.current }),
      });

      if (!response.ok) {
        throw new Error("Failed to initiate chat stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let partialData = "";

      const processStream = async () => {
        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            setIsLoading(false);
            break;
          }
          partialData += decoder.decode(value, { stream: true });
          const lines = partialData.split("\n\n");
          partialData = lines.pop() || "";

          lines.forEach((line) => {
            if (line.startsWith("data:")) {
              const message = line.substring(5).trim();
              if (message) {
                setChatLog((prev) => [...prev, { sender: "bot", message }]);
              }
            }
          });
        }
      };

      processStream();
      setPrompt("");
    } catch (error) {
      console.error("Error in chat submission:", error);
      setChatLog((prev) => [
        ...prev,
        { sender: "bot", message: "Error: Could not connect to server" },
      ]);
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-teal-100 to-lime-100 min-h-screen py-10 flex justify-center items-center">
      <div className="max-w-3xl w-full bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="bg-gradient-to-r from-blue-400 to-purple-500 text-white py-8 px-10">
          <h1 className="text-3xl font-bold text-center mb-2">AiClassmate</h1>
          <p className="text-center text-blue-200 text-lg">
            Your Engaging Study Partner
          </p>
        </div>
        <div
          ref={chatBoxRef}
          className="chat-box p-6 h-[450px] overflow-y-auto space-y-4"
        >
          {chatLog.map((entry, idx) => (
            <div
              key={idx}
              className={`flex items-start ${
                entry.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {entry.sender === "bot" && (
                <div className="mr-3 text-gray-600">
                  <FaRobot className="h-6 w-6" />
                </div>
              )}
              <div
                className={`rounded-xl py-3 px-4 shadow-md max-w-[80%] break-words ${
                  entry.sender === "user"
                    ? "bg-indigo-100 text-indigo-800 rounded-br-none"
                    : "bg-gray-100 text-gray-800 rounded-bl-none"
                }`}
              >
                <p className="text-sm font-semibold mb-1">
                  {entry.sender === "user" ? "You" : "AiClassmate"}
                </p>
                <p className="text-sm">{entry.message}</p>
              </div>
              {entry.sender === "user" && (
                <div className="ml-3 text-gray-600">
                  <FaUser className="h-6 w-6" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start items-center">
              <div className="mr-3 text-gray-600">
                <FaRobot className="animate-pulse h-6 w-6" />
              </div>
              <div className="rounded-xl py-2 px-3 bg-gray-100 text-gray-600 shadow-sm max-w-[80%] italic">
                Thinking...
              </div>
            </div>
          )}
        </div>
        <form
          onSubmit={handleSubmit}
          className="p-5 bg-white border-t border-gray-200 flex items-center rounded-b-xl"
        >
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="flex-1 border border-gray-300 rounded-full py-2.5 px-4 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-sm"
            placeholder="Ask your study question..."
            disabled={isLoading}
          />
          <button
            type="submit"
            className={`ml-4 py-2.5 px-5 rounded-full text-white font-semibold shadow-md transition duration-200 ease-in-out ${
              isLoading
                ? "bg-blue-300 cursor-not-allowed"
                : "bg-blue-500 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-75"
            }`}
            disabled={isLoading}
          >
            {isLoading ? (
              <svg
                className="animate-spin h-5 w-5 mr-2 inline-block"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0c-3.17 0-5.89 1.69-7.41 4A8 8 0 014 12z"
                ></path>
              </svg>
            ) : (
              <FiSend className="inline-block mr-2" />
            )}
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default App;
