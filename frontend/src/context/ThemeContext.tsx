import React, { createContext, useContext, useState, useEffect } from "react";

export type ThemeMode = "dark" | "indigo" | "emerald" | "pastel";

export interface ThemeOption {
  id: ThemeMode;
  name: string;
  description: string;
  badge: string;
  primaryColor: string;
  bgColor: string;
  textColor: string;
  accentColor: string;
}

export const THEME_OPTIONS: ThemeOption[] = [
  {
    id: "dark",
    name: "Modern Dark",
    description: "Sleek obsidian & dark slate with glowing neon accents",
    badge: "Dark Mode",
    primaryColor: "#6366F1",
    bgColor: "#0B0F19",
    textColor: "#F8FAFC",
    accentColor: "#818CF8",
  },
  {
    id: "indigo",
    name: "Classic Indigo",
    description: "Crisp modern tech aesthetic with royal indigo & slate",
    badge: "Tech Clean",
    primaryColor: "#4F46E5",
    bgColor: "#F8FAFC",
    textColor: "#0F172A",
    accentColor: "#3B82F6",
  },
  {
    id: "emerald",
    name: "Campus Emerald",
    description: "Fresh university theme with deep forest green & mint",
    badge: "University",
    primaryColor: "#1B4332",
    bgColor: "#F2F9F5",
    textColor: "#132A13",
    accentColor: "#10B981",
  },
  {
    id: "pastel",
    name: "Soft Pastel",
    description: "Calming soft lavender, sage green & warm off-white",
    badge: "Calm Pastel",
    primaryColor: "#5B4F8A",
    bgColor: "#FAF9F6",
    textColor: "#2D3139",
    accentColor: "#7C6EB0",
  },
];

interface ThemeContextType {
  theme: ThemeMode;
  setTheme: (mode: ThemeMode) => void;
  availableThemes: ThemeOption[];
  currentThemeConfig: ThemeOption;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem("academic_theme") as ThemeMode | null;
    return saved && ["dark", "indigo", "emerald", "pastel"].includes(saved) ? saved : "dark";
  });

  const setTheme = (mode: ThemeMode) => {
    setThemeState(mode);
    localStorage.setItem("academic_theme", mode);
    document.documentElement.setAttribute("data-theme", mode);
  };

  useEffect(() => {
    // Apply theme on initial mount
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const currentThemeConfig =
    THEME_OPTIONS.find((t) => t.id === theme) || THEME_OPTIONS[0];

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        availableThemes: THEME_OPTIONS,
        currentThemeConfig,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};
