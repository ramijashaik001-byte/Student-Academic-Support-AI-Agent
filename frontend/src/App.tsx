import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { Layout } from "./components/Layout";

// Auth
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";

// Student
import { StudentDashboard } from "./pages/student/StudentDashboard";
import { StudentChat } from "./pages/student/StudentChat";
import { StudentKnowledgeBase } from "./pages/student/StudentKnowledgeBase";
import { StudentSchedules } from "./pages/student/StudentSchedules";
import { StudentTickets } from "./pages/student/StudentTickets";
import { StudentProfile } from "./pages/student/StudentProfile";

// Faculty
import { FacultyDashboard } from "./pages/faculty/FacultyDashboard";
import { FacultyCourses } from "./pages/faculty/FacultyCourses";
import { FacultyMaterials } from "./pages/faculty/FacultyMaterials";
import { FacultyEscalations } from "./pages/faculty/FacultyEscalations";
import { FacultyAnnouncements } from "./pages/faculty/FacultyAnnouncements";
import { FacultyFeedback } from "./pages/faculty/FacultyFeedback";
import { FacultyProfile } from "./pages/faculty/FacultyProfile";

// Admin
import { AdminDashboard } from "./pages/admin/AdminDashboard";
import { AdminUsers } from "./pages/admin/AdminUsers";
import { AdminAcademic } from "./pages/admin/AdminAcademic";
import { AdminDocuments } from "./pages/admin/AdminDocuments";
import { AdminRagStatus } from "./pages/admin/AdminRagStatus";
import { AdminEscalations } from "./pages/admin/AdminEscalations";
import { AdminAuditLogs } from "./pages/admin/AdminAuditLogs";
import { AdminSettings } from "./pages/admin/AdminSettings";

const RootRedirect: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  if (user?.role === "student") return <Navigate to="/student/dashboard" replace />;
  if (user?.role === "faculty") return <Navigate to="/faculty/dashboard" replace />;
  return <Navigate to="/admin/dashboard" replace />;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            {/* Public Auth */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Root redirect */}
            <Route path="/" element={<RootRedirect />} />

            {/* Protected Application Routes */}
            <Route element={<Layout />}>
              {/* Student */}
              <Route path="/student/dashboard" element={<StudentDashboard />} />
              <Route path="/student/chat" element={<StudentChat />} />
              <Route path="/student/knowledge-base" element={<StudentKnowledgeBase />} />
              <Route path="/student/schedules" element={<StudentSchedules />} />
              <Route path="/student/tickets" element={<StudentTickets />} />
              <Route path="/student/profile" element={<StudentProfile />} />

              {/* Faculty */}
              <Route path="/faculty/dashboard" element={<FacultyDashboard />} />
              <Route path="/faculty/courses" element={<FacultyCourses />} />
              <Route path="/faculty/materials" element={<FacultyMaterials />} />
              <Route path="/faculty/escalations" element={<FacultyEscalations />} />
              <Route path="/faculty/announcements" element={<FacultyAnnouncements />} />
              <Route path="/faculty/feedback" element={<FacultyFeedback />} />
              <Route path="/faculty/profile" element={<FacultyProfile />} />

              {/* Admin */}
              <Route path="/admin/dashboard" element={<AdminDashboard />} />
              <Route path="/admin/users" element={<AdminUsers />} />
              <Route path="/admin/academic" element={<AdminAcademic />} />
              <Route path="/admin/documents" element={<AdminDocuments />} />
              <Route path="/admin/rag-status" element={<AdminRagStatus />} />
              <Route path="/admin/escalations" element={<AdminEscalations />} />
              <Route path="/admin/audit-logs" element={<AdminAuditLogs />} />
              <Route path="/admin/settings" element={<AdminSettings />} />
            </Route>

            {/* 404 Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

export default App;
