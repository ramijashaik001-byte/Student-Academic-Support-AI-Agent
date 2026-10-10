import React, { useState } from "react";
import { BookOpen, ChevronDown, ChevronUp, FileText, CheckCircle2 } from "lucide-react";
import type { AnswerSource } from "../types";

interface Props {
  source: AnswerSource;
}

export const CitationCard: React.FC<Props> = ({ source }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-[#D1E0D7] bg-[#F0F5F2] rounded-lg p-2.5 text-xs transition-all hover:border-[#B4CBB9]">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between text-left gap-2 text-[#2D3139] font-medium"
      >
        <div className="flex items-center gap-1.5 min-w-0">
          <BookOpen className="w-3.5 h-3.5 text-[#466352] shrink-0" />
          <span className="truncate font-semibold text-[#344E41]">{source.document_title}</span>
          <span className="text-[#9CA3AF]">·</span>
          <span className="text-[#4B515D] bg-white px-1.5 py-0.5 rounded border border-[#E2DFD7] text-[11px] shrink-0">
            Page {source.page_number || 1}
          </span>
          {source.section && (
            <span className="text-[#6C727F] text-[11px] truncate hidden sm:inline">
              ({source.section})
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5 shrink-0 text-[#6C727F]">
          <span className="text-[10px] text-[#344E41] font-medium bg-[#E2EBE5] px-1.5 py-0.5 rounded border border-[#D1E0D7]">
            {Math.round((source.relevance_score || 0.8) * 100)}% match
          </span>
          {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {expanded && (
        <div className="mt-2 pt-2 border-t border-[#D1E0D7] text-[#2D3139] leading-relaxed bg-white p-2.5 rounded-lg border border-[#E8E6E1]">
          <div className="flex items-center gap-1 text-[11px] font-semibold text-[#466352] mb-1">
            <FileText className="w-3 h-3 text-[#466352]" />
            Verified Document Excerpt:
          </div>
          <p className="italic bg-[#FAF9F6] p-2 rounded border border-[#E8E6E1] font-mono text-[11px] text-[#4B515D]">
            "{source.excerpt}"
          </p>
        </div>
      )}
    </div>
  );
};
