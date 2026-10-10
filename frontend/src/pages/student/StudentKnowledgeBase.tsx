import React, { useState, useEffect } from "react";
import {
  BookOpen, Search, Filter, FileText, CheckCircle2,
  Calendar, Layers, Download, Eye, ExternalLink
} from "lucide-react";
import { apiClient } from "../../api/client";
import type { DocumentItem } from "../../types";

export const StudentKnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);

  useEffect(() => {
    loadDocuments();
  }, [selectedCategory]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const params = selectedCategory !== "all" ? { category: selectedCategory } : undefined;
      const res = await apiClient.getDocuments(params);
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: "all", label: "All Materials" },
    { id: "policy", label: "Academic Policies & Rules" },
    { id: "exam_timetable", label: "Exam Timetables & Schedules" },
    { id: "syllabus", label: "Course Syllabi & Guides" },
    { id: "general", label: "General Guidelines" },
  ];

  const filteredDocs = documents.filter((d) =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (d.course_code && d.course_code.toLowerCase().includes(searchQuery.toLowerCase())) ||
    d.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-indigo-600" />
            <span>Authorized Academic Knowledge Base</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse verified institutional syllabi, examination timetables, grading policies, and course guidelines.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by title, subject, code..."
            className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap gap-2">
        {categories.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelectedCategory(c.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedCategory === c.id
                ? "bg-indigo-600 text-white shadow-xs font-semibold"
                : "bg-white text-slate-700 hover:bg-slate-100 border border-slate-200/80"
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {/* Document Grid */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500 bg-white rounded-2xl border border-slate-200">
          Loading authorized academic documents...
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="p-12 text-center text-xs text-slate-400 bg-white rounded-2xl border border-slate-200">
          No documents found matching your filter criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocs.map((doc) => (
            <div
              key={doc.id}
              className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs hover:border-indigo-300 hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200/60">
                    {doc.category.replace("_", " ")}
                  </span>
                  <span className="flex items-center gap-1 text-[10px] text-teal-700 font-bold bg-teal-50 px-2 py-0.5 rounded-md border border-teal-200/60">
                    <CheckCircle2 className="w-3 h-3 text-teal-600" />
                    Verified
                  </span>
                </div>

                <h3 className="font-bold text-sm text-slate-900 leading-snug line-clamp-2">
                  {doc.title}
                </h3>

                <div className="mt-3 space-y-1.5 text-xs text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                    <span>File: {doc.file_name} ({doc.file_type.toUpperCase()})</span>
                  </div>
                  {doc.course_code && (
                    <div className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-slate-400" />
                      <span>Course: {doc.course_code}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span>Academic Year: {doc.academic_year}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="text-slate-400">
                  {doc.chunks_count} indexed chunks
                </span>
                <button
                  onClick={() => setSelectedDoc(doc)}
                  className="text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1"
                >
                  <Eye className="w-3.5 h-3.5" />
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Document Details Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 bg-[#2D3139]/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-lg border border-[#E8E6E1] w-full max-w-lg p-6 space-y-4 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] uppercase font-bold text-[#5B4F8A] bg-[#EBE5FC] border border-[#DDD6FE] px-2 py-0.5 rounded">
                  {selectedDoc.category.replace("_", " ")}
                </span>
                <h3 className="text-base font-bold text-[#2D3139] mt-1">
                  {selectedDoc.title}
                </h3>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="text-[#6C727F] hover:text-[#2D3139] text-lg font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className="bg-[#FAF9F6] p-3.5 rounded-lg border border-[#E8E6E1] text-xs space-y-2 text-[#4B515D]">
              <div><span className="font-semibold text-[#2D3139]">File Name:</span> {selectedDoc.file_name}</div>
              <div><span className="font-semibold text-[#2D3139]">Format:</span> {selectedDoc.file_type.toUpperCase()}</div>
              <div><span className="font-semibold text-[#2D3139]">Uploaded By:</span> {selectedDoc.uploader_name}</div>
              <div><span className="font-semibold text-[#2D3139]">Status:</span> {selectedDoc.status.toUpperCase()}</div>
              <div><span className="font-semibold text-[#2D3139]">Indexed Chunks:</span> {selectedDoc.chunks_count}</div>
              <div><span className="font-semibold text-[#2D3139]">Last Updated:</span> {new Date(selectedDoc.updated_at).toLocaleDateString()}</div>
            </div>

            <div className="p-3 bg-[#F0F5F2] border border-[#D1E0D7] rounded-lg text-xs text-[#344E41]">
              💡 <strong>RAG Verification:</strong> This document is actively embedded in the college vector database and used by the AI assistant for verified factual retrieval.
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 bg-[#5B4F8A] hover:bg-[#4E4377] text-white text-xs font-semibold rounded-lg shadow-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
