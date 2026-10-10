import re
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple


class QuestionCategory(str, Enum):
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"
    PERSONAL_ACADEMIC = "PERSONAL_ACADEMIC"
    CURRICULUM_REGULATION = "CURRICULUM_REGULATION"
    DOCUMENT_SYLLABUS = "DOCUMENT_SYLLABUS"
    CALCULATION = "CALCULATION"
    FOLLOW_UP = "FOLLOW_UP"


class QuestionClassifier:
    """
    Intelligently routes student messages to prevent forcing general questions
    into university document searches or academic database queries.
    """

    FOLLOW_UP_PATTERNS = [
        (r'^(make it|make this|keep it)\s+(shorter|brief|concise|short|simple)', "SHORTER"),
        (r'^(summarize|shorten|condense)\s+(it|this|that|the above)', "SHORTER"),
        (r'^(give me|show me|provide|another)\s+(an?\s+)?example\b', "EXAMPLE"),
        (r'^(can you\s+)?(give|provide)\s+(an?\s+)?example\b', "EXAMPLE"),
        (r'^(explain|what are|tell me)\s+(its|the|their)\s+(advantages|benefits|pros|disadvantages|cons|drawbacks)', "ADVANTAGES"),
        (r'^(explain|tell|rephrase)\s+(this|it|that)?\s*(in\s+simple\s+(words|terms|language)|simply|like i(?:\'m| am) five|eli5)', "SIMPLIFY"),
        (r'^(show|give|write)\s+(me\s+)?(the\s+)?(code|program|implementation|snippet)\b', "CODE"),
        (r'^(why\?|why is that\?|how so\?|tell me more|elaborate\b)', "ELABORATE"),
    ]

    @classmethod
    def classify(
        cls,
        query: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[QuestionCategory, Dict[str, Any]]:
        """
        Returns (category, metadata) where metadata contains detected parameters
        like follow_up_action, detected_semester, or target_topic.
        """
        q = query.strip()
        q_lower = q.lower()
        meta: Dict[str, Any] = {}

        # 1. Check for percentage follow-up e.g. "What if I have 72%?"
        pct_match = re.search(r'(\d{1,3}(?:\.\d+)?)\s*%', q_lower)
        if pct_match and (
            any(w in q_lower for w in ["what if", "if i have", "attendance", "eligible", "detain", "condon", "enough"])
            or any("attendance" in h.get("content", "").lower() for h in (history or [])[-2:])
        ):
            meta["percentage"] = float(pct_match.group(1))
            meta["context_topic"] = "attendance"
            return QuestionCategory.CURRICULUM_REGULATION, meta

        # 1.5 Check for Conversational Follow-up patterns
        for pattern, action in cls.FOLLOW_UP_PATTERNS:
            if re.search(pattern, q_lower):
                meta["follow_up_action"] = action
                meta["context_topic"] = cls._extract_topic_from_history(history)
                return QuestionCategory.FOLLOW_UP, meta

        # Generic pronouns pointing to previous turn ("its advantages", "how does it work", "example of this", "what about tomorrow")
        if history and (len(q.split()) <= 6) and (any(w in q_lower for w in ["it", "its", "this", "that", "these", "those"]) or "what about tomorrow" in q_lower):
            if "tomorrow" in q_lower or "monday" in q_lower or "next" in q_lower:
                return QuestionCategory.CURRICULUM_REGULATION, meta
            if any(w in q_lower for w in ["example", "instance"]):
                meta["follow_up_action"] = "EXAMPLE"
                meta["context_topic"] = cls._extract_topic_from_history(history)
                return QuestionCategory.FOLLOW_UP, meta
            if any(w in q_lower for w in ["advantage", "benefit", "pro", "disadvantage", "drawback"]):
                meta["follow_up_action"] = "ADVANTAGES"
                meta["context_topic"] = cls._extract_topic_from_history(history)
                return QuestionCategory.FOLLOW_UP, meta
            if any(w in q_lower for w in ["simple", "simpler", "simply"]):
                meta["follow_up_action"] = "SIMPLIFY"
                meta["context_topic"] = cls._extract_topic_from_history(history)
                return QuestionCategory.FOLLOW_UP, meta
            if any(w in q_lower for w in ["short", "shorter", "brief"]):
                meta["follow_up_action"] = "SHORTER"
                meta["context_topic"] = cls._extract_topic_from_history(history)
                return QuestionCategory.FOLLOW_UP, meta

        # 2. Check for Personal Academic queries (Must belong to student's records)
        personal_patterns = [
            r'\bmy\s+(marks?|score|grades?|results?|sgpa|cgpa|gpa|attendance|backlogs?|profile|roll\s*number)\b',
            r'\bwhat\s+(is|are)\s+my\b',
            r'\bhow\s+many\s+marks?\s+did\s+i\b',
            r'\bdid\s+i\s+pass\b',
            r'\bhave\s+i\s+failed\b',
            r'\bwhich\s+subjects?\s+have\s+i\s+failed\b',
            r'\bdo\s+i\s+have\s+(any\s+)?backlogs?\b',
            r'\bmy\s+attendance\b',
            r'\bam\s+i\s+eligible\b',
            r'\bcan\s+i\s+write\s+(the\s+)?exam\b',
            r'\b([1-4][-_][1-2])\s+(attendance|marks?|grades?|results?|score)\b',
            r'\battendance\s+(in|for|of)?\s*([1-4][-_][1-2])\b',
            r'\battendance\s+(percentage|report|status)\b',
            r'\bwhich\s+subjects\s+need\s+attention\b',
            r'\bsemester\s+results\b',
            r'\b(my\s+)?attendance\b'
        ]
        if any(re.search(p, q_lower) for p in personal_patterns):
            return QuestionCategory.PERSONAL_ACADEMIC, meta

        # 3. Check for Calculation queries
        if re.search(r'\bcalculate\s+(my\s+)?(cgpa|sgpa|gpa|percentage|attendance)\b', q_lower):
            return QuestionCategory.CALCULATION, meta
        if re.search(r'\bhow\s+many\s+classes\s+(can\s+i\s+miss|do\s+i\s+need|should\s+i\s+attend)\b', q_lower):
            return QuestionCategory.CALCULATION, meta

        # 4. Check for Syllabus, Units or Document queries
        if re.search(r'\b(summarize|explain)\s+(this\s+)?(uploaded\s+)?(pdf|document|docx|file)\b', q_lower):
            return QuestionCategory.DOCUMENT_SYLLABUS, meta
        if re.search(r'\bunit\s*[1-5]\b', q_lower):
            return QuestionCategory.CURRICULUM_REGULATION, meta
        if re.search(r'\bfrom\s+(my\s+)?syllabus\b', q_lower):
            return QuestionCategory.DOCUMENT_SYLLABUS, meta

        # 5. Check for Official Curriculum, Timetables, Schedules, Holidays, Deadlines, Planning
        curriculum_patterns = [
            r'\bsubjects?\s+(do\s+i\s+have\s+in|are\s+in|in)\s+([1-4][-_][1-2])\b',
            r'\b([1-4][-_][1-2])\s+subjects?\b',
            r'\bcurriculum\s+(for|in)\s+([1-4][-_][1-2])\b',
            r'\b(third|fourth|first|second)[\s-]year\s+subjects?\b',
            r'\b[1-4](?:st|nd|rd|th)\s+year\s+subjects?\b',
            r'\bcurrent\s+semester\s+subjects\b',
            r'\bcourses\s+(do\s+i\s+have|in\s+this\s+semester)\b',
            r'\bcredits\s+for\s+each\s+subject\b',
            r'\b(timetable|class\s*schedule|schedule\s*today|classes\s*today|classes\s*tomorrow)\b',
            r'\bwhat\s+about\s+tomorrow\b',
            r'\bnext\s+class\b',
            r'\bclass\s+at\s+\d+\b',
            r'\bweekly\s+timetable\b',
            r'\bfirst\s+class\s+on\s+monday\b',
            r'\btimetable\s+changed\b',
            r'\b(when\s+is\s+my\s+)?(?:edc|signals|stld|ptsp|dbms|python)\s+(?:exam|class)\b',
            r'\b(next\s+exam|examination\s+schedule|exam\s+timetable|exams\s+in\s+date\s+order)\b',
            r'\b(holiday|holidays|vacation|is\s+tomorrow\s+a\s+holiday)\b',
            r'\b(when\s+does\s+the\s+semester\s+start|semester\s+end|academic\s+calendar)\b',
            r'\b(assignments?\s+pending|pending\s+assignments?|assignments?\s+due|deadlines?\s+this\s+week)\b',
            r'\b(project\s+deadlines?|submission\s+requirements?)\b',
            r'\b(deadline\s+for\s+registration|fee\s+payment\s+deadline|last\s+date)\b',
            r'\b(practicals?|lab\s+sessions?)\b',
            r'\b(who\s+teaches|where\s+is\s+my\s+class|room\s+number)\b',
            r'\b(notes\s+for|previous\s+question\s+papers?|pyq|formula\s+sheet)\b',
            r'\b(study\s+plan|study\s+schedule)\b',
            r'\b(notice|circular|latest\s+notice)\b',
            r'\b(minimum\s+)?attendance\s+(rule|rules|policy|criteria|requirement|bylaws)\b',
            r'\b(r23|autonomous)\s+(regulation|rule|policy|passing|detention|condonation|grading)\b',
            r'\bpassing\s+(rule|criteria|minimum|mark)\b',
            r'\bdetention\s+(rule|policy|criteria)\b',
            r'\bcondonation\s+(fee|rule|policy|percentage)\b',
            r'\bgrading\s+(system|scale|formula)\b',
            r'\bwhen\s+are\s+(the\s+)?(mid|semester|end)\s+(exams?|examinations?)\b',
            r'\bexam\s+(timetable|schedule|dates?)\b'
        ]
        if any(re.search(p, q_lower) for p in curriculum_patterns):
            return QuestionCategory.CURRICULUM_REGULATION, meta

        # 6. Default to General Knowledge (educational, technical, programming, definitions)
        return QuestionCategory.GENERAL_KNOWLEDGE, meta

    @staticmethod
    def _extract_topic_from_history(history: Optional[List[Dict[str, str]]]) -> Optional[str]:
        if not history:
            return None

        for msg in reversed(history):
            content = msg.get("content", "").strip()
            if not content:
                continue

            match = re.search(r'\b(?:what\s+is|what\s+are|explain|define|tell\s+me\s+about)\s+([a-zA-Z0-9_\s\+\#]{2,30})[\?\.]?', content, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                candidate = re.sub(r'^(an?|the)\s+', '', candidate, flags=re.IGNORECASE)
                if candidate and len(candidate.split()) <= 4:
                    return candidate

            bold_match = re.search(r'\*\*([A-Za-z0-9\s\(\)\-]{3,35})\*\*', content)
            if bold_match:
                topic = bold_match.group(1).strip()
                if "semester" not in topic.lower() and "result" not in topic.lower() and "attendance" not in topic.lower():
                    return topic

        return None
