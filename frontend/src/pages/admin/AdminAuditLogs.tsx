import React, { useState, useEffect } from "react";
import { ShieldAlert, Clock, User, Globe } from "lucide-react";
import { apiClient } from "../../api/client";
import type { AuditLogItem } from "../../types";

export const AdminAuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getAuditLogs();
      setLogs(res.data);
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
          <ShieldAlert className="w-5 h-5 text-indigo-600" />
          <span>Security & Administrative Audit Trail</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Immutable institutional audit trail recording logins, document uploads, role modifications, and ticket resolutions.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-bold">
              <tr>
                <th className="p-3.5 pl-6">Action / Event</th>
                <th className="p-3.5">User</th>
                <th className="p-3.5">Details</th>
                <th className="p-3.5">IP Address</th>
                <th className="p-3.5 text-right pr-6">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {logs.map((l) => (
                <tr key={l.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="p-3.5 pl-6">
                    <span className="font-mono font-bold text-[10px] text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200/60">
                      {l.action}
                    </span>
                  </td>
                  <td className="p-3.5 font-medium text-slate-800">
                    {l.user_name || "System"} ({l.user_role || "system"})
                  </td>
                  <td className="p-3.5 text-slate-600 max-w-sm truncate">
                    {l.details || "Administrative event"}
                  </td>
                  <td className="p-3.5 font-mono text-slate-400 text-[11px]">
                    {l.ip_address}
                  </td>
                  <td className="p-3.5 text-right pr-6 text-slate-400 text-[11px]">
                    {new Date(l.created_at).toLocaleString([], {
                      month: "short",
                      day: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
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
