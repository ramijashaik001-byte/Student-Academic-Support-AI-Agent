export type UserRole = "student" | "faculty" | "admin";

export interface StudentProfile {
  roll_number: string;
  department_id?: number;
  department_name?: string;
  current_semester: number;
  academic_year: string;
  cgpa: number;
}

export interface FacultyProfile {
  employee_id: string;
  department_id?: number;
  department_name?: string;
  designation: string;
  office_location: string;
  office_hours: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  student_profile?: StudentProfile;
  faculty_profile?: FacultyProfile;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Department {
  id: number;
  code: string;
  name: string;
  head_of_department?: string;
  created_at: string;
}

export interface Course {
  id: number;
  department_id: number;
  code: string;
  name: string;
  semester: number;
  credits: number;
  syllabus_summary?: string;
  department_name?: string;
}

export interface Subject {
  id: number;
  course_id: number;
  faculty_id?: number;
  code: string;
  name: string;
  description?: string;
  faculty_name?: string;
}

export interface AcademicSchedule {
  id: number;
  title: string;
  type: "exam" | "class" | "deadline" | "holiday" | "event";
  course_id?: number;
  course_code?: string;
  date: string;
  start_time?: string;
  end_time?: string;
  venue?: string;
  details?: string;
}

export interface DocumentItem {
  id: number;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  category: string;
  department_id?: number;
  department_name?: string;
  course_id?: number;
  course_code?: string;
  academic_year: string;
  access_level: string;
  status: "uploaded" | "processing" | "indexed" | "failed";
  error_message?: string;
  uploaded_by: number;
  uploader_name?: string;
  chunks_count: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface AnswerSource {
  id: number;
  document_id?: number;
  document_title: string;
  page_number?: number;
  section?: string;
  excerpt: string;
  relevance_score: number;
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  sender: "user" | "assistant";
  content: string;
  confidence_score?: number;
  escalation_suggested: boolean;
  feedback_rating?: "like" | "dislike";
  feedback_comment?: string;
  sources: AnswerSource[];
  follow_up_suggestions: string[];
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
  last_message?: string;
  message_count: number;
}

export interface TicketMessage {
  id: number;
  ticket_id: number;
  sender_id: number;
  sender_name: string;
  sender_role: string;
  message: string;
  attachment_url?: string;
  created_at: string;
}

export interface SupportTicket {
  id: number;
  ticket_number: string;
  student_id: number;
  student_name: string;
  student_roll?: string;
  faculty_id?: number;
  faculty_name?: string;
  department_id?: number;
  department_name?: string;
  course_id?: number;
  course_name?: string;
  conversation_id?: number;
  subject: string;
  description: string;
  priority: "low" | "medium" | "high" | "urgent";
  status: "open" | "assigned" | "in_progress" | "waiting_for_student" | "resolved" | "closed";
  created_at: string;
  updated_at: string;
  messages_count: number;
  messages?: TicketMessage[];
}

export interface NotificationItem {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: "ticket_update" | "announcement" | "course_material" | "exam_schedule" | "system";
  link_url?: string;
  is_read: boolean;
  created_at: string;
}

export interface AnnouncementItem {
  id: number;
  author_id: number;
  author_name: string;
  title: string;
  content: string;
  category: string;
  department_id?: number;
  department_name?: string;
  is_published: boolean;
  created_at: string;
}

export interface AdminAnalytics {
  total_users: number;
  total_students: number;
  total_faculty: number;
  total_questions_asked: number;
  questions_answered_with_sources: number;
  unanswered_questions: number;
  citation_rate_percentage: number;
  total_escalations: number;
  open_escalations: number;
  resolved_escalations: number;
  average_response_time_hours: number;
  total_documents: number;
  total_chunks_indexed: number;
  document_indexing_failures: number;
  satisfaction_rate_percentage: number;
  recent_activity: {
    id: number;
    action: string;
    details: string;
    timestamp: string;
  }[];
}

export interface AuditLogItem {
  id: number;
  user_id?: number;
  user_name?: string;
  user_role?: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  details?: string;
  ip_address: string;
  created_at: string;
}
