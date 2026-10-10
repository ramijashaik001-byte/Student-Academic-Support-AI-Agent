import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GraduationCap, Lock, Mail, User, Building, Hash, ArrowRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { apiClient } from "../api/client";
import type { Department } from "../types";

export const Register: React.FC = () => {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"student" | "faculty">("student");
  const [rollNumber, setRollNumber] = useState("");
  const [departmentId, setDepartmentId] = useState<number | undefined>(undefined);
  const [semester, setSemester] = useState(1);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    apiClient.getDepartments().then((res) => {
      setDepartments(res.data);
      if (res.data.length > 0) setDepartmentId(res.data[0].id);
    }).catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await register({
        full_name: fullName,
        email,
        password,
        role,
        roll_number: role === "student" ? rollNumber : undefined,
        department_id: departmentId,
        current_semester: role === "student" ? semester : undefined,
      });

      if (role === "student") navigate("/student/dashboard");
      else navigate("/faculty/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Check your inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAF9F6] flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        <div className="w-12 h-12 mx-auto rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shadow-xs">
          <GraduationCap className="w-6 h-6" />
        </div>
        <h2 className="mt-3 text-xl font-bold tracking-tight text-[#2D3139]">
          Create Academic Account
        </h2>
        <p className="mt-1 text-xs text-[#6C727F]">
          AI Student Academic Support Agent
        </p>
      </div>

      <div className="mt-5 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-white border border-[#E8E6E1] py-6 px-6 shadow-sm rounded-2xl sm:px-8">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alex Morgan"
                  required
                  className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl pl-9 pr-3 py-2 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                Institutional Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-2.5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@campus.edu"
                  required
                  className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl pl-9 pr-3 py-2 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-2.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl pl-9 pr-3 py-2 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                  Role
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value as any)}
                  className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl px-2.5 py-2 text-xs text-[#2D3139] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                >
                  <option value="student">Student</option>
                  <option value="faculty">Faculty Member</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                  Department
                </label>
                <select
                  value={departmentId || ""}
                  onChange={(e) => setDepartmentId(Number(e.target.value))}
                  className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl px-2.5 py-2 text-xs text-[#2D3139] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                >
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.code} - {d.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {role === "student" && (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                    Roll Number
                  </label>
                  <input
                    type="text"
                    value={rollNumber}
                    onChange={(e) => setRollNumber(e.target.value)}
                    placeholder="2026-CS-101"
                    className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl px-3 py-2 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#4B515D] mb-1">
                    Semester
                  </label>
                  <select
                    value={semester}
                    onChange={(e) => setSemester(Number(e.target.value))}
                    className="w-full bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl px-2.5 py-2 text-xs text-[#2D3139] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:border-[#7C6EB0]"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                      <option key={s} value={s}>
                        Semester {s}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-3 flex items-center justify-center gap-2 bg-[#5B4F8A] hover:bg-[#4E4377] text-white font-medium py-2.5 px-4 rounded-xl text-xs shadow-xs transition-colors disabled:opacity-50"
            >
              <span>{loading ? "Registering..." : "Create Account"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          <div className="mt-4 text-center">
            <Link
              to="/login"
              className="text-xs text-[#6C727F] hover:text-[#5B4F8A] transition-colors"
            >
              Already registered? <span className="font-semibold text-[#5B4F8A] underline">Sign In</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
