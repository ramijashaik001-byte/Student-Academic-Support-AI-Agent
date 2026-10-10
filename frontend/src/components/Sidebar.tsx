import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard, MessageSquareText, BookOpen, Calendar,
  LifeBuoy, User, Layers, UploadCloud, BellRing, BarChart3,
  Users, Database, Activity, ShieldAlert, Settings, CheckSquare,
  GraduationCap
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();

  const studentLinks = [
    { label: "Dashboard", path: "/student/dashboard", icon: LayoutDashboard },
    { label: "AI Academic Chat", path: "/student/chat", icon: MessageSquareText },
    { label: "Knowledge Base", path: "/student/knowledge-base", icon: BookOpen },
    { label: "Schedules & Exams", path: "/student/schedules", icon: Calendar },
    { label: "Support Tickets", path: "/student/tickets", icon: LifeBuoy },
    { label: "My Profile", path: "/student/profile", icon: User },
  ];

  const facultyLinks = [
    { label: "Faculty Overview", path: "/faculty/dashboard", icon: LayoutDashboard },
    { label: "My Courses", path: "/faculty/courses", icon: Layers },
    { label: "Course Materials", path: "/faculty/materials", icon: UploadCloud },
    { label: "Escalated Queries", path: "/faculty/escalations", icon: LifeBuoy },
    { label: "Announcements", path: "/faculty/announcements", icon: BellRing },
    { label: "KB Feedback", path: "/faculty/feedback", icon: BarChart3 },
    { label: "Faculty Profile", path: "/faculty/profile", icon: User },
  ];

  const adminLinks = [
    { label: "Admin Analytics", path: "/admin/dashboard", icon: BarChart3 },
    { label: "User Management", path: "/admin/users", icon: Users },
    { label: "Academic Structure", path: "/admin/academic", icon: GraduationCap },
    { label: "Document Master", path: "/admin/documents", icon: Database },
    { label: "RAG Vector Status", path: "/admin/rag-status", icon: Activity },
    { label: "Escalations Tracker", path: "/admin/escalations", icon: CheckSquare },
    { label: "Audit Logs", path: "/admin/audit-logs", icon: ShieldAlert },
    { label: "System Settings", path: "/admin/settings", icon: Settings },
  ];

  let links = studentLinks;
  if (user?.role === "faculty") links = facultyLinks;
  if (user?.role === "admin") links = adminLinks;

  return (
    <aside className="w-64 bg-white border-r border-[#E8E6E1] flex flex-col shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 border-b border-[#F0EFEA]">
        <div className="text-[10px] font-bold uppercase tracking-wider text-[#8E939E]">
          {user?.role === "student" ? "Student Navigation" : user?.role === "faculty" ? "Faculty Navigation" : "Admin Console"}
        </div>
      </div>

      <nav className="p-3 space-y-1 flex-1">
        {links.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname.startsWith(item.path);

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs transition-all ${
                isActive
                  ? "bg-[#F3F0FF] text-[#53467F] font-semibold border border-[#E0D7FA] shadow-[0_1px_2px_rgba(0,0,0,0.02)]"
                  : "text-[#5A606D] hover:text-[#2D3139] hover:bg-[#F8F7F4]"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-[#7C6EB0]" : "text-[#8E939E]"}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#E8E6E1] text-[11px] text-[#6B7280] bg-[#FAF9F6]">
        <div className="font-medium text-[#3E434D]">University Academic Portal</div>
        <div className="text-[10px] text-[#8E939E] mt-0.5">Academic Session 2025–2026</div>
      </div>
    </aside>
  );
};
