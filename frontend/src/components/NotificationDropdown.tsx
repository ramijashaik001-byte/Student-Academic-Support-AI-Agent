import React, { useState, useEffect } from "react";
import { Bell, CheckCheck, Clock, ExternalLink } from "lucide-react";
import { apiClient } from "../api/client";
import type { NotificationItem } from "../types";
import { useAuth } from "../context/AuthContext";

export const NotificationDropdown: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(false);
  const { unreadCount, refreshUnreadCount } = useAuth();

  const loadNotifications = async () => {
    setLoading(true);
    try {
      const res = await apiClient.getNotifications();
      setNotifications(res.data);
      await refreshUnreadCount();
    } catch {
      // Ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadNotifications();
    }
  }, [isOpen]);

  const handleMarkRead = async (id: number) => {
    try {
      await apiClient.markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      await refreshUnreadCount();
    } catch {}
  };

  const handleMarkAllRead = async () => {
    try {
      await apiClient.markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      await refreshUnreadCount();
    } catch {}
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-[#5A606D] hover:text-[#2D3139] rounded-lg hover:bg-[#F3F2EE] transition-colors focus:outline-none"
        title="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex items-center justify-center w-4 h-4 text-[10px] font-bold text-white bg-[#7C6EB0] rounded-full">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-lg border border-[#E8E6E1] z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
            <div className="p-3.5 bg-[#FAF9F6] text-[#2D3139] flex items-center justify-between border-b border-[#E8E6E1]">
              <div className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-[#7C6EB0]" />
                <span className="font-semibold text-sm">Notifications</span>
                {unreadCount > 0 && (
                  <span className="bg-[#EBE5FC] text-[#5B4F8A] text-[10px] font-medium px-2 py-0.5 rounded-full border border-[#DDD6FE]">
                    {unreadCount} new
                  </span>
                )}
              </div>
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllRead}
                  className="text-[11px] text-[#62826F] hover:text-[#466352] flex items-center gap-1 transition-colors font-medium"
                >
                  <CheckCheck className="w-3.5 h-3.5" />
                  Mark all read
                </button>
              )}
            </div>

            <div className="max-h-80 overflow-y-auto divide-y divide-[#E8E6E1]">
              {loading ? (
                <div className="p-6 text-center text-xs text-[#6C727F]">
                  Loading notifications...
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-8 text-center text-[#6C727F] text-xs">
                  No notifications yet. You're all caught up!
                </div>
              ) : (
                notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`p-3 text-xs transition-colors hover:bg-[#FAF9F6] ${
                      !n.is_read ? "bg-[#F5F3FF]/60" : ""
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h4
                        className={`font-medium leading-snug ${
                          !n.is_read ? "text-[#5B4F8A] font-bold" : "text-[#2D3139]"
                        }`}
                      >
                        {n.title}
                      </h4>
                      {!n.is_read && (
                        <button
                          onClick={() => handleMarkRead(n.id)}
                          className="shrink-0 text-[#62826F] hover:text-[#466352] font-medium text-[10px]"
                        >
                          Mark read
                        </button>
                      )}
                    </div>
                    <p className="text-[#4B515D] mt-1 leading-relaxed text-[11px]">
                      {n.message}
                    </p>
                    <div className="mt-2 flex items-center justify-between text-[10px] text-[#9CA3AF]">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(n.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                          month: "short",
                          day: "numeric",
                        })}
                      </span>
                      {n.link_url && (
                        <a
                          href={n.link_url}
                          onClick={() => setIsOpen(false)}
                          className="text-[#5B4F8A] hover:text-[#433878] flex items-center gap-0.5 font-medium"
                        >
                          View <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
