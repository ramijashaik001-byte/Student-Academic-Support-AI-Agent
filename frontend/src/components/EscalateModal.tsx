import React, { useState, useEffect } from "react";
import { X, Send, AlertTriangle, CheckCircle2 } from "lucide-react";
import { apiClient } from "../api/client";
import type { Course } from "../types";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  initialSubject?: string;
  initialDescription?: string;
  conversationId?: number;
  onSuccess?: () => void;
}

export const EscalateModal: React.FC<Props> = ({
  isOpen,
  onClose,
  initialSubject = "",
  initialDescription = "",
  conversationId,
  onSuccess,
}) => {
  const [subject, setSubject] = useState(initialSubject);
  const [description, setDescription] = useState(initialDescription);
  const [courseId, setCourseId] = useState<number | undefined>(undefined);
  const [priority, setPriority] = useState<"low" | "medium" | "high" | "urgent">("medium");
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successTicketNumber, setSuccessTicketNumber] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setSubject(initialSubject);
      setDescription(initialDescription);
      setSuccessTicketNumber(null);
      setError(null);
      apiClient.getCourses().then((res) => setCourses(res.data)).catch(() => {});
    }
  }, [isOpen, initialSubject, initialDescription]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !description.trim()) {
      setError("Please fill in both the subject and detailed query.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await apiClient.createTicket({
        subject: subject.trim(),
        description: description.trim(),
        priority,
        course_id: courseId || undefined,
        conversation_id: conversationId || undefined,
      });

      setSuccessTicketNumber(res.data.ticket_number);
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit escalation ticket.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-[#2D3139]/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg border border-[#E8E6E1] w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        <div className="bg-[#FAF9F6] border-b border-[#E8E6E1] text-[#2D3139] px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-[#B47C57]" />
            <h3 className="font-semibold text-base">Escalate Query to Faculty</h3>
          </div>
          <button
            onClick={onClose}
            className="text-[#6C727F] hover:text-[#2D3139] p-1 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {successTicketNumber ? (
          <div className="p-6 text-center space-y-4">
            <div className="w-12 h-12 bg-[#E2EBE5] text-[#344E41] rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-[#2D3139]">Ticket Created Successfully!</h4>
              <p className="text-[#4B515D] text-sm mt-1">
                Your ticket <span className="font-mono font-bold text-[#5B4F8A]">{successTicketNumber}</span> has been
                routed to the course faculty and academic advisor.
              </p>
            </div>
            <div className="bg-[#FAF9F6] p-3 rounded-lg border border-[#E8E6E1] text-xs text-[#6C727F]">
              You will receive an in-app notification as soon as the faculty member reviews and responds to your query.
            </div>
            <div className="pt-2">
              <button
                onClick={onClose}
                className="w-full bg-[#5B4F8A] hover:bg-[#4E4377] text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Close & Track in My Tickets
              </button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4">
            {error && (
              <div className="p-3 text-xs bg-red-50 text-red-700 border border-red-200 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Subject / Query Title *
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Attendance discrepancy or exam schedule clash"
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Related Course (Optional)
                </label>
                <select
                  value={courseId || ""}
                  onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">General / All Courses</option>
                  {courses.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.code} - {c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Urgency Level
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  className="w-full text-xs border border-slate-300 rounded-lg px-2.5 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="low">Low (General guidance)</option>
                  <option value="medium">Medium (Standard query)</option>
                  <option value="high">High (Urgent policy/exam issue)</option>
                  <option value="urgent">Urgent (Immediate deadline)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Detailed Explanation *
              </label>
              <textarea
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Explain what specific academic guidance or manual resolution you need..."
                className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                required
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-[#E8E6E1]">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-medium text-[#4B515D] hover:bg-[#F3F2EE] rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-medium bg-[#5B4F8A] hover:bg-[#4E4377] text-white rounded-lg shadow-xs transition-colors disabled:opacity-60"
              >
                <Send className="w-3.5 h-3.5" />
                {loading ? "Submitting..." : "Send to Faculty"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
