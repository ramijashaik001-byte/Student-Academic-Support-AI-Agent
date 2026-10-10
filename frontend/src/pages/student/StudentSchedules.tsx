import React, { useState, useEffect } from "react";
import {
  Calendar, Clock, MapPin, CheckCircle2, AlertCircle,
  FileCheck, ShieldAlert, Award
} from "lucide-react";
import { apiClient } from "../../api/client";
import type { AcademicSchedule } from "../../types";

export const StudentSchedules: React.FC = () => {
  const [schedules, setSchedules] = useState<AcademicSchedule[]>([]);
  const [guidelines, setGuidelines] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"exams" | "deadlines" | "classes" | "guidelines">("exams");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [schedRes, guideRes] = await Promise.all([
          apiClient.getSchedules(),
          apiClient.getExamGuidelines(),
        ]);
        setSchedules(schedRes.data);
        setGuidelines(guideRes.data.guidelines || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const exams = schedules.filter((s) => s.type === "exam");
  const deadlines = schedules.filter((s) => s.type === "deadline");
  const classes = schedules.filter((s) => s.type === "class");

  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-indigo-600" />
          <span>Academic Schedules & Examination Guidelines</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Official, verified examination schedules, class timetables, and mandatory academic guidelines for Fall 2026.
        </p>

        {/* Tab Switcher */}
        <div className="flex flex-wrap gap-2 mt-5 border-t border-slate-100 pt-4">
          <button
            onClick={() => setActiveTab("exams")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === "exams"
                ? "bg-indigo-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/70"
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Examination Timetable ({exams.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("deadlines")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === "deadlines"
                ? "bg-amber-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/70"
            }`}
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Assignment Deadlines ({deadlines.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("classes")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === "classes"
                ? "bg-teal-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/70"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Class & Lab Schedules ({classes.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("guidelines")}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === "guidelines"
                ? "bg-purple-600 text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200/70"
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Mandatory Exam Guidelines</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500 bg-white rounded-2xl border border-slate-200">
          Loading verified academic schedules...
        </div>
      ) : activeTab === "exams" ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
          <div className="p-4 bg-indigo-50/60 border-b border-indigo-100 flex items-center justify-between">
            <span className="text-xs font-bold text-indigo-950 uppercase tracking-wider">
              Mid-Semester Examinations (Semester 6)
            </span>
            <span className="text-[11px] text-indigo-700 font-semibold bg-indigo-100 px-2 py-0.5 rounded">
              Verified by Controller of Examinations
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {exams.map((ex) => (
              <div key={ex.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-xs bg-slate-100 text-slate-800 px-2 py-0.5 rounded">
                      {ex.course_code || "EXAM"}
                    </span>
                    <h3 className="font-bold text-sm text-slate-900">{ex.title}</h3>
                  </div>
                  <p className="text-xs text-slate-500">{ex.details}</p>
                  <div className="flex items-center gap-3 text-xs text-slate-600 pt-1">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      {ex.start_time} - {ex.end_time}
                    </span>
                    <span>·</span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      {ex.venue}
                    </span>
                  </div>
                </div>

                <div className="sm:text-right shrink-0">
                  <div className="text-sm font-bold text-indigo-700 bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-100 inline-block">
                    {ex.date}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">Hall Ticket Required</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : activeTab === "deadlines" ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
          <div className="p-4 bg-amber-50/60 border-b border-amber-100">
            <span className="text-xs font-bold text-amber-950 uppercase tracking-wider">
              Upcoming Project & Assignment Milestones
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {deadlines.map((dl) => (
              <div key={dl.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/60 transition-colors">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-xs bg-amber-100 text-amber-900 px-2 py-0.5 rounded">
                      {dl.course_code || "ASSIGN"}
                    </span>
                    <h3 className="font-bold text-sm text-slate-900">{dl.title}</h3>
                  </div>
                  <p className="text-xs text-slate-500">{dl.details}</p>
                  <div className="flex items-center gap-2 text-xs text-slate-600 pt-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>Submission Portal: {dl.venue || "LMS"}</span>
                  </div>
                </div>

                <div className="sm:text-right shrink-0">
                  <div className="text-sm font-bold text-amber-800 bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-200 inline-block">
                    Due {dl.date} ({dl.start_time})
                  </div>
                  <div className="text-[10px] text-slate-400 mt-1">Late Penalty: 10%/day</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : activeTab === "classes" ? (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs space-y-3">
          <h3 className="font-bold text-sm text-slate-900">Weekly Laboratory & Tutorial Sessions</h3>
          {classes.map((c) => (
            <div key={c.id} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/60 flex items-center justify-between">
              <div>
                <div className="font-semibold text-xs text-slate-900">{c.title}</div>
                <div className="text-xs text-slate-500 mt-0.5">{c.details}</div>
                <div className="text-[11px] text-slate-400 mt-1">{c.venue} · {c.start_time} - {c.end_time}</div>
              </div>
              <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-lg border border-teal-200">
                {c.date}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-5 h-5 text-purple-600" />
            <h3 className="font-bold text-sm text-slate-900">Academic Regulations & Hall Ticket Rules</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {guidelines.map((g, idx) => (
              <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200/70 text-xs space-y-1.5">
                <div className="font-bold text-slate-900 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-teal-600 shrink-0" />
                  <span>{g.title}</span>
                </div>
                <p className="text-slate-600 leading-relaxed text-[11px]">
                  {g.rule}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
