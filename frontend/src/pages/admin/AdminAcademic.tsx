import React, { useState, useEffect } from "react";
import { GraduationCap, Building, Layers, BookOpen } from "lucide-react";
import { apiClient } from "../../api/client";
import type { Department, Course, Subject } from "../../types";

export const AdminAcademic: React.FC = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [depRes, crsRes, subjRes] = await Promise.all([
          apiClient.getDepartments(),
          apiClient.getCourses(),
          apiClient.getSubjects(),
        ]);
        setDepartments(depRes.data);
        setCourses(crsRes.data);
        setSubjects(subjRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-indigo-600" />
          <span>Academic Structure (Departments, Courses & Subjects)</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Master structure defining access permissions and course-level document filtering for RAG.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Departments */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-indigo-600 font-bold text-sm">
            <Building className="w-4 h-4" />
            <span>Departments ({departments.length})</span>
          </div>
          <div className="divide-y divide-slate-100">
            {departments.map((d) => (
              <div key={d.id} className="py-2.5 text-xs">
                <div className="font-semibold text-slate-900">{d.name}</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Code: {d.code} · HOD: {d.head_of_department || "Appointed"}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Courses */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-teal-600 font-bold text-sm">
            <Layers className="w-4 h-4" />
            <span>Active Courses ({courses.length})</span>
          </div>
          <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
            {courses.map((c) => (
              <div key={c.id} className="py-2.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">{c.code}</span>
                  <span className="text-[10px] text-slate-400">Sem {c.semester}</span>
                </div>
                <div className="font-semibold text-slate-900 mt-1">{c.name}</div>
                <div className="text-[11px] text-slate-500 mt-0.5">{c.credits} Credits</div>
              </div>
            ))}
          </div>
        </div>

        {/* Subjects */}
        <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-xs space-y-3">
          <div className="flex items-center gap-2 text-purple-600 font-bold text-sm">
            <BookOpen className="w-4 h-4" />
            <span>Subjects & Faculty Modules</span>
          </div>
          <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
            {subjects.map((s) => (
              <div key={s.id} className="py-2.5 text-xs">
                <div className="font-semibold text-slate-900">{s.name} ({s.code})</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Lead: {s.faculty_name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
