import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { GraduationCap, Lock, Mail, ArrowRight, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { ThemeSwitcher } from "../components/ThemeSwitcher";

export const Login: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login, switchDemoUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ email, password });
      const savedUser = JSON.parse(localStorage.getItem("auth_user") || "{}");
      if (savedUser.role === "student") navigate("/student/dashboard");
      else if (savedUser.role === "faculty") navigate("/faculty/dashboard");
      else navigate("/admin/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid login credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (role: "student" | "faculty" | "admin") => {
    switchDemoUser(role);
  };

  return (
    <div className="min-h-screen bg-[#FAF9F6] text-[#2D3139] flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Top Bar with Theme Switcher */}
      <div className="absolute top-4 right-4 z-20">
        <ThemeSwitcher />
      </div>

      {/* Gentle soft ambient glows */}
      <div className="absolute top-10 left-1/4 w-80 h-80 bg-[#EBE5FC]/60 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-80 h-80 bg-[#E2EBE5]/60 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10 text-center">
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shadow-xs">
            <GraduationCap className="w-6 h-6" />
          </div>
        </div>
        <h2 className="mt-3 text-center text-xl font-bold tracking-tight text-[#2D3139]">
          AI Student Academic Support Agent
        </h2>
        <p className="mt-1 text-center text-xs text-[#6B7280]">
          Welcome! Sign in to access verified academic resources and personalized guidance.
        </p>
      </div>

      <div className="mt-5 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-white border border-[#E8E6E1] py-7 px-6 shadow-[0_4px_24px_rgba(0,0,0,0.03)] rounded-2xl sm:px-9">
          {error && (
            <div className="mb-4 p-3 bg-[#FEF2F2] border border-[#FCA5A5]/60 rounded-xl text-xs text-[#991B1B]">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-semibold text-[#4B5563] mb-1">
                Institutional Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#9CA3AF] absolute left-3 top-2.5" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ramija.student@campus.edu"
                  required
                  className="w-full bg-[#FAFAFA] border border-[#DDDCD7] rounded-xl pl-9 pr-3 py-2 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#C4B5FD] transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-[#4B5563] mb-1">
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
                  className="w-full bg-[#FAFAFA] border border-[#DDDCD7] rounded-xl pl-9 pr-3 py-2 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#C4B5FD] transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 bg-[#6B5B95] hover:bg-[#5E4E88] text-white font-medium py-2.5 px-4 rounded-xl text-xs shadow-xs transition-colors disabled:opacity-50"
            >
              <span>{loading ? "Signing In..." : "Sign In to Portal"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Quick Demo Logins */}
          <div className="mt-5 pt-5 border-t border-[#E8E6E1]">
            <div className="text-[10px] font-bold text-[#8E939E] uppercase tracking-wider text-center mb-2.5 flex items-center justify-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-[#7C6EB0]" /> Quick Evaluator Demo Logins
            </div>
            <div className="grid grid-cols-1 gap-2">
              <button
                type="button"
                onClick={() => handleDemoLogin("student")}
                className="w-full text-left p-2.5 rounded-xl bg-[#F0F5F2] border border-[#D8E3DC] hover:bg-[#E2EBE5] transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-[#2D3139] group-hover:text-[#285A3F]">
                    Ramija Shaik (Student)
                  </div>
                  <div className="text-[10px] text-[#5A606D]">
                    ramija.student@campus.edu · B.Tech CSE Sem 6
                  </div>
                </div>
                <span className="text-[10px] bg-[#E2EBE5] text-[#344E41] font-semibold px-2 py-0.5 rounded-md border border-[#D1E0D7]">
                  Student
                </span>
              </button>

              <button
                type="button"
                onClick={() => handleDemoLogin("faculty")}
                className="w-full text-left p-2.5 rounded-xl bg-[#F5F3FF] border border-[#E0D7FA] hover:bg-[#EBE5FC] transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-[#2D3139] group-hover:text-[#53467F]">
                    Prof. Rajesh Sharma (Faculty)
                  </div>
                  <div className="text-[10px] text-[#5A606D]">
                    prof.sharma@campus.edu · CSE HOD & Professor
                  </div>
                </div>
                <span className="text-[10px] bg-[#EBE5FC] text-[#4C3B78] font-semibold px-2 py-0.5 rounded-md border border-[#DDD6FE]">
                  Faculty
                </span>
              </button>

              <button
                type="button"
                onClick={() => handleDemoLogin("admin")}
                className="w-full text-left p-2.5 rounded-xl bg-[#F0F6FC] border border-[#D5E4F3] hover:bg-[#E1EDF8] transition-all flex items-center justify-between group"
              >
                <div>
                  <div className="text-xs font-semibold text-[#2D3139] group-hover:text-[#2B4C6F]">
                    Dr. Campus Administrator
                  </div>
                  <div className="text-[10px] text-[#5A606D]">
                    admin@campus.edu · Dean of Academic Affairs
                  </div>
                </div>
                <span className="text-[10px] bg-[#E1EDF8] text-[#2B4C6F] font-semibold px-2 py-0.5 rounded-md border border-[#CEE3F5]">
                  Admin
                </span>
              </button>
            </div>
          </div>

          <div className="mt-4 text-center">
            <Link
              to="/register"
              className="text-xs text-[#5A606D] hover:text-[#5B4F8A] transition-colors"
            >
              Don't have an authorized account? <span className="font-semibold text-[#2D3139] underline">Register here</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
