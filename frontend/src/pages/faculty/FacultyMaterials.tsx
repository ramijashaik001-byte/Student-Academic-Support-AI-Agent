import React, { useState, useEffect } from "react";
import {
  UploadCloud, FileText, CheckCircle2, AlertTriangle,
  RotateCcw, Trash2, Eye, Plus, ShieldCheck, X
} from "lucide-react";
import { apiClient } from "../../api/client";
import type { DocumentItem, Course } from "../../types";

export const FacultyMaterials: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [isUploadOpen, setIsUploadOpen] = useState(false);

  // Form State
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("syllabus");
  const [courseId, setCourseId] = useState<number | undefined>(undefined);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [reindexingId, setReindexingId] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [docRes, crsRes] = await Promise.all([
        apiClient.getDocuments(),
        apiClient.getCourses(),
      ]);
      setDocuments(docRes.data);
      setCourses(crsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title.trim()) {
      setUploadError("Please provide a title and select a valid file.");
      return;
    }

    setUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title.trim());
    formData.append("category", category);
    if (courseId) formData.append("course_id", courseId.toString());
    formData.append("access_level", "all");

    try {
      await apiClient.uploadDocument(formData);
      setIsUploadOpen(false);
      setTitle("");
      setFile(null);
      await loadData();
    } catch (err: any) {
      setUploadError(err.response?.data?.detail || "Upload and text extraction failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleReindex = async (id: number) => {
    setReindexingId(id);
    try {
      await apiClient.reindexDocument(id);
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setReindexingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Archive and remove this document from active AI RAG index?")) return;
    try {
      await apiClient.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Delete failed.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-indigo-600" />
            <span>Course Materials & Knowledge Base Ingestion</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Upload course notes, syllabi, guidelines, and assignment specs. The sentence-aware chunker automatically indexes them into the vector database.
          </p>
        </div>

        <button
          onClick={() => setIsUploadOpen(true)}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Academic Document</span>
        </button>
      </div>

      {/* Documents Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
            All Processed Documents ({documents.length})
          </span>
          <span className="text-[11px] text-slate-500">
            Supported formats: PDF, DOCX, TXT, CSV (Max 25MB)
          </span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading documents...</div>
        ) : documents.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">
            No course materials uploaded yet. Click "Upload Academic Document" to add materials.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100/70 text-slate-600 uppercase text-[10px] font-bold">
                <tr>
                  <th className="p-3.5 pl-6">Title & File</th>
                  <th className="p-3.5">Category</th>
                  <th className="p-3.5">Course Code</th>
                  <th className="p-3.5">Indexed Chunks</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right pr-6">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {documents.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="p-3.5 pl-6">
                      <div className="font-semibold text-slate-900">{d.title}</div>
                      <div className="text-[10px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                        <FileText className="w-3 h-3 text-slate-400" />
                        <span>{d.file_name}</span>
                        <span>·</span>
                        <span>{(d.file_size / 1024).toFixed(1)} KB</span>
                      </div>
                    </td>
                    <td className="p-3.5">
                      <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-[11px] font-medium capitalize">
                        {d.category.replace("_", " ")}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono text-slate-600 font-medium">
                      {d.course_code || "General"}
                    </td>
                    <td className="p-3.5">
                      <span className="font-bold text-slate-800">{d.chunks_count}</span> chunks
                    </td>
                    <td className="p-3.5">
                      {d.status === "indexed" ? (
                        <span className="inline-flex items-center gap-1 bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded-md uppercase">
                          <CheckCircle2 className="w-3 h-3 text-teal-600" /> Indexed
                        </span>
                      ) : d.status === "failed" ? (
                        <span className="inline-flex items-center gap-1 bg-red-100 text-red-800 text-[10px] font-bold px-2 py-0.5 rounded-md uppercase" title={d.error_message}>
                          <AlertTriangle className="w-3 h-3 text-red-600" /> Failed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded-md uppercase animate-pulse">
                          Processing
                        </span>
                      )}
                    </td>
                    <td className="p-3.5 text-right pr-6">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleReindex(d.id)}
                          disabled={reindexingId === d.id}
                          className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                          title="Re-extract and Re-index into Vector Store"
                        >
                          <RotateCcw className={`w-3.5 h-3.5 ${reindexingId === d.id ? "animate-spin" : ""}`} />
                        </button>
                        <button
                          onClick={() => handleDelete(d.id)}
                          className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Archive Document"
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
        )}
      </div>

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 bg-[#2D3139]/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-lg border border-[#E8E6E1] w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="bg-[#FAF9F6] text-[#2D3139] border-b border-[#E8E6E1] px-5 py-4 flex items-center justify-between">
              <h3 className="font-semibold text-sm flex items-center gap-2">
                <UploadCloud className="w-4 h-4 text-[#62826F]" />
                Upload Academic Material
              </h3>
              <button
                onClick={() => setIsUploadOpen(false)}
                className="text-[#6C727F] hover:text-[#2D3139]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpload} className="p-5 space-y-4">
              {uploadError && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                  {uploadError}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Document Title *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. CS301 Lecture Notes on Process Scheduling"
                  className="w-full text-xs border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="syllabus">Course Syllabus</option>
                    <option value="exam_timetable">Exam Timetable</option>
                    <option value="policy">Academic Policy</option>
                    <option value="assignment">Assignment / Project</option>
                    <option value="lecture_notes">Lecture Notes</option>
                    <option value="general">General Guideline</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Applicable Course
                  </label>
                  <select
                    value={courseId || ""}
                    onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : undefined)}
                    className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value="">General / All Courses</option>
                    {courses.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.code} - {c.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  File Upload (.pdf, .docx, .txt, .csv) *
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.csv"
                  onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  required
                />
              </div>

              <div className="p-3 bg-indigo-50/60 border border-indigo-100 rounded-lg text-xs text-indigo-900 flex items-start gap-2">
                <ShieldCheck className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                <span>
                  The file will be scanned, chunked into sentence-aware passages, and stored with vector embeddings for real-time student Q&A grounding.
                </span>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[#E8E6E1]">
                <button
                  type="button"
                  onClick={() => setIsUploadOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-[#4B515D] hover:bg-[#F3F2EE] rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-4 py-2 text-xs font-medium bg-[#5B4F8A] hover:bg-[#4E4377] text-white rounded-lg shadow-xs transition-colors disabled:opacity-50"
                >
                  {uploading ? "Extracting & Indexing..." : "Process & Index"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
