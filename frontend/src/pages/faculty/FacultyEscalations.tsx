import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  LifeBuoy, Send, CheckCircle2, Clock, AlertTriangle,
  User, Check, Filter, Search
} from "lucide-react";
import { apiClient } from "../../api/client";
import type { SupportTicket } from "../../types";

export const FacultyEscalations: React.FC = () => {
  const [searchParams] = useSearchParams();
  const urlTicketId = searchParams.get("id");

  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  const [replyText, setReplyText] = useState("");
  const [newStatus, setNewStatus] = useState<string>("resolved");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTickets();
  }, [statusFilter]);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const params = statusFilter !== "all" ? { status_filter: statusFilter } : undefined;
      const res = await apiClient.getTickets(params);
      setTickets(res.data);

      if (urlTicketId) {
        const found = res.data.find((t) => t.id === Number(urlTicketId));
        if (found) loadTicketDetail(found.id);
        else if (res.data.length > 0) loadTicketDetail(res.data[0].id);
      } else if (res.data.length > 0 && !selectedTicket) {
        loadTicketDetail(res.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadTicketDetail = async (id: number) => {
    try {
      const res = await apiClient.getTicket(id);
      setSelectedTicket(res.data);
      setNewStatus(res.data.status);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyText.trim() || !selectedTicket || sending) return;

    setSending(true);
    try {
      await apiClient.sendTicketMessage(selectedTicket.id, { message: replyText.trim() });
      setReplyText("");
      await loadTicketDetail(selectedTicket.id);
      const res = await apiClient.getTickets();
      setTickets(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const handleUpdateStatus = async (status: string) => {
    if (!selectedTicket) return;
    try {
      const res = await apiClient.updateTicketStatus(selectedTicket.id, status);
      setSelectedTicket(res.data);
      setTickets((prev) => prev.map((t) => (t.id === res.data.id ? res.data : t)));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <LifeBuoy className="w-5 h-5 text-indigo-600" />
            <span>Escalated Academic Queries Inbox</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Student questions that were either unaddressed by standard documents or requested human faculty guidance.
          </p>
        </div>

        {/* Status Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Ticket Statuses</option>
            <option value="open">Open / Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="waiting_for_student">Waiting for Student</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-13rem)]">
        {/* Tickets List */}
        <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden flex flex-col shadow-xs">
          <div className="p-3.5 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-700">
            Escalation Inbox ({tickets.length})
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading inbox...</div>
            ) : tickets.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">
                No escalated tickets matching this filter.
              </div>
            ) : (
              tickets.map((t) => {
                const isSelected = selectedTicket?.id === t.id;
                return (
                  <div
                    key={t.id}
                    onClick={() => loadTicketDetail(t.id)}
                    className={`p-3.5 cursor-pointer transition-all ${
                      isSelected ? "bg-indigo-50/70 border-l-4 border-l-indigo-600" : "hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-mono text-[10px] font-bold text-indigo-700">
                        {t.ticket_number}
                      </span>
                      <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                        t.priority === "urgent" ? "bg-red-100 text-red-800" :
                        t.priority === "high" ? "bg-amber-100 text-amber-800" :
                        "bg-slate-100 text-slate-700"
                      }`}>
                        {t.priority}
                      </span>
                    </div>

                    <h4 className="font-semibold text-xs text-slate-900 truncate">
                      {t.subject}
                    </h4>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1">
                      <span>{t.student_name}</span>
                      <span className="capitalize text-[10px] bg-slate-100 px-1.5 py-0.2 rounded font-medium">
                        {t.status.replace("_", " ")}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Ticket Resolution & Chat Thread */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/80 overflow-hidden flex flex-col shadow-xs">
          {selectedTicket ? (
            <>
              {/* Top Details & Status Actions */}
              <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-indigo-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {selectedTicket.ticket_number}
                    </span>
                    <h2 className="font-bold text-sm text-slate-900">{selectedTicket.subject}</h2>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">
                    Student: <span className="font-semibold text-slate-700">{selectedTicket.student_name}</span> (Roll: {selectedTicket.student_roll || "2026-CS-101"})
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 font-medium">Status:</span>
                  <select
                    value={selectedTicket.status}
                    onChange={(e) => handleUpdateStatus(e.target.value)}
                    className="text-xs bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 font-semibold focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="assigned">Assigned</option>
                    <option value="in_progress">In Progress</option>
                    <option value="waiting_for_student">Waiting for Student</option>
                    <option value="resolved">Mark Resolved</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
              </div>

              {/* Message Thread */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50/30">
                {selectedTicket.messages && selectedTicket.messages.map((m) => {
                  const isFaculty = m.sender_role === "faculty" || m.sender_role === "admin";
                  return (
                    <div
                      key={m.id}
                      className={`flex gap-3 max-w-xl ${isFaculty ? "ml-auto justify-end" : "mr-auto"}`}
                    >
                      <div className={`p-4 rounded-2xl text-xs leading-relaxed ${
                        isFaculty
                          ? "bg-[#5B4F8A] text-white rounded-tr-xs"
                          : "bg-white border border-[#E8E6E1] text-[#2D3139] rounded-tl-xs shadow-xs"
                      }`}>
                        <div className="flex items-center justify-between gap-3 text-[10px] mb-1 font-semibold opacity-80">
                          <span>{m.sender_name} ({m.sender_role.toUpperCase()})</span>
                          <span>
                            {new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                          </span>
                        </div>
                        <p className="whitespace-pre-wrap">{m.message}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Faculty Response Composer */}
              <div className="p-3.5 bg-white border-t border-[#E8E6E1] space-y-2">
                <form onSubmit={handleSendReply} className="flex gap-2">
                  <input
                    type="text"
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Type official faculty guidance or response to student..."
                    disabled={sending}
                    className="flex-1 bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl px-4 py-2.5 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0]"
                  />
                  <button
                    type="submit"
                    disabled={sending || !replyText.trim()}
                    className="px-5 py-2.5 bg-[#5B4F8A] hover:bg-[#4E4377] text-white font-medium rounded-xl text-xs transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-xs"
                  >
                    <span>{sending ? "Sending..." : "Send Response"}</span>
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </form>
                <div className="text-[10px] text-slate-400 flex items-center justify-between">
                  <span>Student will receive an instant persistent in-app notification upon response.</span>
                </div>
              </div>
            </>
          ) : (
            <div className="h-full flex items-center justify-center p-8 text-center text-slate-400 text-xs">
              Select an escalated student ticket from the inbox to reply.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
