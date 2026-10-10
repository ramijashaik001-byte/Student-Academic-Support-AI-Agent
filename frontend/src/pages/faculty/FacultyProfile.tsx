import React from "react";
import { User, Mail, Building, MapPin, Clock, ShieldCheck, Briefcase } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export const FacultyProfile: React.FC = () => {
  const { user } = useAuth();
  const profile = user?.faculty_profile;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-center gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-amber-600 to-indigo-600 text-white font-bold text-3xl flex items-center justify-center shadow-lg">
          {user?.full_name?.charAt(0) || "F"}
        </div>
        <div className="text-center sm:text-left space-y-1">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <h1 className="text-2xl font-bold text-slate-900">{user?.full_name}</h1>
            <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2 py-0.5 rounded-full uppercase">
              Faculty
            </span>
          </div>
          <p className="text-xs text-slate-500 flex items-center justify-center sm:justify-start gap-1">
            <Mail className="w-3.5 h-3.5" />
            {user?.email}
          </p>
          <div className="text-[11px] text-slate-400 pt-1">
            Employee ID: <span className="font-mono font-bold text-slate-700">{profile?.employee_id || "FAC-CSE-001"}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <Briefcase className="w-4 h-4" />
            <span className="text-xs font-semibold text-slate-500 uppercase">Designation</span>
          </div>
          <div className="text-base font-bold text-slate-900">{profile?.designation || "Professor & HOD"}</div>
          <div className="text-[11px] text-slate-400 mt-1">Computer Science & Eng.</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <MapPin className="w-4 h-4" />
            <span className="text-xs font-semibold text-slate-500 uppercase">Office Location</span>
          </div>
          <div className="text-base font-bold text-slate-900">{profile?.office_location || "Block B, Room 301"}</div>
          <div className="text-[11px] text-slate-400 mt-1">Academic Complex</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-indigo-600 mb-2">
            <Clock className="w-4 h-4" />
            <span className="text-xs font-semibold text-slate-500 uppercase">Advising Hours</span>
          </div>
          <div className="text-xs font-bold text-slate-900">{profile?.office_hours || "Mon-Thu 2:00 PM - 4:00 PM"}</div>
          <div className="text-[11px] text-teal-600 font-semibold mt-1">Open for consultations</div>
        </div>
      </div>
    </div>
  );
};
