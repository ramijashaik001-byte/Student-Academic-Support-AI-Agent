import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Send, Plus, Trash2, Search, Bot, User, Copy, Check,
  ThumbsUp, ThumbsDown, LifeBuoy, Sparkles, AlertTriangle,
  RotateCcw, BookOpen, ChevronRight, MessageSquare,
  GraduationCap, UploadCloud
} from "lucide-react";
import { apiClient } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import type { ChatMessage, Conversation } from "../../types";
import { CitationCard } from "../../components/CitationCard";
import { EscalateModal } from "../../components/EscalateModal";
import { AcademicMarksModal } from "../../components/AcademicMarksModal";

export const StudentChat: React.FC = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const urlConvId = searchParams.get("id");

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | undefined>(
    urlConvId ? Number(urlConvId) : undefined
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");
  const [copiedId, setCopiedId] = useState<number | null>(null);

  // Academic Profile state
  const [academicProfile, setAcademicProfile] = useState<any>(null);
  const [isMarksModalOpen, setIsMarksModalOpen] = useState(false);

  // Escalation Modal state
  const [escalateData, setEscalateData] = useState<{
    isOpen: boolean;
    subject?: string;
    description?: string;
  }>({ isOpen: false });

  // Feedback state
  const [feedbackSuccessId, setFeedbackSuccessId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    loadConversations();
    loadAcademicProfile();
    if (urlConvId) {
      selectConversation(Number(urlConvId));
    }
  }, []);

  useEffect(() => {
    if (urlConvId && Number(urlConvId) !== activeConversationId) {
      selectConversation(Number(urlConvId));
    }
  }, [urlConvId]);

  const loadAcademicProfile = async () => {
    try {
      const res = await apiClient.getAcademicProfile();
      setAcademicProfile(res.data);
    } catch (err) {
      console.error("Error loading academic profile:", err);
    }
  };

  const loadConversations = async () => {
    try {
      const res = await apiClient.getConversations();
      setConversations(res.data);
      // If we have conversations and none active or in URL, pick first
      if (!activeConversationId && !urlConvId && res.data.length > 0) {
        if (!sessionStorage.getItem("pending_chat_query")) {
          selectConversation(res.data[0].id);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Check for pending query from dashboard
  useEffect(() => {
    const pending = sessionStorage.getItem("pending_chat_query");
    if (pending) {
      sessionStorage.removeItem("pending_chat_query");
      handleSend(pending);
    }
  }, []);

  const selectConversation = async (id: number) => {
    setActiveConversationId(id);
    setSearchParams({ id: id.toString() });
    try {
      const res = await apiClient.getConversation(id);
      setMessages(res.data.messages || []);
      setTimeout(scrollToBottom, 100);
    } catch {
      setMessages([]);
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await apiClient.createConversation();
      setConversations((prev) => [res.data, ...prev]);
      setActiveConversationId(res.data.id);
      setSearchParams({ id: res.data.id.toString() });
      setMessages([]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this conversation?")) return;
    try {
      await apiClient.deleteConversation(id);
      const updated = conversations.filter((c) => c.id !== id);
      setConversations(updated);
      if (activeConversationId === id) {
        if (updated.length > 0) {
          selectConversation(updated[0].id);
        } else {
          setActiveConversationId(undefined);
          setMessages([]);
          setSearchParams({});
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || inputText;
    if (!textToSend.trim() || loading) return;

    setInputText("");
    setLoading(true);

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      conversation_id: activeConversationId || 0,
      sender: "user",
      content: textToSend,
      escalation_suggested: false,
      sources: [],
      follow_up_suggestions: [],
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setTimeout(scrollToBottom, 50);

    try {
      const res = await apiClient.askQuestion({
        message: textToSend,
        conversation_id: activeConversationId,
      });

      // Update active conv ID if newly created
      if (!activeConversationId) {
        setActiveConversationId(res.data.conversation_id);
        setSearchParams({ id: res.data.conversation_id.toString() });
      }

      setMessages((prev) => {
        // Replace optimistic msg with real history, then append assistant reply
        return [...prev.slice(0, prev.length - 1), tempUserMsg, res.data];
      });

      // Refresh conversations list to update title & timestamp
      loadConversations();
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: Date.now() + 1,
        conversation_id: activeConversationId || 0,
        sender: "assistant",
        content: "I apologize, but I encountered a momentary problem accessing the academic knowledge base. Please try asking again.",
        escalation_suggested: true,
        sources: [],
        follow_up_suggestions: ["Contact my faculty member"],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      setTimeout(scrollToBottom, 100);
    }
  };

  const handleCopy = (id: number, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFeedback = async (msgId: number, rating: "like" | "dislike") => {
    try {
      await apiClient.submitFeedback(msgId, { rating });
      setFeedbackSuccessId(msgId);
      setTimeout(() => setFeedbackSuccessId(null), 2000);
    } catch {}
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchFilter.toLowerCase())
  );

  const formatInlineText = (text: string): React.ReactNode => {
    const parts: React.ReactNode[] = [];
    const regex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(text.slice(lastIndex, match.index));
      }
      const token = match[0];
      if (token.startsWith("`") && token.endsWith("`")) {
        parts.push(
          <code key={match.index} className="px-1.5 py-0.5 mx-0.5 rounded text-[11px] font-mono bg-[#EBE5FC]/80 text-[#5B4F8A] border border-[#DDD6FE]">
            {token.slice(1, -1)}
          </code>
        );
      } else if (token.startsWith("**") && token.endsWith("**")) {
        parts.push(
          <strong key={match.index} className="font-bold text-[#1F2937]">
            {token.slice(2, -2)}
          </strong>
        );
      } else if (token.startsWith("*") && token.endsWith("*")) {
        parts.push(
          <em key={match.index} className="italic text-[#4B515D]">
            {token.slice(1, -1)}
          </em>
        );
      }
      lastIndex = match.index + token.length;
    }
    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }
    return parts.length > 0 ? parts : text;
  };

  const renderMessageContent = (content: string) => {
    const lines = content.split("\n");
    const elements: React.ReactNode[] = [];
    let inCodeBlock = false;
    let codeLanguage = "";
    let codeBuffer: string[] = [];
    let tableBuffer: string[] = [];

    const flushTable = () => {
      if (tableBuffer.length > 0) {
        const tableLines = tableBuffer.filter((l) => l.trim().startsWith("|") && l.trim().endsWith("|"));
        if (tableLines.length >= 2) {
          const headerRow = tableLines[0].split("|").slice(1, -1).map((c) => c.trim());
          const dataRows = tableLines.slice(2).map((row) =>
            row.split("|").slice(1, -1).map((c) => c.trim())
          );

          elements.push(
            <div key={`table-${elements.length}`} className="overflow-x-auto my-2.5 border border-[#E8E6E1] rounded-xl shadow-2xs">
              <table className="w-full text-left border-collapse text-[11px]">
                <thead>
                  <tr className="bg-[#FAF9F6] border-b border-[#E8E6E1] text-[#6C727F]">
                    {headerRow.map((h, i) => (
                      <th key={i} className="p-2.5 font-semibold">
                        {formatInlineText(h)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataRows.map((r, rIdx) => (
                    <tr key={rIdx} className="border-b border-[#F0EFEB] hover:bg-[#FAF9F6]/50">
                      {r.map((cell, cIdx) => (
                        <td key={cIdx} className="p-2.5">
                          {formatInlineText(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }
        tableBuffer = [];
      }
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Fenced Code Block start/end
      if (trimmed.startsWith("```")) {
        if (tableBuffer.length > 0) flushTable();
        if (inCodeBlock) {
          // Closing code block
          const codeText = codeBuffer.join("\n");
          elements.push(
            <div key={`code-${elements.length}`} className="my-2.5 rounded-xl overflow-hidden border border-[#3E4451] bg-[#1E1E2E] text-white shadow-xs">
              <div className="flex items-center justify-between px-3 py-1.5 bg-[#282C34] text-[10px] text-[#ABB2BF] font-mono border-b border-[#3E4451]">
                <span>{codeLanguage || "code"}</span>
                <button
                  type="button"
                  onClick={() => navigator.clipboard.writeText(codeText)}
                  className="hover:text-white transition-colors flex items-center gap-1"
                >
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </button>
              </div>
              <pre className="p-3 text-[11px] font-mono overflow-x-auto text-[#ECEFF4] leading-relaxed">
                <code>{codeText}</code>
              </pre>
            </div>
          );
          inCodeBlock = false;
          codeBuffer = [];
          codeLanguage = "";
        } else {
          // Opening code block
          inCodeBlock = true;
          codeLanguage = trimmed.replace("```", "").trim();
          codeBuffer = [];
        }
        continue;
      }

      if (inCodeBlock) {
        codeBuffer.push(line);
        continue;
      }

      // Markdown Table row
      if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
        tableBuffer.push(line);
        continue;
      } else if (tableBuffer.length > 0) {
        flushTable();
      }

      // Headings
      if (trimmed.startsWith("### ")) {
        elements.push(
          <h4 key={`h4-${i}`} className="font-bold text-sm text-[#2D3139] mt-3 mb-1">
            {formatInlineText(trimmed.replace("### ", ""))}
          </h4>
        );
        continue;
      }
      if (trimmed.startsWith("## ")) {
        elements.push(
          <h3 key={`h3-${i}`} className="font-bold text-base text-[#2D3139] mt-3.5 mb-1.5 border-b border-[#E8E6E1] pb-1">
            {formatInlineText(trimmed.replace("## ", ""))}
          </h3>
        );
        continue;
      }
      if (trimmed.startsWith("# ")) {
        elements.push(
          <h2 key={`h2-${i}`} className="font-bold text-lg text-[#2D3139] mt-4 mb-2">
            {formatInlineText(trimmed.replace("# ", ""))}
          </h2>
        );
        continue;
      }

      // Bullet points
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        elements.push(
          <li key={`li-${i}`} className="ml-4 list-disc text-xs text-[#2D3139] my-0.5 leading-relaxed">
            {formatInlineText(trimmed.slice(2))}
          </li>
        );
        continue;
      }

      // Numbered lists
      const numMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
      if (numMatch) {
        elements.push(
          <div key={`num-${i}`} className="flex items-start gap-2 text-xs text-[#2D3139] my-0.5 leading-relaxed ml-1">
            <span className="font-semibold text-[#5B4F8A]">{numMatch[1]}.</span>
            <span>{formatInlineText(numMatch[2])}</span>
          </div>
        );
        continue;
      }

      // Normal lines / paragraphs
      if (trimmed === "") {
        elements.push(<div key={`sp-${i}`} className="h-1.5" />);
      } else {
        elements.push(
          <div key={`p-${i}`} className="text-xs text-[#2D3139] leading-relaxed">
            {formatInlineText(line)}
          </div>
        );
      }
    }

    if (inCodeBlock && codeBuffer.length > 0) {
      elements.push(
        <pre key={`code-end`} className="p-3 my-2 bg-[#1E1E2E] text-white rounded-xl text-[11px] font-mono overflow-x-auto">
          <code>{codeBuffer.join("\n")}</code>
        </pre>
      );
    }
    flushTable();

    return <div className="space-y-1">{elements}</div>;
  };

  return (
    <div className="flex h-[calc(100vh-8.5rem)] bg-white rounded-2xl border border-[#E8E6E1] shadow-xs overflow-hidden">
      {/* Left Chat History Sidebar */}
      <div className="w-72 bg-[#FAF9F6] border-r border-[#E8E6E1] flex flex-col shrink-0">
        <div className="p-3.5 border-b border-[#E8E6E1] space-y-2">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-[#5B4F8A] hover:bg-[#4E4377] text-white rounded-xl text-xs font-semibold shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Academic Chat</span>
          </button>

          {/* Search conversations */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#9CA3AF] absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search chat topics..."
              className="w-full bg-white border border-[#E2DFD7] rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-1 focus:ring-[#7C6EB0]"
            />
          </div>
        </div>

        {/* Conversation List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {filteredConversations.length === 0 ? (
            <div className="p-4 text-center text-xs text-[#6C727F]">
              No conversations found.
            </div>
          ) : (
            filteredConversations.map((c) => {
              const isActive = c.id === activeConversationId;
              return (
                <div
                  key={c.id}
                  onClick={() => selectConversation(c.id)}
                  className={`group flex items-center justify-between p-2.5 rounded-lg text-xs cursor-pointer transition-all ${
                    isActive
                      ? "bg-[#EBE5FC] text-[#5B4F8A] font-semibold border border-[#DDD6FE]"
                      : "text-[#4B515D] hover:bg-[#F3F0FF]/40"
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? "text-[#5B4F8A]" : "text-[#9CA3AF]"}`} />
                    <span className="truncate">{c.title}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-600 rounded transition-opacity"
                    title="Delete Chat"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Main Chat Conversation View */}
      <div className="flex-1 flex flex-col bg-[#FAF9F6]/40 overflow-hidden">
        {/* Academic Profile & Semester Quick Selector Header */}
        <div className="px-4 py-2.5 bg-white border-b border-[#E8E6E1] flex flex-wrap items-center justify-between gap-2 text-xs shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shrink-0">
              <GraduationCap className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="font-bold text-[#2D3139]">
                {academicProfile?.degree || "B.Tech"} {academicProfile?.branch || "ECE"} ({academicProfile?.regulation || "R23"})
              </span>
              <span className="text-[#9CA3AF]">·</span>
              <span className="text-[#6C727F]">
                {academicProfile?.institution || "Narasaraopeta Engineering College"}
              </span>
              <span className="text-[#9CA3AF]">·</span>
              <span className="font-mono text-[#5B4F8A] font-semibold bg-[#EBE5FC]/60 px-1.5 py-0.5 rounded border border-[#DDD6FE]/60">
                {academicProfile?.roll_number || user?.student_profile?.roll_number || "23471A05AR"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Quick semester inquiry pills */}
            <div className="hidden sm:flex items-center gap-1 bg-[#FAF9F6] p-0.5 rounded-lg border border-[#E2DFD7]">
              {["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"].map((sem) => (
                <button
                  key={sem}
                  onClick={() => handleSend(`What subjects are in ${sem}?`)}
                  className="px-1.5 py-0.5 rounded text-[10px] font-semibold text-[#4B515D] hover:bg-[#EBE5FC] hover:text-[#5B4F8A] transition-colors"
                  title={`Check ${sem} curriculum`}
                >
                  {sem}
                </button>
              ))}
            </div>

            <button
              onClick={() => setIsMarksModalOpen(true)}
              className="flex items-center gap-1 px-2.5 py-1 bg-[#F5F3FF] hover:bg-[#EBE5FC] text-[#5B4F8A] border border-[#DDD6FE] rounded-lg text-[11px] font-semibold transition-colors shadow-2xs"
              title="Import Official Marksheet CSV"
            >
              <UploadCloud className="w-3.5 h-3.5" />
              <span>Import Marksheet</span>
            </button>
          </div>
        </div>

        {/* Messages Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-lg mx-auto text-center p-6 space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shadow-xs">
                <Bot className="w-7 h-7" />
              </div>
              <div>
                <h3 className="font-bold text-lg text-[#2D3139]">
                  Hi {user?.full_name}! What can I help you understand today?
                </h3>
                <p className="text-xs text-[#6C727F] mt-1.5 leading-relaxed">
                  I'm your AI Academic Mentor for B.Tech (2023–2027 R23). I check university bylaws, examination schedules, attendance requirements, marks, and course syllabi to give you transparent, verified answers with source citations.
                </p>
              </div>

              {/* Sample question cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left pt-2">
                {[
                  { q: "What are my 1-1 semester marks?", desc: "View verified scores, grades & SGPA" },
                  { q: "What is my current CGPA?", desc: "Calculated across completed semesters" },
                  { q: "What subjects are in 2-1?", desc: "Check verified R23 curriculum & credits" },
                  { q: "What is my current attendance?", desc: "Inspect attendance % & condonation status" },
                  { q: "Which subjects have backlogs?", desc: "Check active vs. cleared backlogs" },
                  { q: "What is the R23 passing rule?", desc: "35% external & 40% aggregate criteria" },
                ].map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSend(item.q)}
                    className="p-3 bg-white border border-[#E2DFD7] rounded-xl hover:border-[#DDD6FE] hover:bg-[#FBFBFA] transition-all text-xs group"
                  >
                    <div className="font-semibold text-[#2D3139] group-hover:text-[#5B4F8A]">
                      {item.q}
                    </div>
                    <div className="text-[11px] text-[#6C727F] mt-0.5">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m) => {
              const isUser = m.sender === "user";
              return (
                <div
                  key={m.id}
                  className={`flex gap-3 max-w-3xl ${isUser ? "ml-auto justify-end" : "mr-auto"}`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shrink-0 shadow-xs">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`space-y-2 max-w-xl ${isUser ? "items-end" : ""}`}>
                    {/* Message Bubble */}
                    <div
                      className={`p-4 rounded-2xl text-xs leading-relaxed shadow-xs ${
                        isUser
                          ? "bg-[#5B4F8A] text-white rounded-tr-xs"
                          : "bg-white border border-[#E8E6E1] text-[#2D3139] rounded-tl-xs"
                      }`}
                    >
                      {renderMessageContent(m.content)}

                      {/* Escalation Button if low confidence or faculty escalation suggested */}
                      {!isUser && m.escalation_suggested && (
                        <div className="mt-3 pt-3 border-t border-[#E8E6E1] flex items-center justify-between gap-2">
                          <div className="flex items-center gap-1.5 text-[#B47C57] font-semibold text-[11px]">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            <span>Faculty verification advised</span>
                          </div>
                          <button
                            onClick={() =>
                              setEscalateData({
                                isOpen: true,
                                subject: "Academic Query Escalation",
                                description: `Inquiry details: ${m.content}`,
                              })
                            }
                            className="flex items-center gap-1 px-3 py-1.5 bg-[#B47C57] hover:bg-[#9E6945] text-white text-[11px] font-semibold rounded-lg shadow-xs transition-colors"
                          >
                            <LifeBuoy className="w-3.5 h-3.5" />
                            <span>Contact Faculty</span>
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Source Citations Cards */}
                    {!isUser && m.sources && m.sources.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <div className="text-[11px] font-semibold text-[#6C727F] flex items-center gap-1">
                          <BookOpen className="w-3 h-3 text-[#62826F]" />
                          <span>Supporting Document Sources ({m.sources.length}):</span>
                        </div>
                        <div className="grid grid-cols-1 gap-1.5">
                          {m.sources.map((src, i) => (
                            <CitationCard key={i} source={src} />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Assistant message action controls */}
                    {!isUser && (
                      <div className="flex items-center justify-between pt-1 text-[11px] text-[#6C727F]">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleCopy(m.id, m.content)}
                            className="hover:text-[#2D3139] flex items-center gap-1 transition-colors"
                            title="Copy response"
                          >
                            {copiedId === m.id ? (
                              <>
                                <Check className="w-3 h-3 text-[#62826F]" />
                                <span className="text-[#62826F] font-medium">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3 h-3" />
                                <span>Copy</span>
                              </>
                            )}
                          </button>

                          <span>·</span>

                          <button
                            onClick={() => handleFeedback(m.id, "like")}
                            className="hover:text-[#62826F] flex items-center gap-1 transition-colors"
                            title="Helpful response"
                          >
                            <ThumbsUp className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => handleFeedback(m.id, "dislike")}
                            className="hover:text-red-600 flex items-center gap-1 transition-colors"
                            title="Inaccurate response"
                          >
                            <ThumbsDown className="w-3 h-3" />
                          </button>

                          {feedbackSuccessId === m.id && (
                            <span className="text-[#62826F] font-medium text-[10px]">
                              Thanks for feedback!
                            </span>
                          )}
                        </div>

                        {m.confidence_score !== undefined && (
                          <span className="text-[10px] text-[#9CA3AF]">
                            Confidence: {Math.round(m.confidence_score * 100)}%
                          </span>
                        )}
                      </div>
                    )}

                    {/* Follow-up suggestion pills */}
                    {!isUser && m.follow_up_suggestions && m.follow_up_suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1.5">
                        {m.follow_up_suggestions.map((sug, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSend(sug)}
                            className="text-[11px] px-2.5 py-1 rounded-full bg-[#F5F3FF] hover:bg-[#EBE5FC] text-[#5B4F8A] border border-[#DDD6FE] transition-colors flex items-center gap-1"
                          >
                            <span>{sug}</span>
                            <ChevronRight className="w-2.5 h-2.5" />
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-[#5B4F8A] text-white flex items-center justify-center shrink-0 text-xs font-bold">
                      {user?.full_name?.charAt(0) || "U"}
                    </div>
                  )}
                </div>
              );
            })
          )}

          {/* Typing Indicator */}
          {loading && (
            <div className="flex gap-3 max-w-xl mr-auto">
              <div className="w-8 h-8 rounded-xl bg-[#EBE5FC] border border-[#DDD6FE] text-[#5B4F8A] flex items-center justify-center shrink-0 shadow-xs">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-3.5 bg-white border border-[#E8E6E1] rounded-2xl rounded-tl-xs shadow-xs flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-[#7C6EB0] rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-2 h-2 bg-[#7C6EB0] rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-2 h-2 bg-[#7C6EB0] rounded-full animate-bounce" />
                </div>
                <span className="text-xs text-[#6C727F] font-medium">
                  Retrieving authorized academic sources...
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3.5 bg-white border-t border-[#E8E6E1]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask an academic question (e.g. attendance rules, exam dates, deadlines)..."
              disabled={loading}
              className="flex-1 bg-[#FBFBFA] border border-[#E2DFD7] rounded-xl px-4 py-2.5 text-xs text-[#2D3139] placeholder-[#9CA3AF] focus:outline-none focus:ring-2 focus:ring-[#7C6EB0] focus:bg-white transition-all"
            />
            <button
              type="submit"
              disabled={loading || !inputText.trim()}
              className="px-4 py-2.5 bg-[#5B4F8A] hover:bg-[#4E4377] text-white font-medium rounded-xl text-xs shadow-xs transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              <span>Ask</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
          <div className="mt-1.5 text-[10px] text-center text-[#6C727F]">
            AI responses are strictly grounded in official university documents. Never fabricate policies.
          </div>
        </div>
      </div>

      {/* Escalation Modal */}
      <EscalateModal
        isOpen={escalateData.isOpen}
        onClose={() => setEscalateData({ isOpen: false })}
        initialSubject={escalateData.subject}
        initialDescription={escalateData.description}
        conversationId={activeConversationId}
      />

      {/* Marksheet CSV Import Modal */}
      <AcademicMarksModal
        isOpen={isMarksModalOpen}
        onClose={() => setIsMarksModalOpen(false)}
        onImportSuccess={() => {
          handleSend("What are my 1-1 semester marks?");
        }}
      />
    </div>
  );
};
