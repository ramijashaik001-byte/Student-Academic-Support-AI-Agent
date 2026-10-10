import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MessageSquare, BookOpen, Calendar, LifeBuoy, ArrowRight,
  Clock, CheckCircle, AlertTriangle, FileText, Send, Sparkles,
  ExternalLink, BellRing, AlertCircle
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { apiClient } from "../../api/client";
import type {
  AcademicSchedule, DocumentItem, Conversation,
  AnnouncementItem, SupportTicket
} from "../../types";
import { EscalateModal } from "../../components/EscalateModal";

export const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [quickQuery, setQuickQuery] = useState("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [schedules, setSchedules] = useState<AcademicSchedule[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [announcements, setAnnouncements] = useState<AnnouncementItem[]>([]);
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEscalateOpen, setIsEscalateOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [convRes, schedRes, docRes, annRes, tickRes] = await Promise.all([
          apiClient.getConversations(),
          apiClient.getSchedules(),
          apiClient.getDocuments(),
          apiClient.getAnnouncements(),
          apiClient.getTickets(),
        ]);
        setConversations(convRes.data);
        setSchedules(schedRes.data);
        setDocuments(docRes.data);
        setAnnouncements(annRes.data);
        setTickets(tickRes.data);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickQuery.trim()) return;
    // Store quick query and navigate to chat
    sessionStorage.setItem("pending_chat_query", quickQuery.trim());
    navigate("/student/chat");
  };

  const upcomingExams = schedules.filter((s) => s.type === "exam").slice(0, 3);
  const upcomingDeadlines = schedules.filter((s) => s.type === "deadline").slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Personalized Welcome Banner */}
      <div className="bg-[#F5F3FF] border border-[#E0D7FA] text-[#2D3139] rounded-2xl p-6 sm:p-8 shadow-xs relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EBE5FC] text-[#5B4F8A] border border-[#DDD6FE] text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" /> AI Academic Support Assistant Active
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2D3139]">
            Welcome back, {user?.full_name}! 👋
          </h1>
          <p className="mt-2 text-[#4B515D] text-sm leading-relaxed">
            I'm your AI academic mentor, grounded in authorized college regulations, exam guidelines, syllabi, and schedules. Ask me any question or browse resources below.
          </p>

          {/* Quick AI Question Input */}
          <form onSubmit={handleQuickSubmit} className="mt-5 flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={quickQuery}
                onChange={(e) => setQuickQuery(e.target.value)}
                placeholder="Ask about attendance rules, exam timetables, CS301 syllabus, lab rules..."
                className="w-full bg-white border border-[#E2DFD7] rounded-xl px-4 py-3 text-sm text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] shadow-xs"
              />
            </div>
            <button
              type="submit"
              className="px-5 py-3 bg-[#5B4F8A] hover:bg-[#4E4377] text-white rounded-xl text-sm font-semibold flex items-center gap-2 shadow-xs transition-colors shrink-0"
            >
              <span>Ask AI</span>
              <Send className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Suggestion Chips */}
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <span className="text-[#6C727F] py-1 font-medium text-[11px]">Popular:</span>
            {[
              "What is the 75% attendance rule?",
              "When are my mid-semester exams?",
              "CS301 project submission deadline",
              "How to apply for medical condonation?",
            ].map((chip) => (
              <button
                key={chip}
                onClick={() => {
                  sessionStorage.setItem("pending_chat_query", chip);
                  navigate("/student/chat");
                }}
                className="px-2.5 py-1 rounded-lg bg-white hover:bg-[#FAF9F6] text-[#4B515D] hover:text-[#2D3139] border border-[#E2DFD7] text-[11px] transition-colors shadow-xs"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Quick Actions Row */}
          <div className="grid grid-cols-3 gap-3">
            <Link
              to="/student/chat"
              className="p-4 bg-white rounded-xl border border-[#E8E6E1] shadow-xs hover:border-[#DDD6FE] transition-all group"
            >
              <div className="w-9 h-9 rounded-lg bg-[#F5F3FF] text-[#5B4F8A] flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <MessageSquare className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-xs text-[#2D3139]">Academic Chat</h3>
              <p className="text-[11px] text-[#6C727F] mt-0.5">Ask questions with citations</p>
            </Link>

            <Link
              to="/student/knowledge-base"
              className="p-4 bg-white rounded-xl border border-[#E8E6E1] shadow-xs hover:border-[#D1E3D7] transition-all group"
            >
              <div className="w-9 h-9 rounded-lg bg-[#F0F5F2] text-[#466352] flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <BookOpen className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-xs text-[#2D3139]">College Documents</h3>
              <p className="text-[11px] text-[#6C727F] mt-0.5">Explore syllabi & policies</p>
            </Link>

            <button
              onClick={() => setIsEscalateOpen(true)}
              className="text-left p-4 bg-white rounded-xl border border-[#E8E6E1] shadow-xs hover:border-[#E8DFD1] transition-all group"
            >
              <div className="w-9 h-9 rounded-lg bg-[#FDF6E9] text-[#B47C57] flex items-center justify-center mb-2 group-hover:scale-105 transition-transform">
                <LifeBuoy className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-xs text-[#2D3139]">Contact Faculty</h3>
              <p className="text-[11px] text-[#6C727F] mt-0.5">Escalate unresolved queries</p>
            </button>
          </div>

          {/* Upcoming Examinations Card */}
          <div className="bg-white rounded-xl border border-[#E8E6E1] p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-[#7C6EB0]" />
                <h3 className="font-bold text-sm text-[#2D3139]">Upcoming Verified Examinations</h3>
              </div>
              <Link to="/student/schedules" className="text-xs text-[#5B4F8A] hover:underline flex items-center gap-1 font-medium">
                View Timetable <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {upcomingExams.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#6C727F] bg-[#FAF9F6] rounded-lg">
                No examination dates currently published in verified schedules.
              </div>
            ) : (
              <div className="space-y-2.5">
                {upcomingExams.map((ex) => (
                  <div key={ex.id} className="p-3 bg-[#FAF9F6] border border-[#E8E6E1] rounded-lg flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-xs text-[#2D3139]">{ex.title}</div>
                      <div className="text-[11px] text-[#6C727F] flex items-center gap-2 mt-0.5">
                        <span>Venue: {ex.venue || "Hall A"}</span>
                        <span>·</span>
                        <span>{ex.start_time} - {ex.end_time}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="inline-block bg-[#F5F3FF] text-[#5B4F8A] border border-[#DDD6FE] text-[11px] font-bold px-2 py-0.5 rounded-md">
                        {ex.date}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Upcoming Assignment Deadlines Card */}
          <div className="bg-white rounded-xl border border-[#E8E6E1] p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-[#B47C57]" />
                <h3 className="font-bold text-sm text-[#2D3139]">Upcoming Assignment Deadlines</h3>
              </div>
              <Link to="/student/schedules" className="text-xs text-[#B47C57] hover:underline flex items-center gap-1 font-medium">
                All Deadlines <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {upcomingDeadlines.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#6C727F] bg-[#FAF9F6] rounded-lg">
                No active assignment deadlines reported.
              </div>
            ) : (
              <div className="space-y-2.5">
                {upcomingDeadlines.map((dl) => (
                  <div key={dl.id} className="p-3 bg-[#FAF9F6] border border-[#E8E6E1] rounded-lg flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-xs text-[#2D3139]">{dl.title}</div>
                      <div className="text-[11px] text-[#6C727F] mt-0.5">{dl.details}</div>
                    </div>
                    <div className="text-right shrink-0 ml-3">
                      <span className="inline-block bg-[#FDF6E9] text-[#8C5D35] border border-[#E8DFD1] text-[11px] font-bold px-2 py-0.5 rounded-md">
                        Due {dl.date}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Conversations */}
          <div className="bg-white rounded-xl border border-[#E8E6E1] p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-[#62826F]" />
                <h3 className="font-bold text-sm text-[#2D3139]">Recent Conversations</h3>
              </div>
              <Link to="/student/chat" className="text-xs text-[#62826F] hover:underline flex items-center gap-1 font-medium">
                Continue Chat <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {conversations.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#6C727F] bg-[#FAF9F6] rounded-lg">
                No past chat history. Start a new question using the prompt above!
              </div>
            ) : (
              <div className="space-y-2">
                {conversations.slice(0, 4).map((c) => (
                  <Link
                    key={c.id}
                    to={`/student/chat?id=${c.id}`}
                    className="p-3 rounded-lg border border-[#E8E6E1] hover:border-[#DDD6FE] hover:bg-[#F5F3FF]/30 transition-all flex items-center justify-between block group"
                  >
                    <div>
                      <div className="text-xs font-semibold text-[#2D3139] group-hover:text-[#5B4F8A]">
                        {c.title}
                      </div>
                      <div className="text-[11px] text-[#6C727F] mt-0.5">
                        {c.last_message || "Active conversation thread"}
                      </div>
                    </div>
                    <span className="text-[10px] text-[#9CA3AF] shrink-0">
                      {new Date(c.updated_at).toLocaleDateString([], { month: "short", day: "numeric" })}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column (1 Col) */}
        <div className="space-y-6">
          {/* Institutional Announcements */}
          <div className="bg-white rounded-xl border border-[#E8E6E1] p-5 shadow-xs">
            <div className="flex items-center gap-2 mb-4">
              <BellRing className="w-4 h-4 text-[#7C6EB0]" />
              <h3 className="font-bold text-sm text-[#2D3139]">College Announcements</h3>
            </div>

            {announcements.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#6C727F] bg-[#FAF9F6] rounded-lg">
                No new announcements published.
              </div>
            ) : (
              <div className="space-y-3">
                {announcements.slice(0, 4).map((a) => (
                  <div key={a.id} className="p-3 rounded-lg bg-[#FAF9F6] border border-[#E8E6E1] text-xs">
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="font-semibold text-[#2D3139]">{a.title}</span>
                      <span className="text-[9px] uppercase tracking-wider font-bold bg-[#EBE5FC] text-[#5B4F8A] px-1.5 py-0.5 rounded border border-[#DDD6FE]">
                        {a.category}
                      </span>
                    </div>
                    <p className="text-[#4B515D] text-[11px] leading-relaxed">
                      {a.content}
                    </p>
                    <div className="text-[10px] text-[#9CA3AF] mt-2 font-medium">
                      By {a.author_name}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active Support Tickets */}
          <div className="bg-white rounded-xl border border-[#E8E6E1] p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <LifeBuoy className="w-4 h-4 text-[#62826F]" />
                <h3 className="font-bold text-sm text-[#2D3139]">My Support Tickets</h3>
              </div>
              <Link to="/student/tickets" className="text-xs text-[#62826F] hover:underline flex items-center gap-1 font-medium">
                View All <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {tickets.length === 0 ? (
              <div className="p-6 text-center text-xs text-[#6C727F] bg-[#FAF9F6] rounded-lg">
                No active tickets. Need help from a professor? Click "Contact Faculty".
              </div>
            ) : (
              <div className="space-y-2.5">
                {tickets.slice(0, 3).map((t) => (
                  <Link
                    key={t.id}
                    to="/student/tickets"
                    className="p-3 rounded-lg bg-[#FAF9F6] border border-[#E8E6E1] block hover:border-[#DDD6FE] transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono text-[10px] font-bold text-[#5B4F8A]">
                        {t.ticket_number}
                      </span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded capitalize ${
                        t.status === "resolved" ? "bg-[#E2EBE5] text-[#344E41] border border-[#D1E0D7]" :
                        t.status === "waiting_for_student" ? "bg-[#E1EDF8] text-[#2B4C6F] border border-[#CEE3F5] font-bold" :
                        "bg-[#FDF6E9] text-[#8C5D35] border border-[#E8DFD1]"
                      }`}>
                        {t.status.replace("_", " ")}
                      </span>
                    </div>
                    <div className="font-semibold text-xs text-[#2D3139] truncate">
                      {t.subject}
                    </div>
                    <div className="text-[11px] text-[#6C727F] mt-0.5 truncate">
                      {t.faculty_name ? `Assigned to: ${t.faculty_name}` : "Pending assignment"}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>

          {/* Recommended Course Materials */}
          <div className="bg-white rounded-xl border border-[#E8E6E1] p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-[#7C6EB0]" />
                <h3 className="font-bold text-sm text-[#2D3139]">Recommended Documents</h3>
              </div>
              <Link to="/student/knowledge-base" className="text-xs text-[#7C6EB0] hover:underline flex items-center gap-1 font-medium">
                Browse <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="space-y-2">
              {documents.slice(0, 4).map((d) => (
                <div key={d.id} className="p-2.5 rounded-lg border border-[#E8E6E1] bg-[#FAF9F6] flex items-center justify-between text-xs">
                  <div className="truncate pr-2">
                    <div className="font-medium text-[#2D3139] truncate">{d.title}</div>
                    <div className="text-[10px] text-[#6C727F] capitalize">{d.category.replace("_", " ")} · {d.file_type.toUpperCase()}</div>
                  </div>
                  <span className="text-[10px] font-bold text-[#344E41] bg-[#E2EBE5] px-2 py-0.5 rounded border border-[#D1E0D7] shrink-0">
                    Verified
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Escalate Modal */}
      <EscalateModal
        isOpen={isEscalateOpen}
        onClose={() => setIsEscalateOpen(false)}
        onSuccess={() => apiClient.getTickets().then((res) => setTickets(res.data))}
      />
    </div>
  );
};
