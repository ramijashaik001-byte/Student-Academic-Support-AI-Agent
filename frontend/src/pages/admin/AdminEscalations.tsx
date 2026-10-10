import React, { useState, useEffect } from "react";
import { LifeBuoy, Filter, User, Clock, CheckCircle2 } from "lucide-react";
import { apiClient } from "../../api/client";
import type { SupportTicket } from "../../types";

export const AdminEscalations: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getTickets();
      setTickets(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <LifeBuoy className="w-5 h-5 text-indigo-600" />
          <span>Institutional Escalation & Support Tickets</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Campus-wide oversight of student academic escalations, faculty response rates, and resolutions.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-bold">
              <tr>
                <th className="p-3.5 pl-6">Ticket No.</th>
                <th className="p-3.5">Student</th>
                <th className="p-3.5">Assigned Faculty</th>
                <th className="p-3.5">Subject</th>
                <th className="p-3.5">Priority</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right pr-6">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tickets.map((t) => (
                <tr key={t.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="p-3.5 pl-6 font-mono font-bold text-indigo-700">
                    {t.ticket_number}
                  </td>
                  <td className="p-3.5 font-semibold text-slate-900">
                    {t.student_name}
                  </td>
                  <td className="p-3.5 text-slate-600">
                    {t.faculty_name || "Unassigned"}
                  </td>
                  <td className="p-3.5 text-slate-800 truncate max-w-xs">
                    {t.subject}
                  </td>
                  <td className="p-3.5">
                    <span className="uppercase text-[9px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                      {t.priority}
                    </span>
                  </td>
                  <td className="p-3.5">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${
                      t.status === "resolved" ? "bg-teal-100 text-teal-800" :
                      t.status === "waiting_for_student" ? "bg-blue-100 text-blue-800" :
                      "bg-amber-100 text-amber-800"
                    }`}>
                      {t.status.replace("_", " ")}
                    </span>
                  </td>
                  <td className="p-3.5 text-right pr-6 text-slate-400">
                    {new Date(t.created_at).toLocaleDateString([], { month: "short", day: "numeric" })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
