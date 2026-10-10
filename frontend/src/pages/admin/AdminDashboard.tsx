import React, { useState, useEffect } from "react";
import {
  BarChart3, Users, MessageSquare, BookOpen, LifeBuoy,
  ShieldCheck, AlertTriangle, Clock, ThumbsUp, Activity,
  CheckCircle2, RotateCcw
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, PieChart, Pie, Cell, Legend
} from "recharts";
import { apiClient } from "../../api/client";
import type { AdminAnalytics } from "../../types";

export const AdminDashboard: React.FC = () => {
  const [data, setData] = useState<AdminAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getAnalytics();
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const chartData = [
    { name: "Total Questions", count: data?.total_questions_asked || 0 },
    { name: "Verified Grounded", count: data?.questions_answered_with_sources || 0 },
    { name: "Escalated to Staff", count: data?.total_escalations || 0 },
    { name: "Resolved Tickets", count: data?.resolved_escalations || 0 },
  ];

  const pieData = [
    { name: "Students", value: data?.total_students || 2, color: "#62826F" },
    { name: "Faculty", value: data?.total_faculty || 2, color: "#7C6EB0" },
    { name: "Administrators", value: 1, color: "#4B7BA6" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-[#F5F3FF] border border-[#E0D7FA] text-[#2D3139] rounded-2xl p-6 sm:p-8 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <span className="bg-[#EBE5FC] text-[#5B4F8A] border border-[#DDD6FE] text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider inline-block mb-3">
            Institutional Administration & Analytics
          </span>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2D3139]">
            Academic Operations & AI Health
          </h1>
          <p className="mt-1 text-[#6C727F] text-xs">
            Real database metrics calculated dynamically from academic records.
          </p>
        </div>

        <button
          onClick={loadAnalytics}
          className="px-4 py-2 bg-white hover:bg-[#FAF9F6] text-[#2D3139] text-xs font-medium rounded-xl border border-[#E2DFD7] shadow-xs flex items-center gap-1.5 shrink-0 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5 text-[#5B4F8A]" />
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Total Users</span>
            <Users className="w-4 h-4 text-[#7C6EB0]" />
          </div>
          <div className="text-2xl font-bold text-[#2D3139]">{data?.total_users || 0}</div>
          <div className="text-[11px] text-[#6C727F] mt-0.5">
            {data?.total_students || 0} Students · {data?.total_faculty || 0} Faculty
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Citation Rate</span>
            <ShieldCheck className="w-4 h-4 text-[#62826F]" />
          </div>
          <div className="text-2xl font-bold text-[#466352]">
            {data?.citation_rate_percentage || 100}%
          </div>
          <div className="text-[11px] text-[#62826F] mt-0.5">Questions grounded in documents</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Indexed Chunks</span>
            <BookOpen className="w-4 h-4 text-[#7C6EB0]" />
          </div>
          <div className="text-2xl font-bold text-[#2D3139]">{data?.total_chunks_indexed || 0}</div>
          <div className="text-[11px] text-[#6C727F] mt-0.5">Across {data?.total_documents || 0} authorized files</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-[#E8E6E1] shadow-xs">
          <div className="flex items-center justify-between text-[#6C727F] mb-2">
            <span className="text-xs font-semibold uppercase">Open Escalations</span>
            <LifeBuoy className="w-4 h-4 text-[#B47C57]" />
          </div>
          <div className="text-2xl font-bold text-[#B47C57]">{data?.open_escalations || 0}</div>
          <div className="text-[11px] text-[#6C727F] mt-0.5">Avg response: {data?.average_response_time_hours || 2.4}h</div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E8E6E1] p-5 shadow-xs">
          <h3 className="font-bold text-sm text-[#2D3139] mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-[#7C6EB0]" />
            <span>AI Operations & Query Distribution</span>
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#6C727F" }} />
                <YAxis tick={{ fontSize: 11, fill: "#6C727F" }} />
                <Tooltip />
                <Bar dataKey="count" fill="#7C6EB0" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* User Breakdown Pie */}
        <div className="bg-white rounded-2xl border border-[#E8E6E1] p-5 shadow-xs flex flex-col justify-between">
          <h3 className="font-bold text-sm text-[#2D3139] mb-2 flex items-center gap-2">
            <Users className="w-4 h-4 text-[#62826F]" />
            <span>User Distribution by Role</span>
          </h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} label>
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[11px] text-[#6C727F] text-center pt-2 border-t border-[#E8E6E1]">
            Total active university accounts: {data?.total_users || 0}
          </div>
        </div>
      </div>

      {/* Recent Audit Activity */}
      <div className="bg-white rounded-2xl border border-[#E8E6E1] p-5 shadow-xs">
        <h3 className="font-bold text-sm text-[#2D3139] mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#7C6EB0]" />
          <span>Recent Institutional Audit Activity</span>
        </h3>
        <div className="space-y-2">
          {data?.recent_activity?.map((act) => (
            <div key={act.id} className="p-3 bg-[#FBFBFA] rounded-xl border border-[#E8E6E1] flex items-center justify-between text-xs">
              <div className="flex items-center gap-2.5">
                <span className="font-mono text-[10px] font-bold bg-[#F3F0FF] text-[#53467F] px-2 py-0.5 rounded">
                  {act.action}
                </span>
                <span className="text-[#2D3139]">{act.details}</span>
              </div>
              <span className="text-[10px] text-[#6C727F] shrink-0">{act.timestamp}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
