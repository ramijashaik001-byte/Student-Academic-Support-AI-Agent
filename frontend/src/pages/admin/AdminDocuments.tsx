import React, { useState, useEffect } from "react";
import { Database, RotateCcw, Trash2, CheckCircle2, AlertTriangle, FileText, Plus } from "lucide-react";
import { apiClient } from "../../api/client";
import type { DocumentItem } from "../../types";

export const AdminDocuments: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [reindexingId, setReindexingId] = useState<number | null>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getDocuments();
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReindex = async (id: number) => {
    setReindexingId(id);
    try {
      await apiClient.reindexDocument(id);
      await loadDocs();
    } catch (err) {
      console.error(err);
    } finally {
      setReindexingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Permanently archive and de-index this document from the AI knowledge base?")) return;
    try {
      await apiClient.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Delete failed.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-600" />
            <span>Document Master & Vector Knowledge Base</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Complete inventory of authorized college documents, sentence chunks, and vector store indices.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-bold">
              <tr>
                <th className="p-3.5 pl-6">Document Title</th>
                <th className="p-3.5">Category</th>
                <th className="p-3.5">Type & Size</th>
                <th className="p-3.5">Chunks</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right pr-6">Management</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {documents.map((d) => (
                <tr key={d.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="p-3.5 pl-6">
                    <div className="font-semibold text-slate-900">{d.title}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{d.file_name}</div>
                  </td>
                  <td className="p-3.5 capitalize font-medium text-slate-700">
                    {d.category.replace("_", " ")}
                  </td>
                  <td className="p-3.5 text-slate-500">
                    {d.file_type.toUpperCase()} ({(d.file_size / 1024).toFixed(1)} KB)
                  </td>
                  <td className="p-3.5 font-bold text-indigo-600">
                    {d.chunks_count} chunks
                  </td>
                  <td className="p-3.5">
                    <span className="inline-flex items-center gap-1 bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                      <CheckCircle2 className="w-3 h-3 text-teal-600" /> {d.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-right pr-6">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleReindex(d.id)}
                        disabled={reindexingId === d.id}
                        className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        title="Re-index document"
                      >
                        <RotateCcw className={`w-3.5 h-3.5 ${reindexingId === d.id ? "animate-spin" : ""}`} />
                      </button>
                      <button
                        onClick={() => handleDelete(d.id)}
                        className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="De-index document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
