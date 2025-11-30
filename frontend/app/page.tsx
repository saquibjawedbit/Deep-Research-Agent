"use client";

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface StatusUpdate {
  type: string;
  message: string;
  agent?: string;
  result?: string;
  task?: string;
  description?: string;
  tool?: string;
  progress?: number;
  details?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<StatusUpdate | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStatus]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const query = input;
    setInput("");
    setLoading(true);
    setCurrentStatus({ type: "started", message: "Connecting to research agent..." });

    try {
      // Use SSE streaming endpoint
      const eventSource = new EventSource(
        `http://localhost:8000/api/research/stream?${new URLSearchParams({
          query,
          sources: "papers, web",
          max_docs: "5",
        })}`
      );

      eventSource.onmessage = (event) => {
        const data: StatusUpdate = JSON.parse(event.data);

        if (data.type === "completed" && data.result) {
          // Final result received
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: data.result,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setCurrentStatus(null);
          setLoading(false);
          eventSource.close();
        } else if (data.type === "error") {
          // Error occurred
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: `❌ Error: ${data.message}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
          setCurrentStatus(null);
          setLoading(false);
          eventSource.close();
        } else if (data.type === "done") {
          // Stream ended
          eventSource.close();
        } else {
          // Status update
          setCurrentStatus(data);
        }
      };

      eventSource.onerror = (error) => {
        console.error("SSE Error:", error);
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "❌ Error: Connection to research agent lost",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        setCurrentStatus(null);
        setLoading(false);
        eventSource.close();
      };

    } catch (err) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `❌ Error: ${err instanceof Error ? err.message : "An unknown error occurred"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setCurrentStatus(null);
      setLoading(false);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="h-screen flex flex-col relative overflow-hidden bg-black">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-20"
          style={{ backgroundImage: "url('/bg.png')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black via-purple-950/30 to-black" />
      </div>

      {/* Gradient Orbs */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl animate-pulse pointer-events-none" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ animationDelay: "1s" }} />

      {/* Header - Only show when there are messages */}
      {hasMessages && (
        <div className="relative z-10 border-b border-gray-800/50 bg-black/40 backdrop-blur-xl animate-slide-up-fade">
          <div className="max-w-5xl mx-auto px-4 py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center animate-glow-pulse">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                  Deep Research Agent
                </h1>
                <p className="text-xs text-gray-400">AI-powered research assistant</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Messages Container or Empty State */}
      <div className={`relative z-10 flex-1 overflow-y-auto ${!hasMessages ? 'flex items-center justify-center' : ''}`}>
        {!hasMessages ? (
          <div className="flex flex-col items-center justify-center text-center px-4 max-w-4xl mx-auto w-full">
            <div className="mb-12 animate-slide-up-fade">
              <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center mb-6 border border-purple-500/20 mx-auto">
                <svg className="w-12 h-12 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h1 className="text-5xl md:text-6xl font-black mb-4 bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                Deep Research Agent
              </h1>
              <p className="text-xl text-gray-400 mb-8">
                Ask me anything and I'll conduct deep research across academic papers and web sources
              </p>
            </div>

            {/* Centered Input */}
            <div className="w-full max-w-3xl mb-12 animate-slide-up-fade" style={{ animationDelay: "0.1s" }}>
              <form onSubmit={handleSubmit} className="relative">
                <div className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-3xl opacity-30 group-hover:opacity-50 blur transition duration-300" />
                  <div className="relative flex items-center">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask me to research anything..."
                      disabled={loading}
                      className="w-full px-8 py-5 pr-16 bg-gray-900/95 border border-gray-700/50 rounded-3xl text-white text-lg placeholder-gray-500 focus:outline-none focus:border-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      autoFocus
                    />
                    <button
                      type="submit"
                      disabled={loading || !input.trim()}
                      className="absolute right-2 p-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-purple-500/50 transition-all"
                    >
                      {loading ? (
                        <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                      ) : (
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </div>

            {/* Suggestion Chips */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl w-full animate-slide-up-fade" style={{ animationDelay: "0.2s" }}>
              {[
                "Latest developments in quantum computing",
                "Impact of AI on healthcare",
                "Climate change mitigation strategies",
                "Future of renewable energy"
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => setInput(suggestion)}
                  className="glass-morphism px-5 py-3 rounded-xl text-sm text-gray-300 hover:text-white hover:border-purple-500/50 transition-all text-left"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-5xl mx-auto px-4 py-6">
            <div className="space-y-6 pb-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  {message.role === "assistant" && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0 mt-1">
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                  )}
                  <div className={`max-w-3xl ${message.role === "user" ? "ml-auto" : ""}`}>
                    <div
                      className={`rounded-2xl px-5 py-3 ${message.role === "user"
                        ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white"
                        : "glass-morphism bg-gray-900/50 text-gray-100"
                        }`}
                    >
                      {message.role === "assistant" ? (
                        <div className="prose prose-invert prose-sm max-w-none prose-headings:text-white prose-p:text-gray-300 prose-a:text-purple-400 prose-strong:text-white prose-code:text-pink-400 prose-code:bg-pink-400/10 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-table:border-collapse prose-th:border prose-th:border-gray-700 prose-th:bg-gray-800/50 prose-th:px-4 prose-th:py-2 prose-td:border prose-td:border-gray-700 prose-td:px-4 prose-td:py-2">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                        </div>
                      ) : (
                        <p className="text-sm">{message.content}</p>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-1 px-2">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  {message.role === "user" && (
                    <div className="w-8 h-8 rounded-lg bg-gray-700 flex items-center justify-center flex-shrink-0 mt-1">
                      <svg className="w-5 h-5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                  )}
                </div>
              ))}
              {loading && currentStatus && (
                <div className="flex gap-3 animate-slide-up-fade">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0 animate-glow-pulse">
                    {currentStatus.type === 'system' || currentStatus.type === 'started' ? (
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    ) : currentStatus.type === 'thinking' ? (
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    ) : currentStatus.type === 'tool_start' || currentStatus.type === 'action' ? (
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    ) : currentStatus.type === 'task_completed' || currentStatus.type === 'step_complete' ? (
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    )}
                  </div>
                  <div className="glass-morphism bg-gray-900/50 rounded-2xl px-5 py-3 max-w-3xl flex-1">
                    <div className="space-y-2">
                      {currentStatus.agent && (
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                          <span className="text-xs font-semibold text-purple-400">{currentStatus.agent}</span>
                          {currentStatus.task && (
                            <span className="text-xs text-gray-500">• {currentStatus.task}</span>
                          )}
                        </div>
                      )}
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                        </div>
                        <span className="text-sm text-gray-300">{currentStatus.message}</span>
                      </div>
                      {currentStatus.progress !== undefined && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                            <span>Research Progress</span>
                            <span>{currentStatus.progress}%</span>
                          </div>
                          <div className="w-full bg-gray-800 rounded-full h-1.5">
                            <div
                              className="bg-gradient-to-r from-purple-500 to-blue-500 h-1.5 rounded-full transition-all duration-500"
                              style={{ width: `${currentStatus.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                      {currentStatus.description && (
                        <p className="text-xs text-gray-500 mt-1">{currentStatus.description}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* Bottom Input Bar - Only show when there are messages */}
      {hasMessages && (
        <div className="relative z-10 border-t border-gray-800/50 bg-black/40 backdrop-blur-xl animate-slide-up-fade">
          <div className="max-w-5xl mx-auto px-4 py-4">
            <form onSubmit={handleSubmit} className="relative">
              <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl opacity-30 group-hover:opacity-50 blur transition duration-300" />
                <div className="relative flex items-center">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask me to research anything..."
                    disabled={loading}
                    className="w-full px-6 py-4 pr-14 bg-gray-900/95 border border-gray-700/50 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    className="absolute right-2 p-2.5 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl text-white disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-purple-500/50 transition-all"
                  >
                    {loading ? (
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
