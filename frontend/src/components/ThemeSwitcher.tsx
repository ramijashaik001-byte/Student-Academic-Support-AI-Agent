import React, { useState, useRef, useEffect } from "react";
import { Moon, Sparkles, Trees, Palette, Check, ChevronDown } from "lucide-react";
import { useTheme, type ThemeMode } from "../context/ThemeContext";

export const ThemeSwitcher: React.FC<{ compact?: boolean }> = ({ compact = false }) => {
  const { theme, setTheme, availableThemes, currentThemeConfig } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEsc);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEsc);
    };
  }, []);

  const getThemeIcon = (id: ThemeMode, className = "w-3.5 h-3.5") => {
    switch (id) {
      case "dark":
        return <Moon className={className} />;
      case "indigo":
        return <Sparkles className={className} />;
      case "emerald":
        return <Trees className={className} />;
      case "pastel":
        return <Palette className={className} />;
      default:
        return <Palette className={className} />;
    }
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        title={`Current Theme: ${currentThemeConfig.name}`}
        aria-label="Switch Theme"
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-xs font-medium transition-all shadow-xs cursor-pointer focus:outline-none theme-switcher-btn"
        style={{
          backgroundColor: "var(--theme-card, #FFFFFF)",
          borderColor: "var(--theme-border, #E8E6E1)",
          color: "var(--theme-text-primary, #2D3139)",
        }}
      >
        <span
          className="w-4 h-4 rounded-md flex items-center justify-center shrink-0"
          style={{ color: currentThemeConfig.primaryColor }}
        >
          {getThemeIcon(theme, "w-3.5 h-3.5")}
        </span>

        {!compact && (
          <span className="text-[11px] font-semibold tracking-tight hidden sm:inline">
            {currentThemeConfig.name}
          </span>
        )}

        <ChevronDown className="w-3 h-3 opacity-60 ml-0.5" />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-64 rounded-2xl border shadow-xl z-50 p-1.5 animate-in fade-in zoom-in-95 duration-100"
          style={{
            backgroundColor: "var(--theme-card, #FFFFFF)",
            borderColor: "var(--theme-border, #E8E6E1)",
            color: "var(--theme-text-primary, #2D3139)",
          }}
        >
          <div className="px-3 py-2 border-b mb-1" style={{ borderColor: "var(--theme-border, #E8E6E1)" }}>
            <p className="text-[10px] font-bold uppercase tracking-wider opacity-60">
              Select Theme Style
            </p>
          </div>

          <div className="space-y-1">
            {availableThemes.map((opt) => {
              const isSelected = opt.id === theme;
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => {
                    setTheme(opt.id);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded-xl text-xs flex items-start gap-2.5 transition-all cursor-pointer ${
                    isSelected ? "font-semibold shadow-xs" : "opacity-80 hover:opacity-100"
                  }`}
                  style={{
                    backgroundColor: isSelected
                      ? "var(--theme-surface-active, rgba(99, 102, 241, 0.08))"
                      : "transparent",
                    color: "var(--theme-text-primary, #2D3139)",
                  }}
                >
                  <span
                    className="w-6 h-6 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
                    style={{
                      backgroundColor: isSelected ? opt.primaryColor : "var(--theme-border, #E8E6E1)",
                      color: isSelected ? "#FFFFFF" : opt.primaryColor,
                    }}
                  >
                    {getThemeIcon(opt.id, "w-3.5 h-3.5")}
                  </span>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold">{opt.name}</span>
                      {isSelected && (
                        <Check className="w-3.5 h-3.5 shrink-0" style={{ color: opt.primaryColor }} />
                      )}
                    </div>
                    <p className="text-[10px] opacity-70 leading-snug mt-0.5 truncate">
                      {opt.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
