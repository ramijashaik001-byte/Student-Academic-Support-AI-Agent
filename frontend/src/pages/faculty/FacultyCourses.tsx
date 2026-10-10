import React, { useState, useEffect } from "react";
import { Layers, Users, BookOpen, Clock, Calendar, CheckCircle2 } from "lucide-react";
import { apiClient } from "../../api/client";
import type { Course, Subject } from "../../types";

export const FacultyCourses: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [crsRes, subjRes] = await Promise.all([
          apiClient.getCourses(),
          apiClient.getSubjects(),
        ]);
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
          <Layers className="w-5 h-5 text-indigo-600" />
          <span>My Assigned Courses & Subjects</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Review curriculum, enrolled student cohorts, and assigned theoretical and practical modules.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {courses.map((c) => (
          <div key={c.id} className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-xs space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-200/60">
                  {c.code}
                </span>
                <h3 className="font-bold text-base text-slate-900 mt-2">{c.name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{c.department_name}</p>
              </div>
              <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2 py-1 rounded-lg border border-teal-200">
                {c.credits} Credits
              </span>
            </div>

            <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600">
              <span className="font-semibold text-slate-800">Syllabus Overview:</span> {c.syllabus_summary}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
              <div className="flex items-center gap-1.5">
                <Users className="w-4 h-4 text-slate-400" />
                <span>64 Enrolled Students</span>
              </div>
              <span className="text-slate-400">Semester {c.semester}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
