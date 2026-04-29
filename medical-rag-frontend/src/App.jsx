import { useEffect, useState } from "react";
import { api } from "./api";

const COLORS = {
  navy: "rgb(2, 26, 84)",
  pink: "rgb(255, 133, 187)",
  lightPink: "rgb(255, 206, 227)",
  light: "rgb(245, 245, 245)",
};

function ConfidenceBadge({ value }) {
  const styles = {
    High: "bg-green-100 text-green-700",
    Medium: "bg-yellow-100 text-yellow-700",
    Low: "bg-red-100 text-red-700",
  };

  return (
    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${styles[value] || "bg-slate-100 text-slate-700"}`}>
      {value || "Unknown"}
    </span>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [authMode, setAuthMode] = useState("login");

  const [name, setName] = useState("");
  const [email, setEmail] = useState("doctor@test.com");
  const [password, setPassword] = useState("123456");

  const [question, setQuestion] = useState("");
  const [answerData, setAnswerData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [ingestMessage, setIngestMessage] = useState("");

  const [cdcUrl, setCdcUrl] = useState("");
  const [whoUrl, setWhoUrl] = useState("");
  const [niceUrl, setNiceUrl] = useState("");
  const [pubmedQuery, setPubmedQuery] = useState("");

  const loadMe = async () => {
    const token = localStorage.getItem("ragmedic_token");
    if (!token) return;

    try {
      const res = await api.get("/auth/me");
      setUser(res.data);
      fetchHistory();
    } catch {
      localStorage.removeItem("ragmedic_token");
      setUser(null);
    }
  };

  useEffect(() => {
    loadMe();
  }, []);

  const handleAuth = async () => {
    try {
      const endpoint = authMode === "login" ? "/auth/login" : "/auth/register";

      const payload =
        authMode === "login"
          ? { email, password }
          : { name, email, password };

      const res = await api.post(endpoint, payload);

      localStorage.setItem("ragmedic_token", res.data.token);
      setUser(res.data.user);
      fetchHistory();
    } catch (err) {
      alert(err.response?.data?.detail || "Auth failed");
    }
  };

  const logout = () => {
    localStorage.removeItem("ragmedic_token");
    setUser(null);
    setAnswerData(null);
    setHistory([]);
  };

  const fetchHistory = async () => {
    try {
      const res = await api.get("/history");
      setHistory(res.data);
    } catch {
      setHistory([]);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setAnswerData(null);

    try {
      const res = await api.post("/ask", { question });
      setAnswerData(res.data);
      fetchHistory();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to get answer");
    } finally {
      setLoading(false);
    }
  };

  const ingestPubMed = async () => {
    if (!pubmedQuery.trim()) return;

    const res = await api.post("/ingest/pubmed", {
      query: pubmedQuery,
      limit: 5,
    });

    setIngestMessage(`PubMed: ${res.data.chunks_stored} chunks stored`);
  };

  const ingestUrl = async (type) => {
    const map = {
      cdc: ["/ingest/cdc-url", cdcUrl],
      who: ["/ingest/who-url", whoUrl],
      nice: ["/ingest/nice-url", niceUrl],
    };

    const [endpoint, url] = map[type];
    if (!url.trim()) return;

    const res = await api.post(endpoint, { url });
    setIngestMessage(`${type.toUpperCase()}: ${res.data.chunks_stored} chunks stored`);
  };

  if (!user) {
    return (
      <div
        className="min-h-screen flex items-center justify-center p-4"
        style={{ backgroundColor: COLORS.light }}
      >
        <div className="bg-white border shadow-sm rounded-3xl p-6 w-full max-w-md">
          <h1 className="text-3xl font-bold" style={{ color: COLORS.navy }}>
            RagMedic
          </h1>
          <p className="text-sm mt-1" style={{ color: COLORS.navy }}>
            Source-backed medical Q&A assistant
          </p>

          <div className="flex gap-2 mt-6">
            <button
              onClick={() => setAuthMode("login")}
              className="flex-1 py-2 rounded-xl text-sm font-medium"
              style={{
                backgroundColor: authMode === "login" ? COLORS.navy : COLORS.lightPink,
                color: authMode === "login" ? "white" : COLORS.navy,
              }}
            >
              Login
            </button>

            <button
              onClick={() => setAuthMode("register")}
              className="flex-1 py-2 rounded-xl text-sm font-medium"
              style={{
                backgroundColor: authMode === "register" ? COLORS.navy : COLORS.lightPink,
                color: authMode === "register" ? "white" : COLORS.navy,
              }}
            >
              Register
            </button>
          </div>

          <div className="space-y-3 mt-5">
            {authMode === "register" && (
              <input
                className="w-full border rounded-xl p-3 text-sm outline-none"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            )}

            <input
              className="w-full border rounded-xl p-3 text-sm outline-none"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <input
              className="w-full border rounded-xl p-3 text-sm outline-none"
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <button
              onClick={handleAuth}
              className="w-full py-3 rounded-xl font-medium text-white"
              style={{ backgroundColor: COLORS.pink }}
            >
              {authMode === "login" ? "Login" : "Create Account"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: COLORS.light, color: COLORS.navy }}
    >
      <header
        className="sticky top-0 z-20 border-b"
        style={{ backgroundColor: COLORS.navy }}
      >
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between gap-4 items-center">
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-white">
              RagMedic
            </h1>
            <p className="text-sm" style={{ color: COLORS.lightPink }}>
              Welcome, {user.name}
            </p>
          </div>

          <button
            onClick={logout}
            className="px-4 py-2 rounded-xl text-sm font-medium"
            style={{ backgroundColor: COLORS.pink, color: COLORS.navy }}
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4 grid gap-5 lg:grid-cols-3">
        <section className="lg:col-span-2 space-y-5">
          <div className="bg-white rounded-3xl shadow-sm border p-4 md:p-5">
            <h2 className="font-semibold text-lg mb-3">Ask Medical Query</h2>

            <textarea
              className="w-full min-h-36 border rounded-2xl p-4 outline-none resize-none"
              placeholder="Example: What is first-line treatment for type 2 diabetes?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />

            <button
              onClick={askQuestion}
              disabled={loading}
              className="mt-3 w-full md:w-auto px-6 py-3 rounded-2xl font-medium disabled:opacity-60"
              style={{ backgroundColor: COLORS.pink, color: COLORS.navy }}
            >
              {loading ? "Generating answer..." : "Ask"}
            </button>
          </div>

          {answerData && (
            <div className="bg-white rounded-3xl shadow-sm border p-4 md:p-5">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-lg">Answer</h2>
                <ConfidenceBadge value={answerData.confidence} />
              </div>

              <div
                className="mt-4 border rounded-2xl p-4"
                style={{ backgroundColor: COLORS.light }}
              >
                <pre className="whitespace-pre-wrap text-sm leading-6 font-sans">
                  {answerData.answer}
                </pre>
              </div>

              <p className="text-sm mt-4">
                <b>Reason:</b> {answerData.reason}
              </p>

              <h3 className="font-semibold mt-5 mb-3">Sources</h3>

              <div className="space-y-3">
                {answerData.sources?.length ? (
                  answerData.sources.map((src, index) => (
                    <a
                      key={index}
                      href={src.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block border rounded-2xl p-4 text-sm hover:opacity-90"
                      style={{ backgroundColor: COLORS.lightPink }}
                    >
                      <div className="flex justify-between gap-3">
                        <b>{src.source}</b>
                        <span className="text-xs">Score: {src.score ?? "N/A"}</span>
                      </div>
                      <p className="mt-1">{src.title}</p>
                      <p className="mt-1 truncate" style={{ color: COLORS.navy }}>
                        {src.url}
                      </p>
                    </a>
                  ))
                ) : (
                  <p className="text-sm">No sources found.</p>
                )}
              </div>
            </div>
          )}

          <div className="bg-white rounded-3xl shadow-sm border p-4 md:p-5">
            <h2 className="font-semibold text-lg mb-3">Query History</h2>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {history.map((item) => (
                <div key={item.id} className="border rounded-2xl p-4">
                  <p className="font-medium text-sm">{item.question}</p>

                  <div className="mt-2">
                    <ConfidenceBadge value={item.confidence} />
                  </div>

                  <div
                    className="mt-3 rounded-xl p-3 text-sm whitespace-pre-wrap"
                    style={{ backgroundColor: COLORS.light }}
                  >
                    {item.answer}
                  </div>

                  {item.sources?.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="font-semibold text-sm">Sources</p>

                      {item.sources.map((src, i) => (
                        <a
                          key={i}
                          href={src.url}
                          target="_blank"
                          rel="noreferrer"
                          className="block text-sm underline"
                          style={{ color: COLORS.navy }}
                        >
                          {src.source} — {src.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        <aside className="space-y-5">
          <div className="bg-white rounded-3xl shadow-sm border p-4 md:p-5">
            <h2 className="font-semibold text-lg mb-1">Admin Ingestion</h2>
            <p className="text-sm mb-4">
              Add trusted medical sources into Qdrant.
            </p>

            {ingestMessage && (
              <div
                className="mb-4 text-sm border rounded-xl p-3"
                style={{
                  backgroundColor: COLORS.lightPink,
                  color: COLORS.navy,
                }}
              >
                {ingestMessage}
              </div>
            )}

            <div className="space-y-3">
              <input
                className="w-full border rounded-2xl p-3 text-sm"
                placeholder="PubMed query"
                value={pubmedQuery}
                onChange={(e) => setPubmedQuery(e.target.value)}
              />
              <button
                onClick={ingestPubMed}
                className="w-full py-3 rounded-2xl text-sm font-medium"
                style={{ backgroundColor: COLORS.navy, color: "white" }}
              >
                Ingest PubMed
              </button>

              <input
                className="w-full border rounded-2xl p-3 text-sm"
                placeholder="CDC URL"
                value={cdcUrl}
                onChange={(e) => setCdcUrl(e.target.value)}
              />
              <button
                onClick={() => ingestUrl("cdc")}
                className="w-full py-3 rounded-2xl text-sm font-medium"
                style={{ backgroundColor: COLORS.navy, color: "white" }}
              >
                Ingest CDC URL
              </button>

              <input
                className="w-full border rounded-2xl p-3 text-sm"
                placeholder="WHO URL"
                value={whoUrl}
                onChange={(e) => setWhoUrl(e.target.value)}
              />
              <button
                onClick={() => ingestUrl("who")}
                className="w-full py-3 rounded-2xl text-sm font-medium"
                style={{ backgroundColor: COLORS.navy, color: "white" }}
              >
                Ingest WHO URL
              </button>

              <input
                className="w-full border rounded-2xl p-3 text-sm"
                placeholder="NICE URL"
                value={niceUrl}
                onChange={(e) => setNiceUrl(e.target.value)}
              />
              <button
                onClick={() => ingestUrl("nice")}
                className="w-full py-3 rounded-2xl text-sm font-medium"
                style={{ backgroundColor: COLORS.navy, color: "white" }}
              >
                Ingest NICE URL
              </button>
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}