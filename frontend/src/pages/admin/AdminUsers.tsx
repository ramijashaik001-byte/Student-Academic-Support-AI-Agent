import React, { useState, useEffect } from "react";
import { Users, Shield, UserCheck, UserX, Search, Filter } from "lucide-react";
import { apiClient } from "../../api/client";
import type { User as UserType } from "../../types";

export const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<UserType[]>([]);
  const [loading, setLoading] = useState(true);
  const [roleFilter, setRoleFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    loadUsers();
  }, [roleFilter]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const params = roleFilter !== "all" ? roleFilter : undefined;
      const res = await apiClient.getUsers(params);
      setUsers(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      await apiClient.updateUserRole(userId, newRole);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole as any } : u))
      );
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to update role.");
    }
  };

  const handleStatusToggle = async (userId: number, currentStatus: boolean) => {
    try {
      await apiClient.updateUserStatus(userId, !currentStatus);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: !currentStatus } : u))
      );
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to toggle status.");
    }
  };

  const filteredUsers = users.filter((u) =>
    u.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    u.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-600" />
            <span>Institutional User Management & RBAC</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage students, faculty advisors, and administrative accounts. Backend enforces authorization strictly.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search users..."
            className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-indigo-500"
          />
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-1.5 focus:ring-2 focus:ring-indigo-500"
          >
            <option value="all">All Roles</option>
            <option value="student">Students</option>
            <option value="faculty">Faculty</option>
            <option value="admin">Administrators</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 uppercase text-[10px] font-bold">
              <tr>
                <th className="p-3.5 pl-6">User / Email</th>
                <th className="p-3.5">Assigned Role</th>
                <th className="p-3.5">Academic Profile Details</th>
                <th className="p-3.5">Status</th>
                <th className="p-3.5 text-right pr-6">Manage Access</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredUsers.map((u) => (
                <tr key={u.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="p-3.5 pl-6">
                    <div className="font-semibold text-slate-900">{u.full_name}</div>
                    <div className="text-[11px] text-slate-400">{u.email}</div>
                  </td>
                  <td className="p-3.5">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="text-xs bg-slate-50 border border-slate-300 rounded px-2 py-1 font-semibold capitalize"
                    >
                      <option value="student">Student</option>
                      <option value="faculty">Faculty</option>
                      <option value="admin">Administrator</option>
                    </select>
                  </td>
                  <td className="p-3.5 text-slate-600">
                    {u.role === "student" && u.student_profile && (
                      <span>Roll: {u.student_profile.roll_number} · Sem {u.student_profile.current_semester}</span>
                    )}
                    {u.role === "faculty" && u.faculty_profile && (
                      <span>Emp ID: {u.faculty_profile.employee_id} · {u.faculty_profile.designation}</span>
                    )}
                    {u.role === "admin" && <span className="text-purple-700 font-semibold">Institutional Senate Admin</span>}
                  </td>
                  <td className="p-3.5">
                    {u.is_active ? (
                      <span className="bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        Active
                      </span>
                    ) : (
                      <span className="bg-red-100 text-red-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        Deactivated
                      </span>
                    )}
                  </td>
                  <td className="p-3.5 text-right pr-6">
                    <button
                      onClick={() => handleStatusToggle(u.id, u.is_active)}
                      className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-colors ${
                        u.is_active
                          ? "text-red-700 hover:bg-red-50 border border-red-200"
                          : "text-teal-700 hover:bg-teal-50 border border-teal-200"
                      }`}
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
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
