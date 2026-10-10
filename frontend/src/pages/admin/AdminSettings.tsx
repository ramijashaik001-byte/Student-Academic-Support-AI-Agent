import React, { useState, useEffect } from "react";
import { Settings, Save, CheckCircle2, ShieldCheck, Key, Cpu } from "lucide-react";
import { apiClient } from "../../api/client";

export const AdminSettings: React.FC = () => {
  const [llmProvider, setLlmProvider] = useState("local_fallback");
  const [modelName, setModelName] = useState("gemini-1.5-flash");
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [openaiApiKey, setOpenaiApiKey] = useState("");
  const [chunkSize, setChunkSize] = useState(550);
  const [retrievalTopK, setRetrievalTopK] = useState(4);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.40);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(false);

  useEffect(() => {
    apiClient.getSettings().then((res) => {
      setLlmProvider(res.data.llm_provider || "local_fallback");
      setModelName(res.data.model_name || "gemini-1.5-flash");
      setChunkSize(res.data.chunk_size || 550);
      setRetrievalTopK(res.data.retrieval_top_k || 4);
      setConfidenceThreshold(res.data.confidence_threshold || 0.40);
    }).catch(() => {});
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedMsg(false);
    try {
      await apiClient.updateSettings({
        llm_provider: llmProvider,
        model_name: modelName,
        gemini_api_key: geminiApiKey ? geminiApiKey : undefined,
        openai_api_key: openaiApiKey ? openaiApiKey : undefined,
        chunk_size: chunkSize,
        retrieval_top_k: retrievalTopK,
        confidence_threshold: confidenceThreshold,
      });
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <Settings className="w-5 h-5 text-indigo-600" />
          <span>AI Engine & RAG Configuration</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Configure external LLM providers or utilize the zero-cost deterministic academic mentor engine.
        </p>
      </div>

      {savedMsg && (
        <div className="p-3.5 bg-teal-50 border border-teal-200 text-teal-800 text-xs rounded-xl flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
          <span>AI engine parameters updated successfully!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-6">
        <div>
          <label className="block text-xs font-bold text-slate-800 mb-1 flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-indigo-600" />
            <span>Generation & Intelligence Engine</span>
          </label>
          <select
            value={llmProvider}
            onChange={(e) => setLlmProvider(e.target.value)}
            className="w-full text-xs bg-slate-50 border border-slate-300 rounded-xl px-3 py-2.5 font-medium focus:ring-2 focus:ring-indigo-500"
          >
            <option value="local_fallback">
              Deterministic Academic Mentor Fallback (100% Offline / Zero-Cost)
            </option>
            <option value="gemini">Google Gemini 1.5 Flash (Cloud API)</option>
            <option value="openai">OpenAI GPT-4o-mini (Cloud API)</option>
          </select>
          <p className="text-[11px] text-slate-400 mt-1">
            Deterministic fallback generates humanized, strictly grounded responses directly from verified chunks without requiring external API keys.
          </p>
        </div>

        {llmProvider === "gemini" && (
          <div>
            <label className="block text-xs font-bold text-slate-800 mb-1 flex items-center gap-1.5">
              <Key className="w-4 h-4 text-teal-600" />
              <span>Google Gemini API Key</span>
            </label>
            <input
              type="password"
              value={geminiApiKey}
              onChange={(e) => setGeminiApiKey(e.target.value)}
              placeholder="AIzaSy... (Keep blank to preserve server env value)"
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono focus:ring-2 focus:ring-teal-500"
            />
          </div>
        )}

        {llmProvider === "openai" && (
          <div>
            <label className="block text-xs font-bold text-slate-800 mb-1 flex items-center gap-1.5">
              <Key className="w-4 h-4 text-purple-600" />
              <span>OpenAI API Key</span>
            </label>
            <input
              type="password"
              value={openaiApiKey}
              onChange={(e) => setOpenaiApiKey(e.target.value)}
              placeholder="sk-... (Keep blank to preserve server env value)"
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 font-mono focus:ring-2 focus:ring-purple-500"
            />
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-100">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Sentence Chunk Target Size
            </label>
            <input
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[10px] text-slate-400">Characters per chunk</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Retrieval Top-K
            </label>
            <input
              type="number"
              value={retrievalTopK}
              onChange={(e) => setRetrievalTopK(Number(e.target.value))}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[10px] text-slate-400">Number of chunks in prompt</span>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Escalation Threshold
            </label>
            <input
              type="number"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(Number(e.target.value))}
              className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-[10px] text-slate-400">Trigger faculty escalation below</span>
          </div>
        </div>

        <div className="flex justify-end pt-3">
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-1.5 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            <span>{saving ? "Updating..." : "Save AI Engine Settings"}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
