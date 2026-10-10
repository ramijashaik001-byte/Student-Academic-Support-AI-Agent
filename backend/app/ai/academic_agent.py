import json
import re
from typing import List, Dict, Any, Optional, Tuple
import httpx
from app.config import settings

SYSTEM_INSTRUCTION = """You are a helpful, accurate, friendly AI Student Academic Support Agent. You can answer general knowledge questions, explain technical concepts, help with programming, support exam preparation, and retrieve a student's personal academic information when the relevant data is available.

Always understand the user's actual question before deciding how to answer. Do not restrict yourself to academic database queries. For general questions, provide a direct and accurate answer using your language-model capabilities. For personal academic questions, retrieve the correct records and never invent personal information. For document-specific questions, use relevant source documents. For calculations, show the correct working when useful. Remember conversational context for follow-up questions. Explain difficult topics in simple language and adapt the answer length to the user's request. If information is missing or uncertain, say so honestly. Never fabricate results, citations, syllabus details, or capabilities."""


class AcademicAgent:
    def __init__(self):
        self.settings = settings

    def generate_response(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        retrieved_sources: List[Dict[str, Any]],
        user_name: str = "Student",
        course_name: Optional[str] = None,
        db: Optional[Any] = None,
        student_id: Optional[int] = None,
        category: Optional[Any] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinates answer generation using live LLM (Gemini/OpenAI),
        academic tool router, general knowledge engine, or local grounded mentor engine.
        """
        from app.ai.question_classifier import QuestionClassifier, QuestionCategory
        from app.ai.general_knowledge_engine import GeneralKnowledgeEngine

        if category is None or meta is None:
            category, meta = QuestionClassifier.classify(query, history=conversation_history)

        cat_val = category.value if hasattr(category, "value") else str(category)

        # 1. Personal Academic, Calculation, Timetable, Exams, or Curriculum/Regulations check
        if db is not None and student_id is not None:
            try:
                from app.ai.academic_intent_router import AcademicIntentRouter
                academic_res = AcademicIntentRouter.try_handle_academic_query(
                    db=db,
                    student_id=student_id,
                    query=query,
                    conversation_history=conversation_history,
                    user_name=user_name
                )
                if academic_res:
                    return academic_res
            except Exception as e:
                print(f"AcademicIntentRouter notice: {e}")

        # Check exception keywords
        exception_keywords = ["medical leave exception", "condonation waiver", "dispute marks", "re-evaluation appeal", "canteen", "complaint against", "special permission", "biryani", "hostel mess"]
        is_exception_query = any(k in query.lower() for k in exception_keywords)
        max_score = max([s["relevance_score"] for s in retrieved_sources], default=0.0)

        # 2. General Knowledge or Conversational Follow-up check
        # Only route to general knowledge if NOT an exception query and NOT explicitly grounded with relevant documents
        has_gemini = bool(settings.GEMINI_API_KEY and settings.LLM_PROVIDER in ["gemini", "auto"])
        has_openai = bool(settings.OPENAI_API_KEY and settings.LLM_PROVIDER in ["openai", "auto"])

        if not is_exception_query and max_score < 0.4 and cat_val in ["GENERAL_KNOWLEDGE", "FOLLOW_UP"]:
            # If live LLM configured, call without attaching irrelevant college document snippets
            if has_gemini:
                llm_res = self._call_gemini(query, conversation_history, [], user_name)
                if llm_res:
                    return {
                        "content": llm_res["content"],
                        "confidence_score": 0.95,
                        "escalation_suggested": False,
                        "sources": [],
                        "follow_up_suggestions": self._generate_follow_ups(query, [], False)
                    }
            elif has_openai:
                llm_res = self._call_openai(query, conversation_history, [], user_name)
                if llm_res:
                    return {
                        "content": llm_res["content"],
                        "confidence_score": 0.95,
                        "escalation_suggested": False,
                        "sources": [],
                        "follow_up_suggestions": self._generate_follow_ups(query, [], False)
                    }

            # Offline/Local intelligent general knowledge answering
            gk_res = GeneralKnowledgeEngine.answer_question(
                query=query,
                category=cat_val,
                metadata=meta or {},
                history=conversation_history,
                user_name=user_name
            )
            if gk_res:
                return gk_res

        # 3. Document / Syllabus / Fallback processing
        max_score = max([s["relevance_score"] for s in retrieved_sources], default=0.0)
        exception_keywords = ["medical leave exception", "condonation waiver", "dispute marks", "re-evaluation appeal", "canteen", "complaint against", "special permission"]
        is_exception_query = any(k in query.lower() for k in exception_keywords)

        llm_response = None
        if has_gemini:
            llm_response = self._call_gemini(query, conversation_history, retrieved_sources, user_name)
        elif has_openai:
            llm_response = self._call_openai(query, conversation_history, retrieved_sources, user_name)

        if llm_response:
            answer_text = llm_response["content"]
            confidence = llm_response.get("confidence_score", max_score)
            escalation_suggested = llm_response.get("escalation_suggested", (max_score < settings.CONFIDENCE_THRESHOLD or is_exception_query))
        else:
            answer_text, confidence, escalation_suggested = self._grounded_fallback_mentor(
                query=query,
                history=conversation_history,
                sources=retrieved_sources,
                user_name=user_name,
                is_exception=is_exception_query
            )

        valid_sources = []
        if retrieved_sources and max_score >= 0.25:
            for s in retrieved_sources[:3]:
                valid_sources.append({
                    "document_id": s.get("document_id"),
                    "document_title": s.get("document_title", "College Document"),
                    "page_number": s.get("page_number", 1),
                    "section": s.get("section_heading", "General"),
                    "excerpt": s.get("content", "")[:280] + ("..." if len(s.get("content", "")) > 280 else ""),
                    "relevance_score": s.get("relevance_score", 0.8)
                })

        follow_ups = self._generate_follow_ups(query, retrieved_sources, escalation_suggested)

        return {
            "content": answer_text,
            "confidence_score": round(confidence, 2),
            "escalation_suggested": escalation_suggested,
            "sources": valid_sources if not escalation_suggested or valid_sources else [],
            "follow_up_suggestions": follow_ups
        }

    def _grounded_fallback_mentor(
        self,
        query: str,
        history: List[Dict[str, str]],
        sources: List[Dict[str, Any]],
        user_name: str,
        is_exception: bool
    ) -> Tuple[str, float, bool]:
        """
        Humanized deterministic mentor that extracts answers directly from verified sources.
        """
        q_lower = query.strip().lower()

        # Handle greetings
        if re.match(r'^(hi|hello|hey|good morning|good afternoon|greetings)\b', q_lower):
            greeting = f"Hello {user_name}! I'm your AI Academic Support Assistant. How can I help you today? You can ask me about course syllabi, exam schedules, attendance rules, or assignment deadlines."
            return greeting, 0.95, False

        # No sources found or very low score
        max_score = max([s["relevance_score"] for s in sources], default=0.0)
        if not sources or max_score < settings.CONFIDENCE_THRESHOLD:
            msg = (
                f"Hello {user_name}. I searched our college documents for **\"{query}\"**, but I couldn't find "
                "verified official information on this specific topic.\n\n"
                "To ensure you don't receive inaccurate details, I recommend submitting this inquiry "
                "to your course faculty or academic department using the button below."
            )
            return msg, round(max_score, 2), True

        # Check if the query asks about attendance
        if any(w in q_lower for w in ["attendance", "present", "absent", "%", "condonation", "detention"]):
            best_chunk = next((s for s in sources if "attendance" in s["content"].lower() or "condonation" in s["content"].lower()), sources[0])
            content = best_chunk["content"]
            title = best_chunk["document_title"]
            page = best_chunk.get("page_number", 1)

            # Follow up context detection (e.g. "what if I have 72%")
            pct_match = re.search(r'(\d{1,2})%', q_lower)
            if pct_match:
                pct = int(pct_match.group(1))
                if pct >= 75:
                    resp = (
                        f"Great news! With **{pct}%** attendance, you comfortably meet the university requirement. "
                        f"According to **{title}** (Page {page}), students with 75% or higher are directly eligible "
                        "to appear for semester end examinations."
                    )
                    return resp, 0.92, False
                elif 65 <= pct < 75:
                    resp = (
                        f"With **{pct}%** attendance, you fall into the condonation bracket (65% to 74%).\n\n"
                        f"According to **{title}** (Page {page}):\n"
                        "- Attendance between 65% and 74% may be condoned on valid medical grounds or university-authorized activities.\n"
                        "- You must submit a formal medical certificate and pay the prescribed condonation fee before the deadline.\n\n"
                        "Would you like me to connect you with your academic advisor or HOD to initiate the condonation request?"
                    )
                    return resp, 0.90, True
                else:
                    resp = (
                        f"With **{pct}%** attendance, your attendance is below the minimum 65% threshold required for condonation.\n\n"
                        f"According to the official policy in **{title}** (Page {page}), students with below 65% attendance "
                        "face detention and will not be eligible to write semester examinations for this term. "
                        "I strongly encourage you to speak directly with your department head or faculty mentor."
                    )
                    return resp, 0.90, True

            # General attendance explanation
            resp = (
                f"Here is the official attendance policy summarized from **{title}** (Page {page}):\n\n"
                f"{content}\n\n"
                "• **Minimum Required:** 75% overall attendance.\n"
                "• **Medical Condonation:** Allowed between 65% and 74% with valid certificates.\n"
                "• **Detention:** Less than 65% results in detention for the academic term."
            )
            return resp, round(max_score, 2), False

        # Check if the query asks about exams or timetables
        if any(w in q_lower for w in ["exam", "timetable", "mid semester", "schedule", "when are my"]):
            best_chunk = next((s for s in sources if any(k in s["content"].lower() for k in ["exam", "date", "time", "cs301", "hall"])), sources[0])
            title = best_chunk["document_title"]
            page = best_chunk.get("page_number", 1)
            content = best_chunk["content"]

            resp = (
                f"I found the verified examination details in **{title}** (Page {page}):\n\n"
                f"{content}\n\n"
                "Please make sure to carry your college identity card and hall ticket. Entry closes 15 minutes before exam commencement."
            )
            return resp, round(max_score, 2), False

        # General grounded response from top chunk
        top_chunk = sources[0]
        title = top_chunk["document_title"]
        page = top_chunk.get("page_number", 1)
        section = top_chunk.get("section_heading", "Overview")
        content = top_chunk["content"]

        resp = (
            f"Based on **{title}** ({section}, Page {page}), here is the relevant academic information:\n\n"
            f"{content}\n\n"
            "If you need further clarification or step-by-step assistance, feel free to ask!"
        )
        return resp, round(max_score, 2), is_exception

    def _call_gemini(self, query: str, history: List[Dict[str, str]], sources: List[Dict[str, Any]], user_name: str) -> Optional[Dict[str, Any]]:
        try:
            api_key = settings.GEMINI_API_KEY
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.MODEL_NAME}:generateContent?key={api_key}"

            context_snippets = "\n\n".join([
                f"[Source: {s['document_title']} | Page: {s.get('page_number', 1)} | Section: {s.get('section_heading', 'N/A')}]\n{s['content']}"
                for s in sources[:4]
            ])

            conversation_str = ""
            for h in history[-4:]:
                conversation_str += f"{h['sender'].upper()}: {h['content']}\n"

            user_prompt = f"""Verified Academic Document Excerpts:
{context_snippets if context_snippets else "No matching documents found."}

Recent Conversation:
{conversation_str}

Student ({user_name}): {query}

Instructions:
Answer the student respectfully and accurately. Cite document titles and page numbers. If facts are not in the text, state so and advise contacting faculty."""

            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{SYSTEM_INSTRUCTION}\n\n{user_prompt}"}]}
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 600,
                }
            }

            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    max_score = max([s["relevance_score"] for s in sources], default=0.0)
                    needs_escalation = "escalate" in text.lower() or "faculty" in text.lower() and max_score < 0.5
                    return {
                        "content": text,
                        "confidence_score": round(max_score, 2),
                        "escalation_suggested": needs_escalation
                    }
        except Exception as e:
            print(f"Gemini API request note: {e}")
        return None

    def _call_openai(self, query: str, history: List[Dict[str, str]], sources: List[Dict[str, Any]], user_name: str) -> Optional[Dict[str, Any]]:
        try:
            api_key = settings.OPENAI_API_KEY
            url = "https://api.openai.com/v1/chat/completions"

            context_snippets = "\n\n".join([
                f"[Source: {s['document_title']} | Page: {s.get('page_number', 1)}]\n{s['content']}"
                for s in sources[:4]
            ])

            messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
            for h in history[-4:]:
                messages.append({"role": "user" if h["sender"] == "user" else "assistant", "content": h["content"]})

            messages.append({"role": "user", "content": f"Document context:\n{context_snippets}\n\nQuestion: {query}"})

            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 500
            }

            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    text = data["choices"][0]["message"]["content"]
                    max_score = max([s["relevance_score"] for s in sources], default=0.0)
                    needs_escalation = "escalate" in text.lower() or max_score < 0.5
                    return {
                        "content": text,
                        "confidence_score": round(max_score, 2),
                        "escalation_suggested": needs_escalation
                    }
        except Exception as e:
            print(f"OpenAI API request note: {e}")
        return None

    def _generate_follow_ups(self, query: str, sources: List[Dict[str, Any]], escalation: bool) -> List[str]:
        q_lower = query.lower()
        if escalation:
            return [
                "How do I submit an escalation ticket to faculty?",
                "Who is the Head of the Department?",
                "Where can I find faculty office hours?"
            ]
        if "attendance" in q_lower or "%" in q_lower:
            return [
                "What is the medical condonation fee?",
                "What happens if attendance is below 65%?",
                "How do I apply for official duty (OD) leave?"
            ]
        if "exam" in q_lower or "timetable" in q_lower:
            return [
                "What are the exam hall rules and timings?",
                "Can I bring a programmable calculator?",
                "When will semester results be announced?"
            ]
        if "os" in q_lower or "operating systems" in q_lower or "cs301" in q_lower:
            return [
                "When is the CS301 project submission deadline?",
                "What are the prescribed textbooks for Operating Systems?",
                "What topics are included in Unit 2?"
            ]
        return [
            "Can you explain this in simpler terms?",
            "What documents support this rule?",
            "Can I escalate this to my faculty member?"
        ]


academic_agent = AcademicAgent()
