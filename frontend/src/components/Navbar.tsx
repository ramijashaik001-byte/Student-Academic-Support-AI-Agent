import React from "react";
import { GraduationCap, LogOut, UserCircle2, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { NotificationDropdown } from "./NotificationDropdown";
import { ThemeSwitcher } from "./ThemeSwitcher";
import type { UserRole } from "../types";

export const Navbar: React.FC = () => {
  const { user, logout, switchDemoUser } = useAuth();

  const handleSwitch = (role: UserRole) => {
    switchDemoUser(role);
  };

  const getRoleBadge = (role?: string) => {
    switch (role) {
      case "admin":
        return (
          <span className="bg-[#E1EDF8] text-[#2B4C6F] border border-[#CEE3F5] text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider">
            Admin
          </span>
        );
      case "faculty":
        return (
          <span className="bg-[#EBE5FC] text-[#4C3B78] border border-[#DDD6FE] text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider">
            Faculty
          </span>
        );
      default:
        return (
          <span className="bg-[#E2EBE5] text-[#344E41] border border-[#D1E0D7] text-[10px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider">
            Student
          </span>
        );
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-xs text-[#2D3139] border-b border-[#E8E6E1] shadow-[0_1px_3px_rgba(0,0,0,0.03)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shadow-xs">
            <GraduationCap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm sm:text-base tracking-tight text-[#2D3139]">
                AI Student Academic Support Agent
              </span>
            </div>
            <p className="text-[11px] text-[#6B7280] hidden sm:block">
              College document grounded academic assistant
            </p>
          </div>
        </div>

        {/* Demo Switcher & User Actions */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Quick Demo Switcher */}
          <div className="hidden lg:flex items-center bg-[#FBFBFA] border border-[#E8E6E1] p-1 rounded-xl text-xs gap-1">
            <span className="text-[11px] text-[#6B7280] px-2 flex items-center gap-1 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-[#7C6EB0]" /> Switch Role:
            </span>
            <button
              onClick={() => handleSwitch("student")}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                user?.role === "student"
                  ? "bg-[#E2EBE5] text-[#344E41] border border-[#D1E0D7] font-semibold shadow-xs"
                  : "text-[#5A606D] hover:text-[#2D3139] hover:bg-[#F3F2EE]"
              }`}
            >
              Student
            </button>
            <button
              onClick={() => handleSwitch("faculty")}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                user?.role === "faculty"
                  ? "bg-[#EBE5FC] text-[#4C3B78] border border-[#DDD6FE] font-semibold shadow-xs"
                  : "text-[#5A606D] hover:text-[#2D3139] hover:bg-[#F3F2EE]"
              }`}
            >
              Faculty
            </button>
            <button
              onClick={() => handleSwitch("admin")}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all ${
                user?.role === "admin"
                  ? "bg-[#E1EDF8] text-[#2B4C6F] border border-[#CEE3F5] font-semibold shadow-xs"
                  : "text-[#5A606D] hover:text-[#2D3139] hover:bg-[#F3F2EE]"
              }`}
            >
              Administrator
            </button>
          </div>

          {/* Theme Switcher */}
          <ThemeSwitcher />

          {/* In-App Notifications */}
          <NotificationDropdown />

          {/* Current User Card */}
          <div className="flex items-center gap-2 pl-2 border-l border-[#E8E6E1]">
            <div className="hidden md:block text-right">
              <div className="text-xs font-semibold text-[#2D3139]">{user?.full_name}</div>
              <div className="mt-0.5">{getRoleBadge(user?.role)}</div>
            </div>

            <div className="w-9 h-9 rounded-full bg-[#EBE5FC] border border-[#DDD6FE] flex items-center justify-center overflow-hidden text-[#5B4F8A]">
              {user?.avatar_url ? (
                <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
              ) : (
                <UserCircle2 className="w-5 h-5 text-[#5B4F8A]" />
              )}
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 text-[#6B7280] hover:text-[#DC2626] hover:bg-[#FEE2E2]/60 rounded-lg transition-colors ml-1"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
