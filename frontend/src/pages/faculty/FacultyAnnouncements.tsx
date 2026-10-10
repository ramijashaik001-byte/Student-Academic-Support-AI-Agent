import React, { useState, useEffect } from "react";
import { BellRing, Plus, Trash2, CheckCircle2, Clock, X } from "lucide-react";
import { apiClient } from "../../api/client";
import type { AnnouncementItem } from "../../types";

export const FacultyAnnouncements: React.FC = () => {
  const [announcements, setAnnouncements] = useState<AnnouncementItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category, setCategory] = useState("academic");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadAnnouncements();
  }, []);

  const loadAnnouncements = async () => {
    try {
      const res = await apiClient.getAnnouncements();
      setAnnouncements(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    setLoading(true);
    try {
      await apiClient.createAnnouncement({
        title: title.trim(),
        content: content.trim(),
        category,
      });
      setIsModalOpen(false);
      setTitle("");
      setContent("");
      await loadAnnouncements();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this announcement?")) return;
    try {
      await apiClient.deleteAnnouncement(id);
      setAnnouncements((prev) => prev.filter((a) => a.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Delete failed.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BellRing className="w-5 h-5 text-indigo-600" />
            <span>Academic Updates & Announcements</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Broadcast official notices and deadlines to students. Automatically generates persistent in-app notifications.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Post New Announcement</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {announcements.map((a) => (
          <div key={a.id} className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-xs space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded">
                  {a.category}
                </span>
                <span className="text-[10px] text-slate-400">
                  {new Date(a.created_at).toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })}
                </span>
              </div>
              <h3 className="font-bold text-sm text-slate-900">{a.title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed mt-2 whitespace-pre-wrap">
                {a.content}
              </p>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Published by {a.author_name}</span>
              <button
                onClick={() => handleDelete(a.id)}
                className="text-slate-400 hover:text-red-600 transition-colors"
                title="Delete announcement"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-[#2D3139]/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-lg border border-[#E8E6E1] w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="bg-[#FAF9F6] text-[#2D3139] border-b border-[#E8E6E1] px-5 py-4 flex items-center justify-between">
              <h3 className="font-semibold text-sm flex items-center gap-2">
                <BellRing className="w-4 h-4 text-[#7C6EB0]" />
                Publish Announcement
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-[#6C727F] hover:text-[#2D3139]">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreate} className="p-5 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#4B515D] mb-1">Title *</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Schedule for Lab Submissions & Demos"
                  className="w-full text-xs border border-[#E2DFD7] rounded-xl px-3 py-2 focus:ring-2 focus:ring-[#7C6EB0] focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#4B515D] mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full text-xs border border-[#E2DFD7] rounded-xl px-2.5 py-2 bg-white focus:ring-2 focus:ring-[#7C6EB0] focus:outline-none"
                >
                  <option value="academic">Academic / Course</option>
                  <option value="exam">Examinations</option>
                  <option value="urgent">Urgent Notice</option>
                  <option value="general">General Campus Update</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#4B515D] mb-1">Announcement Content *</label>
                <textarea
                  rows={4}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="Provide complete academic notice details..."
                  className="w-full text-xs border border-[#E2DFD7] rounded-xl px-3 py-2 focus:ring-2 focus:ring-[#7C6EB0] focus:outline-none resize-none"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-[#E8E6E1]">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium text-[#4B515D] hover:bg-[#F3F2EE] rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 text-xs font-medium bg-[#5B4F8A] hover:bg-[#4E4377] text-white rounded-lg shadow-xs transition-colors disabled:opacity-50"
                >
                  {loading ? "Publishing..." : "Publish & Notify"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
