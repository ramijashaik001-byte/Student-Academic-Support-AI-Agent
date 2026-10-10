import React, { useState, useEffect } from "react";
import {
  LifeBuoy, Plus, MessageSquare, Send, Clock, CheckCircle2,
  AlertTriangle, User, Paperclip, ChevronRight
} from "lucide-react";
import { apiClient } from "../../api/client";
import type { SupportTicket, TicketMessage } from "../../types";
import { EscalateModal } from "../../components/EscalateModal";

export const StudentTickets: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(null);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getTickets();
      setTickets(res.data);
      if (res.data.length > 0 && !selectedTicket) {
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
      // Reload ticket detail
      await loadTicketDetail(selectedTicket.id);
      // Reload tickets list to update counter
      const res = await apiClient.getTickets();
      setTickets(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "resolved":
        return <span className="bg-teal-100 text-teal-800 font-bold px-2.5 py-1 rounded-full text-[10px] uppercase">Resolved</span>;
      case "waiting_for_student":
        return <span className="bg-blue-100 text-blue-800 font-bold px-2.5 py-1 rounded-full text-[10px] uppercase animate-pulse">Faculty Replied</span>;
      case "in_progress":
        return <span className="bg-amber-100 text-amber-800 font-bold px-2.5 py-1 rounded-full text-[10px] uppercase">In Progress</span>;
      default:
        return <span className="bg-slate-100 text-slate-800 font-bold px-2.5 py-1 rounded-full text-[10px] uppercase">Assigned</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <LifeBuoy className="w-5 h-5 text-indigo-600" />
            <span>Academic Support Escalations & Tickets</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Track inquiries escalated to faculty advisors and communicate directly with academic staff.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>New Escalation Ticket</span>
        </button>
      </div>

      {/* Ticket Center Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-13rem)]">
        {/* Left: Tickets List */}
        <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden flex flex-col shadow-xs">
          <div className="p-3.5 bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-700">
            My Inquiries ({tickets.length})
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading tickets...</div>
            ) : tickets.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">
                No tickets submitted yet. Click "New Escalation Ticket" to contact faculty.
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
                      {getStatusBadge(t.status)}
                    </div>
                    <h3 className="font-semibold text-xs text-slate-900 truncate">
                      {t.subject}
                    </h3>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mt-1.5">
                      <span>{t.faculty_name || "Department Advisor"}</span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(t.created_at).toLocaleDateString([], { month: "short", day: "numeric" })}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right: Detailed Conversation Thread */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/80 overflow-hidden flex flex-col shadow-xs">
          {selectedTicket ? (
            <>
              {/* Ticket Top Meta */}
              <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200/60">
                      {selectedTicket.ticket_number}
                    </span>
                    <h2 className="font-bold text-sm text-slate-900">{selectedTicket.subject}</h2>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
                    <span>Course: {selectedTicket.course_name || "General Academic"}</span>
                    <span>·</span>
                    <span>Assigned Faculty: {selectedTicket.faculty_name || "Dean Office"}</span>
                  </div>
                </div>
                <div>{getStatusBadge(selectedTicket.status)}</div>
              </div>

              {/* Message Thread */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-slate-50/30">
                {selectedTicket.messages && selectedTicket.messages.map((m) => {
                  const isStudent = m.sender_role === "student";
                  return (
                    <div
                      key={m.id}
                      className={`flex gap-3 max-w-xl ${isStudent ? "ml-auto justify-end" : "mr-auto"}`}
                    >
                      <div className={`p-4 rounded-2xl text-xs leading-relaxed ${
                        isStudent
                          ? "bg-indigo-600 text-white rounded-tr-xs"
                          : "bg-white border border-slate-200 text-slate-800 rounded-tl-xs shadow-xs"
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

              {/* Reply Box */}
              {selectedTicket.status !== "closed" ? (
                <div className="p-3.5 bg-white border-t border-slate-200">
                  <form onSubmit={handleSendReply} className="flex gap-2">
                    <input
                      type="text"
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Type your response to faculty..."
                      disabled={sending}
                      className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <button
                      type="submit"
                      disabled={sending || !replyText.trim()}
                      className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl text-xs transition-colors disabled:opacity-50 flex items-center gap-1.5"
                    >
                      <span>{sending ? "Sending..." : "Reply"}</span>
                      <Send className="w-3.5 h-3.5" />
                    </button>
                  </form>
                </div>
              ) : (
                <div className="p-3 text-center text-xs text-slate-500 bg-slate-50 border-t border-slate-200">
                  This support ticket is marked as Closed.
                </div>
              )}
            </>
          ) : (
            <div className="h-full flex items-center justify-center p-8 text-center text-slate-400 text-xs">
              Select a ticket to inspect details and faculty responses.
            </div>
          )}
        </div>
      </div>

      <EscalateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={loadTickets}
      />
    </div>
  );
};
