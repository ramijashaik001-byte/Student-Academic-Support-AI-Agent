import React from "react";
import { User, Award, BookOpen, Building, Mail, Hash, Calendar, ShieldCheck } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export const StudentProfile: React.FC = () => {
  const { user } = useAuth();
  const profile = user?.student_profile;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header Profile Card */}
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-center gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 to-teal-500 text-white font-bold text-3xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
          {user?.full_name?.charAt(0) || "S"}
        </div>
        <div className="text-center sm:text-left space-y-1">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <h1 className="text-2xl font-bold text-slate-900">{user?.full_name}</h1>
            <span className="bg-teal-100 text-teal-800 text-xs font-bold px-2 py-0.5 rounded-full uppercase">
              Student
            </span>
          </div>
          <p className="text-xs text-slate-500 flex items-center justify-center sm:justify-start gap-1">
            <Mail className="w-3.5 h-3.5" />
            {user?.email}
          </p>
          <div className="text-[11px] text-slate-400 pt-1">
            Roll Number: <span className="font-mono font-bold text-slate-700">{profile?.roll_number || "2026-CS-101"}</span> · Academic Session {profile?.academic_year || "2025-2026"}
          </div>
        </div>
      </div>

      {/* Academic Details Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <Award className="w-4 h-4" />
            <span className="text-xs font-semibold text-slate-500 uppercase">Current CGPA</span>
          </div>
          <div className="text-2xl font-bold text-slate-900">{profile?.cgpa || 8.85}</div>
          <div className="text-[11px] text-teal-600 font-semibold mt-1">Excellent Standing</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <BookOpen className="w-4 h-4" />
            <span className="text-xs font-semibold text-slate-500 uppercase">Current Term</span>
          </div>
          <div className="text-2xl font-bold text-slate-900">Semester {profile?.current_semester || 6}</div>
          <div className="text-[11px] text-slate-400 mt-1">B.Tech Program</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <Building className="w-4 h-4" />
            <span className="text-xs font-semibold text-slate-500 uppercase">Department</span>
          </div>
          <div className="text-lg font-bold text-slate-900">Computer Science & Eng.</div>
          <div className="text-[11px] text-slate-400 mt-1">School of Computing</div>
        </div>
      </div>

      {/* System & AI Preferences */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
        <h3 className="font-bold text-sm text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-teal-600" />
          <span>AI Academic Support System Integration</span>
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          Your student profile is synchronized with university databases for role-based access control (RBAC). 
          The AI Academic Support Agent retrieves verified documents specifically authorized for B.Tech Semester 6 students.
        </p>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-2">
          <div className="font-semibold text-slate-800">Verification & Privacy Policy:</div>
          <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
            <li>Conversation memory is private and isolated to your student account.</li>
            <li>All AI answers cite official documents with page and section numbers.</li>
            <li>Low-confidence queries can be escalated directly to your faculty mentor at any time.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
