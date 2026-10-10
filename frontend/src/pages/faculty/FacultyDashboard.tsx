import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Layers, UploadCloud, LifeBuoy, BellRing, ArrowRight,
  CheckCircle2, Clock, FileText, AlertTriangle, Users
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { apiClient } from "../../api/client";
import type { SupportTicket, DocumentItem, Course } from "../../types";

export const FacultyDashboard: React.FC = () => {
  const { user } = useAuth();
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [tickRes, docRes, crsRes] = await Promise.all([
          apiClient.getTickets(),
          apiClient.getDocuments(),
          apiClient.getCourses(),
        ]);
        setTickets(tickRes.data);
        setDocuments(docRes.data);
        setCourses(crsRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const openTickets = tickets.filter((t) => t.status !== "resolved" && t.status !== "closed");

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-[#F5F3FF] border border-[#E0D7FA] text-[#2D3139] rounded-2xl p-6 sm:p-8 shadow-xs">
        <div className="max-w-3xl">
          <span className="bg-[#EBE5FC] text-[#5B4F8A] text-xs font-bold px-3 py-1 rounded-full border border-[#DDD6FE] uppercase tracking-wider inline-block mb-3">
            Faculty Academic Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2D3139]">
            Welcome, {user?.full_name}
          </h1>
          <p className="mt-2 text-[#4B515D] text-sm leading-relaxed">
            Manage course materials, review student queries escalated by the AI assistant, and publish academic announcements.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Pending Escalations</span>
            <LifeBuoy className="w-5 h-5 text-[#B47C57]" />
          </div>
          <div className="text-3xl font-bold text-[#B47C57]">{openTickets.length}</div>
          <div className="text-[11px] text-[#B47C57] font-medium mt-1">Requires faculty review or reply</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Course Materials</span>
            <UploadCloud className="w-5 h-5 text-[#62826F]" />
          </div>
          <div className="text-3xl font-bold text-[#2D3139]">{documents.length}</div>
          <div className="text-[11px] text-[#62826F] font-medium mt-1">Active indexed knowledge files</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Active Courses</span>
            <Layers className="w-5 h-5 text-[#7C6EB0]" />
          </div>
          <div className="text-3xl font-bold text-[#2D3139]">{courses.length}</div>
          <div className="text-[11px] text-[#7C6EB0] font-medium mt-1">Under Computer Science Dept.</div>
        </div>
      </div>

      {/* Two Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Escalated Queries Inbox Preview */}
        <div className="bg-white rounded-2xl border border-[#E8E6E1] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <LifeBuoy className="w-4 h-4 text-[#B47C57]" />
              <h3 className="font-bold text-sm text-[#2D3139]">Student Escalations Inbox</h3>
            </div>
            <Link to="/faculty/escalations" className="text-xs text-[#5B4F8A] hover:underline flex items-center gap-1 font-medium">
              View Inbox <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {openTickets.length === 0 ? (
            <div className="p-8 text-center text-xs text-[#6C727F] bg-[#FAF9F6] rounded-xl">
              No pending escalated student tickets at this time.
            </div>
          ) : (
            <div className="space-y-3">
              {openTickets.slice(0, 4).map((t) => (
                <Link
                  key={t.id}
                  to={`/faculty/escalations?id=${t.id}`}
                  className="p-3.5 rounded-xl border border-[#E8E6E1] hover:border-[#DDD6FE] hover:bg-[#F5F3FF]/30 transition-all block group"
                >
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="font-mono text-[10px] font-bold text-[#5B4F8A]">
                      {t.ticket_number}
                    </span>
                    <span className="text-[10px] font-bold uppercase bg-[#FDF6E9] text-[#8C5D35] border border-[#E8DFD1] px-2 py-0.5 rounded-md">
                      {t.priority}
                    </span>
                  </div>
                  <h4 className="font-semibold text-xs text-[#2D3139] group-hover:text-[#5B4F8A] truncate">
                    {t.subject}
                  </h4>
                  <div className="text-[11px] text-[#6C727F] mt-1 flex items-center justify-between">
                    <span>Student: {t.student_name} ({t.student_roll || "N/A"})</span>
                    <span className="text-[10px] text-[#9CA3AF]">
                      {new Date(t.created_at).toLocaleDateString([], { month: "short", day: "numeric" })}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recently Uploaded Documents Preview */}
        <div className="bg-white rounded-2xl border border-[#E8E6E1] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-[#62826F]" />
              <h3 className="font-bold text-sm text-[#2D3139]">Knowledge Base Materials</h3>
            </div>
            <Link to="/faculty/materials" className="text-xs text-[#62826F] hover:underline flex items-center gap-1 font-medium">
              Upload New <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-2.5">
            {documents.slice(0, 4).map((d) => (
              <div key={d.id} className="p-3 rounded-xl bg-[#FAF9F6] border border-[#E8E6E1] flex items-center justify-between">
                <div>
                  <div className="font-semibold text-xs text-[#2D3139] truncate">{d.title}</div>
                  <div className="text-[10px] text-[#6C727F] mt-0.5">
                    {d.file_name} · {d.chunks_count} chunks indexed
                  </div>
                </div>
                <span className="text-[10px] font-bold bg-[#E2EBE5] text-[#344E41] border border-[#D1E0D7] px-2 py-0.5 rounded-md uppercase">
                  {d.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
