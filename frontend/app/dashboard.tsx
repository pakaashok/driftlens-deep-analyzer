"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchEnvironments,
  analyzeEnvironments,
  fetchMatrix,
  fetchDriftResults,
  type DeepAnalysis,
  type MatrixResult,
  type DriftResults,
} from "@/lib/api";
import {
  Activity,
  GitCompare,
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  RefreshCw,
  AlertCircle,
  ChevronRight,
  Radio,
  Clock,
  GitCommit,
  User,
} from "lucide-react";

function ScoreCard({
  title,
  score,
  drift,
  color,
  icon: Icon,
}: {
  title: string;
  score: number;
  drift: number;
  color: string;
  icon: React.ElementType;
}) {
  return (
    <div className={`rounded-xl border p-5 ${color}`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon className="w-4 h-4" />
        <span className="text-xs font-bold
          uppercase tracking-wider">
          {title}
        </span>
      </div>
      <div className="text-3xl font-bold
        font-mono mb-1">
        {score.toFixed(1)}%
      </div>
      <div className="flex items-center
        justify-between">
        <span className="text-xs opacity-70">
          similarity
        </span>
        <span className="text-xs font-mono">
          drift: {drift.toFixed(1)}%
        </span>
      </div>
      <div className="mt-3 w-full h-1.5
        bg-black/20 rounded-full overflow-hidden">
        <div
          className="h-full bg-current rounded-full
            opacity-70 transition-all duration-700"
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

function DriftBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    "NO DRIFT":
      "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    "LOW DRIFT":
      "bg-blue-500/20 text-blue-400 border-blue-500/30",
    "MODERATE DRIFT":
      "bg-amber-500/20 text-amber-400 border-amber-500/30",
    "HIGH DRIFT":
      "bg-orange-500/20 text-orange-400 border-orange-500/30",
    "CRITICAL DRIFT":
      "bg-rose-500/20 text-rose-400 border-rose-500/30",
  };
  return (
    <span className={`px-3 py-1 rounded-full
      text-xs font-bold border
      ${colors[level] ||
        "bg-slate-500/20 text-slate-400"}`}>
      {level}
    </span>
  );
}

function LiveBadge() {
  return (
    <div className="flex items-center gap-1.5
      px-3 py-1 rounded-full
      bg-emerald-500/10
      border border-emerald-500/20">
      <span className="w-2 h-2 rounded-full
        bg-emerald-400 animate-pulse" />
      <span className="text-xs font-semibold
        text-emerald-400">
        LIVE
      </span>
    </div>
  );
}

export default function Dashboard() {
  const [environments, setEnvironments] =
    useState<string[]>([]);
  const [envA, setEnvA] = useState("");
  const [envB, setEnvB] = useState("");
  const [result, setResult] =
    useState<DeepAnalysis | null>(null);
  const [matrix, setMatrix] =
    useState<MatrixResult | null>(null);
  const [driftResults, setDriftResults] =
    useState<DriftResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "live" | "manual" | "matrix"
  >("live");
  const [lastUpdated, setLastUpdated] =
    useState<string>("");
  const [polling, setPolling] = useState(true);

  // Load drift results (auto-updated by GitHub Actions)
  const loadDriftResults = useCallback(async () => {
    try {
      const data = await fetchDriftResults();
      if (data && !data.status) {
        setDriftResults(data);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch {}
  }, []);

  // Load matrix
  const loadMatrix = useCallback(async () => {
    try {
      const data = await fetchMatrix();
      setMatrix(data);
    } catch {}
  }, []);

  // Initial load
  useEffect(() => {
    fetchEnvironments()
      .then((d) => {
        setEnvironments(d.environments);
        if (d.environments.length >= 2) {
          setEnvA(d.environments[0]);
          setEnvB(d.environments[1]);
        }
      })
      .catch(() =>
        setError("Cannot connect to backend")
      );

    loadDriftResults();
    loadMatrix();
  }, [loadDriftResults, loadMatrix]);

  // Auto-poll every 30 seconds
  useEffect(() => {
    if (!polling) return;
    const interval = setInterval(() => {
      loadDriftResults();
      loadMatrix();
    }, 30000);
    return () => clearInterval(interval);
  }, [polling, loadDriftResults, loadMatrix]);

  const handleAnalyze = async () => {
    if (!envA || !envB || envA === envB) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await analyzeEnvironments(envA, envB);
      setResult(data);
    } catch {
      setError("Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  const liveAnalysis = driftResults?.analysis;
  const valueDiffs = result
    ? Object.entries(
        result.analysis.cosine.value_differences
      )
    : liveAnalysis
    ? Object.entries(
        liveAnalysis.cosine.value_differences
      )
    : [];

  return (
    <div className="min-h-screen
      bg-[hsl(222,47%,6%)] text-white">

      {/* Header */}
      <header className="border-b border-white/10
        bg-black/20 backdrop-blur-xl
        sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4
          flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl
              bg-gradient-to-br from-cyan-400
              to-violet-600 flex items-center
              justify-center shadow-lg">
              <Activity className="w-5 h-5
                text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold">
                DriftLens{" "}
                <span className="text-cyan-400">
                  Deep Analyzer
                </span>
              </h1>
              <p className="text-xs text-white/40">
                JACCARD + COSINE SIMILARITY
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <LiveBadge />
            {lastUpdated && (
              <span className="text-xs
                text-white/30 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {lastUpdated}
              </span>
            )}
            <button
              onClick={() => setPolling(!polling)}
              className={`px-3 py-1.5 rounded-lg
                text-xs font-medium border
                transition-all
                ${polling
                  ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                  : "border-white/10 text-white/40"
                }`}
            >
              <Radio className="w-3 h-3 inline mr-1" />
              {polling ? "Auto-refresh ON" : "Auto-refresh OFF"}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto
        px-6 py-8 space-y-6">

        {error && (
          <div className="flex items-center gap-3
            p-4 rounded-xl border
            border-rose-500/20 bg-rose-500/10
            text-rose-400 text-sm">
            <AlertCircle className="w-4 h-4
              flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-1 p-1 rounded-xl
          bg-white/5 border border-white/10 w-fit">
          {[
            { id: "live",   label: "🔴 Live Drift" },
            { id: "manual", label: "🔬 Manual" },
            { id: "matrix", label: "📊 Matrix" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() =>
                setActiveTab(
                  tab.id as typeof activeTab
                )
              }
              className={`px-4 py-2 rounded-lg
                text-sm font-medium transition-all
                ${activeTab === tab.id
                  ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                  : "text-white/50 hover:text-white"
                }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* LIVE TAB - Auto-updated by GitHub Actions */}
        {activeTab === "live" && (
          <div className="space-y-4">

            {liveAnalysis ? (
              <>
                {/* Git Info */}
                {driftResults && (
                  <div className="rounded-xl border
                    border-white/10 bg-white/5 p-4
                    flex items-center gap-6
                    flex-wrap">
                    <div className="flex items-center
                      gap-2 text-xs text-white/50">
                      <GitCommit className="w-3.5 h-3.5" />
                      <span className="font-mono">
                        {driftResults.commit
                          .slice(0, 8)}
                      </span>
                    </div>
                    <div className="flex items-center
                      gap-2 text-xs text-white/50">
                      <User className="w-3.5 h-3.5" />
                      {driftResults.triggered_by}
                    </div>
                    <div className="flex items-center
                      gap-2 text-xs text-white/50">
                      <Clock className="w-3.5 h-3.5" />
                      {new Date(
                        driftResults.timestamp
                      ).toLocaleString()}
                    </div>
                    <div className="ml-auto text-xs
                      text-white/40 italic">
                      {driftResults.commit_message}
                    </div>
                  </div>
                )}

                {/* Score Cards */}
                <div className="grid grid-cols-3 gap-4">
                  <ScoreCard
                    title="Jaccard"
                    score={liveAnalysis.jaccard
                      .similarity_percentage}
                    drift={liveAnalysis.jaccard
                      .key_drift_percentage}
                    color="border-cyan-500/20
                      bg-cyan-500/10 text-cyan-400"
                    icon={GitCompare}
                  />
                  <ScoreCard
                    title="Cosine"
                    score={liveAnalysis.cosine
                      .similarity_percentage}
                    drift={liveAnalysis.cosine
                      .value_drift_percentage}
                    color="border-violet-500/20
                      bg-violet-500/10 text-violet-400"
                    icon={Activity}
                  />
                  <ScoreCard
                    title="Combined"
                    score={liveAnalysis.combined
                      .similarity_percentage}
                    drift={liveAnalysis.combined
                      .overall_drift_percentage}
                    color="border-emerald-500/20
                      bg-emerald-500/10 text-emerald-400"
                    icon={Zap}
                  />
                </div>

                {/* Recommendation */}
                <div className="rounded-xl border
                  border-white/10 bg-white/5 p-4
                  flex items-center justify-between">
                  <p className="text-sm text-white/80">
                    {liveAnalysis.combined.recommendation}
                  </p>
                  <DriftBadge
                    level={
                      liveAnalysis.combined.drift_level
                    }
                  />
                </div>

                {/* Value Differences */}
                {valueDiffs.length > 0 && (
                  <div className="rounded-xl border
                    border-white/10 overflow-hidden">
                    <div className="px-4 py-3
                      bg-white/5 border-b
                      border-white/10 flex items-center
                      justify-between">
                      <span className="text-sm
                        font-semibold text-white">
                        Value Differences
                      </span>
                      <span className="text-xs
                        px-2 py-0.5 rounded-full
                        bg-violet-500/20 text-violet-400
                        font-bold">
                        {valueDiffs.length} changes
                      </span>
                    </div>
                    <div className="grid grid-cols-4
                      px-4 py-2 bg-white/5 text-xs
                      font-semibold text-white/40
                      uppercase tracking-wider
                      border-b border-white/10">
                      <div>Config Key</div>
                      <div className="text-cyan-400">
                        dev
                      </div>
                      <div className="text-violet-400">
                        prod
                      </div>
                      <div>Change</div>
                    </div>
                    <div className="divide-y
                      divide-white/5">
                      {valueDiffs.map(([key, diff]) => (
                        <div key={key}
                          className="grid grid-cols-4
                            px-4 py-3 hover:bg-white/5
                            transition-colors">
                          <div className="text-xs
                            font-mono text-white/70
                            truncate pr-2"
                            title={key}>
                            {key}
                          </div>
                          <div className="text-xs
                            font-mono text-cyan-400
                            truncate"
                            title={diff.value_a}>
                            {diff.value_a}
                          </div>
                          <div className="text-xs
                            font-mono text-violet-400
                            truncate"
                            title={diff.value_b}>
                            {diff.value_b}
                          </div>
                          <div className="flex
                            items-center gap-1
                            text-xs font-mono">
                            {diff.direction === "increased"
                              ? <ArrowUp className="w-3 h-3 text-rose-400" />
                              : diff.direction === "decreased"
                              ? <ArrowDown className="w-3 h-3 text-emerald-400" />
                              : <Minus className="w-3 h-3 text-white/40" />
                            }
                            <span className={
                              diff.direction === "increased"
                                ? "text-rose-400"
                                : diff.direction === "decreased"
                                ? "text-emerald-400"
                                : "text-white/40"
                            }>
                              {diff.change_pct > 0
                                ? `${diff.change_pct.toFixed(0)}%`
                                : "~"}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="rounded-2xl border
                border-white/10 bg-white/5 p-16
                flex flex-col items-center gap-4">
                <RefreshCw className="w-8 h-8
                  text-cyan-400 animate-spin" />
                <div className="text-center">
                  <p className="text-white
                    font-semibold">
                    Waiting for drift results...
                  </p>
                  <p className="text-white/40
                    text-sm mt-1">
                    Push a k8s config change to
                    trigger detection
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* MANUAL TAB */}
        {activeTab === "manual" && (
          <div className="space-y-4">
            <div className="rounded-2xl border
              border-white/10 bg-white/5 p-6">
              <h2 className="text-sm font-semibold
                text-white/60 uppercase
                tracking-wider mb-4">
                Manual Analysis
              </h2>
              <div className="flex items-center
                gap-4 flex-wrap">
                <select
                  value={envA}
                  onChange={(e) =>
                    setEnvA(e.target.value)
                  }
                  className="px-4 py-2.5 rounded-xl
                    border border-white/10
                    bg-white/10 text-white text-sm
                    font-medium focus:outline-none
                    focus:border-cyan-500/50 min-w-32"
                >
                  {environments.map((e) => (
                    <option key={e} value={e}
                      className="bg-slate-900">
                      {e}
                    </option>
                  ))}
                </select>
                <ChevronRight className="w-5 h-5
                  text-white/30" />
                <select
                  value={envB}
                  onChange={(e) =>
                    setEnvB(e.target.value)
                  }
                  className="px-4 py-2.5 rounded-xl
                    border border-white/10
                    bg-white/10 text-white text-sm
                    font-medium focus:outline-none
                    focus:border-cyan-500/50 min-w-32"
                >
                  {environments.map((e) => (
                    <option key={e} value={e}
                      className="bg-slate-900">
                      {e}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleAnalyze}
                  disabled={
                    loading || envA === envB
                  }
                  className="px-6 py-2.5 rounded-xl
                    bg-gradient-to-r from-cyan-500
                    to-violet-600 text-white text-sm
                    font-semibold hover:opacity-90
                    disabled:opacity-50
                    flex items-center gap-2"
                >
                  {loading
                    ? <RefreshCw className="w-4 h-4 animate-spin" />
                    : <Zap className="w-4 h-4" />
                  }
                  {loading ? "Analyzing..." : "Analyze"}
                </button>
              </div>
            </div>

            {result && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <ScoreCard
                    title="Jaccard"
                    score={result.analysis.jaccard
                      .similarity_percentage}
                    drift={result.analysis.jaccard
                      .key_drift_percentage}
                    color="border-cyan-500/20
                      bg-cyan-500/10 text-cyan-400"
                    icon={GitCompare}
                  />
                  <ScoreCard
                    title="Cosine"
                    score={result.analysis.cosine
                      .similarity_percentage}
                    drift={result.analysis.cosine
                      .value_drift_percentage}
                    color="border-violet-500/20
                      bg-violet-500/10 text-violet-400"
                    icon={Activity}
                  />
                  <ScoreCard
                    title="Combined"
                    score={result.analysis.combined
                      .similarity_percentage}
                    drift={result.analysis.combined
                      .overall_drift_percentage}
                    color="border-emerald-500/20
                      bg-emerald-500/10 text-emerald-400"
                    icon={Zap}
                  />
                </div>
                <div className="rounded-xl border
                  border-white/10 bg-white/5 p-4
                  flex items-center justify-between">
                  <p className="text-sm text-white/80">
                    {result.analysis.combined
                      .recommendation}
                  </p>
                  <DriftBadge
                    level={result.analysis.combined
                      .drift_level}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* MATRIX TAB */}
        {activeTab === "matrix" && matrix && (
          <div className="rounded-xl border
            border-white/10 overflow-hidden">
            <div className="px-4 py-3 bg-white/5
              border-b border-white/10">
              <span className="text-sm font-semibold
                text-white">
                All Environments Matrix
              </span>
            </div>
            <div className="p-4">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="text-left py-2
                      px-3 text-white/40 text-xs
                      font-semibold uppercase">
                      ENV
                    </th>
                    {matrix.environments.map((e) => (
                      <th key={e}
                        className="text-center py-2
                          px-3 text-white/40 text-xs
                          font-semibold uppercase">
                        {e}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y
                  divide-white/5">
                  {matrix.environments.map(
                    (envRow) => (
                    <tr key={envRow}
                      className="hover:bg-white/5">
                      <td className="py-3 px-3
                        font-semibold text-white/70
                        text-xs uppercase">
                        {envRow}
                      </td>
                      {matrix.environments.map(
                        (envCol) => {
                        const cell = matrix.matrix
                          [envRow][envCol];
                        const score =
                          cell.combined_score * 100;
                        return (
                          <td key={envCol}
                            className="py-3 px-3
                              text-center">
                            {envRow === envCol ? (
                              <span className="text-xs
                                text-emerald-400
                                font-mono font-bold">
                                100%
                              </span>
                            ) : (
                              <div className="space-y-1">
                                <div className={`
                                  text-sm font-mono
                                  font-bold
                                  ${score >= 95
                                    ? "text-emerald-400"
                                    : score >= 85
                                    ? "text-blue-400"
                                    : score >= 70
                                    ? "text-amber-400"
                                    : "text-rose-400"
                                  }`}>
                                  {score.toFixed(1)}%
                                </div>
                                <DriftBadge
                                  level={
                                    cell.drift_level
                                  }
                                />
                              </div>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-white/10
        mt-16 py-4">
        <div className="max-w-7xl mx-auto px-6
          flex justify-between text-xs text-white/30">
          <span>DriftLens Deep Analyzer v0.1.0</span>
          <span>
            Auto-refresh every 30s •
            Jaccard(40%) + Cosine(60%)
          </span>
        </div>
      </footer>
    </div>
  );
}
