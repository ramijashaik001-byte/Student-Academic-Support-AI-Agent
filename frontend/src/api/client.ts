import axios from "axios";
import type {
  AuthResponse, User, Department, Course, Subject,
  AcademicSchedule, DocumentItem, ChatMessage, Conversation,
  SupportTicket, TicketMessage, NotificationItem, AnnouncementItem,
  AdminAnalytics, AuditLogItem
} from "../types";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("auth_token");
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Don't auto-redirect if we are checking switch-demo
      const isSwitch = error.config?.url?.includes("/auth/switch-demo");
      if (!isSwitch && !window.location.pathname.includes("/login")) {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
      }
    }
    return Promise.reject(error);
  }
);

export const apiClient = {
  // Auth
  login: (data: any) => api.post<AuthResponse>("/auth/login", data),
  register: (data: any) => api.post<AuthResponse>("/auth/register", data),
  getMe: () => api.get<User>("/auth/me"),
  logout: () => api.post("/auth/logout"),
  switchDemo: (role: string) => api.post<AuthResponse>(`/auth/switch-demo?role=${role}`),

  // Chat
  askQuestion: (data: { message: string; conversation_id?: number; course_id?: number }) =>
    api.post<ChatMessage>("/chat", data),
  getConversations: () => api.get<Conversation[]>("/chat/conversations"),
  getConversation: (id: number) => api.get<{ id: number; title: string; messages: ChatMessage[] }>(`/chat/conversations/${id}`),
  createConversation: () => api.post<Conversation>("/chat/conversations"),
  deleteConversation: (id: number) => api.delete(`/chat/conversations/${id}`),
  submitFeedback: (messageId: number, data: { rating: "like" | "dislike"; comment?: string }) =>
    api.post(`/chat/messages/${messageId}/feedback`, data),

  // Documents
  getDocuments: (params?: { category?: string; department_id?: number }) =>
    api.get<DocumentItem[]>("/documents", { params }),
  getDocument: (id: number) => api.get<DocumentItem>(`/documents/${id}`),
  getDocumentStatus: (id: number) => api.get<{ id: number; status: string; chunks_count: number }>(`/documents/${id}/status`),
  uploadDocument: (formData: FormData) =>
    api.post<DocumentItem>("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  deleteDocument: (id: number) => api.delete(`/documents/${id}`),
  reindexDocument: (id: number) => api.post(`/documents/${id}/reindex`),

  // Tickets
  createTicket: (data: any) => api.post<SupportTicket>("/tickets", data),
  getTickets: (params?: { status_filter?: string; priority_filter?: string }) =>
    api.get<SupportTicket[]>("/tickets", { params }),
  getTicket: (id: number) => api.get<SupportTicket>(`/tickets/${id}`),
  sendTicketMessage: (id: number, data: { message: string; attachment_url?: string }) =>
    api.post<TicketMessage>(`/tickets/${id}/messages`, data),
  updateTicketStatus: (id: number, status: string) =>
    api.patch<SupportTicket>(`/tickets/${id}/status`, { status }),
  assignTicket: (id: number, faculty_id: number) =>
    api.patch<SupportTicket>(`/tickets/${id}/assign`, { faculty_id }),

  // Academic
  getDepartments: () => api.get<Department[]>("/academic/departments"),
  getCourses: (department_id?: number) =>
    api.get<Course[]>("/academic/courses", { params: { department_id } }),
  getSubjects: (course_id?: number) =>
    api.get<Subject[]>("/academic/subjects", { params: { course_id } }),
  getSchedules: (params?: { schedule_type?: string; course_id?: number }) =>
    api.get<AcademicSchedule[]>("/academic/schedules", { params }),
  getExamGuidelines: () => api.get<{ guidelines: any[]; verified_document_sources: string[] }>("/academic/exam-guidelines"),
  getAcademicProfile: () => api.get<any>("/academic/profile"),
  getAcademicSemesters: () => api.get<any[]>("/academic/semesters"),
  getCurriculumSubjects: (params: { semester?: string; keyword?: string }) =>
    api.get<any>("/academic/curriculum/subjects", { params }),
  getStudentMarks: (semester?: string, subject_code?: string) =>
    api.get<any>("/academic/student/marks", { params: { semester, subject_code } }),
  getAllStudentMarks: () => api.get<any>("/academic/student/marks/all"),
  getStudentAttendance: (semester?: string, subject_code?: string) =>
    api.get<any>("/academic/student/attendance", { params: { semester, subject_code } }),
  getStudentBacklogs: () => api.get<any>("/academic/student/backlogs"),
  getAcademicProgress: () => api.get<any>("/academic/student/progress"),
  validateMarksCsv: (formData: FormData) =>
    api.post<any>("/academic/import/marks-csv", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  confirmMarksImport: (payload: any) =>
    api.post<any>("/academic/import/confirm-marks", payload),
  getTemplateDownloadUrl: (type: string) => `/api/academic/templates/${type}`,

  // Announcements
  getAnnouncements: (category?: string) =>
    api.get<AnnouncementItem[]>("/announcements", { params: { category } }),
  createAnnouncement: (data: any) => api.post<AnnouncementItem>("/announcements", data),
  deleteAnnouncement: (id: number) => api.delete(`/announcements/${id}`),

  // Notifications
  getNotifications: () => api.get<NotificationItem[]>("/notifications"),
  getUnreadCount: () => api.get<{ unread_count: number }>("/notifications/unread-count"),
  markNotificationRead: (id: number) => api.patch(`/notifications/${id}/read`),
  markAllNotificationsRead: () => api.post("/notifications/read-all"),

  // Admin
  getAnalytics: () => api.get<AdminAnalytics>("/admin/analytics"),
  getUsers: (role?: string) => api.get<User[]>("/admin/users", { params: { role } }),
  updateUserRole: (id: number, new_role: string) =>
    api.patch<User>(`/admin/users/${id}/role?new_role=${new_role}`),
  updateUserStatus: (id: number, is_active: boolean) =>
    api.patch<User>(`/admin/users/${id}/status?is_active=${is_active}`),
  getRagStatus: () => api.get<any>("/admin/rag-status"),
  reindexAllDocs: () => api.post<any>("/admin/rag-reindex-all"),
  getAuditLogs: (limit?: number) => api.get<AuditLogItem[]>("/admin/audit-logs", { params: { limit } }),
  getSettings: () => api.get<any>("/admin/settings"),
  updateSettings: (data: any) => api.post("/admin/settings", data),
};
