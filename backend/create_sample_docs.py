import csv
from pathlib import Path
from docx import Document as DocxDocument
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

DOCS_DIR = Path(__file__).resolve().parent / "sample_documents"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def generate_attendance_policy_pdf():
    pdf_path = DOCS_DIR / "Academic_Regulations_and_Attendance_Policy_2026.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(54, height - 54, "CENTRAL UNIVERSITY OF ENGINEERING & TECHNOLOGY")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, height - 76, "Academic Regulations & Attendance Policy Handbook (2025-2026)")
    c.setFont("Helvetica", 10)
    c.drawString(54, height - 92, "Document Reference: CUET/ACAD/REG/2026/01 | Approved by Academic Senate")
    c.line(54, height - 98, width - 54, height - 98)

    y = height - 125
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y, "1. Minimum Attendance Requirement (75% Standard)")
    y -= 18
    c.setFont("Helvetica", 10)
    text1 = [
        "A student shall be eligible to appear in the End Semester Examinations (SEE) if and only if",
        "they have acquired a minimum of 75% attendance in aggregate across all registered theory and practical subjects.",
        "Attendance is calculated from the official semester commencement date until the last instructional working day.",
        "Students with 75% or greater attendance are automatically certified to receive examination admit cards / hall tickets."
    ]
    for line in text1:
        c.drawString(54, y, line)
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y, "2. Condonation of Attendance Shortage (65% to 74%)")
    y -= 18
    c.setFont("Helvetica", 10)
    text2 = [
        "Condonation of shortage of attendance between 65% and 74% (inclusive) may be recommended by the Dean of Academic Affairs",
        "on valid medical grounds (prolonged illness/hospitalization) or university-authorized participation in national sports, NCC, or NSS.",
        "The prescribed condonation fee of Rs. 1,500 must be deposited with the bursar along with an authentic medical certificate issued",
        "by a registered medical practitioner and countersigned by the University Chief Medical Officer.",
        "Application for condonation must be submitted at least 7 working days prior to examination commencement."
    ]
    for line in text2:
        c.drawString(54, y, line)
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y, "3. Detention and Re-registration (Below 65%)")
    y -= 18
    c.setFont("Helvetica", 10)
    text3 = [
        "A student who scores below 65% aggregate attendance is strictly detained and is NOT eligible to write",
        "the semester end examinations. No condonation is legally permissible below 65% under any circumstances.",
        "The student must re-register for the detained semester during the subsequent academic academic year."
    ]
    for line in text3:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(54, 40, "Page 1 of 2 - Official Regulations Handbook 2026")
    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, height - 54, "4. Evaluation, Marks Distribution & Passing Standards")
    y = height - 80
    c.setFont("Helvetica", 10)
    text4 = [
        "• Continuous Internal Assessment (CIA): 40 Marks (2 Mid-term tests, 2 quizzes, 1 capstone project/assignment).",
        "• Semester End Examination (SEE): 60 Marks (3 Hours comprehensive written examination).",
        "• Passing Minimum: Student must secure minimum 40% in SEE (24 out of 60) and 40% aggregate overall (40 out of 100).",
        "• Grading System: 10-point scale: O (90-100), A+ (80-89), A (70-79), B+ (60-69), B (50-59), C (40-49), F (Below 40 - Fail).",
        "• Grade Point Average (GPA): Computed as Sum(Credits * GradePoints) / Total Registered Credits."
    ]
    for line in text4:
        c.drawString(54, y, line)
        y -= 16

    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y, "5. Grievance and Dispute Escalation")
    y -= 18
    c.setFont("Helvetica", 10)
    text5 = [
        "Any disputes regarding attendance calculation discrepancies must be escalated to the Subject Teacher and Head of Department",
        "within 3 days of publication of the attendance roster. Academic appeals for grade reviews must be filed with the Controller",
        "of Examinations within 10 days of grade publication."
    ]
    for line in text5:
        c.drawString(54, y, line)
        y -= 14

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(54, 40, "Page 2 of 2 - End of Document")
    c.save()
    print("Created:", pdf_path)


def generate_exam_timetable_pdf():
    pdf_path = DOCS_DIR / "Mid_Semester_Examination_Guidelines_and_Timetable.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(54, height - 54, "OFFICE OF THE CONTROLLER OF EXAMINATIONS")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, height - 76, "Mid-Semester Examination Schedule & Guidelines - Fall 2026")
    c.line(54, height - 84, width - 54, height - 84)

    y = height - 110
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y, "1. Examination Timetable (B.Tech Computer Science - Semester 6)")
    y -= 22

    # Timetable entries
    schedule = [
        ("Date", "Subject Code", "Subject Name", "Timings", "Venue"),
        ("2026-10-26 (Monday)", "CS301", "Operating Systems", "10:00 AM - 12:00 PM", "Hall A, Academic Block 2"),
        ("2026-10-28 (Wednesday)", "CS302", "Database Management Systems", "10:00 AM - 12:00 PM", "Hall A, Academic Block 2"),
        ("2026-10-30 (Friday)", "CS303", "Computer Networks", "10:00 AM - 12:00 PM", "Hall B, Academic Block 2"),
        ("2026-11-02 (Monday)", "CS304", "Artificial Intelligence & ML", "10:00 AM - 12:00 PM", "Hall B, Academic Block 2"),
        ("2026-11-04 (Wednesday)", "CS305", "Cloud Computing & DevOps", "10:00 AM - 12:00 PM", "Hall C, Academic Block 1"),
    ]

    for row_idx, row in enumerate(schedule):
        if row_idx == 0:
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(colors.navy)
        else:
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.black)
        
        c.drawString(54, y, row[0])
        c.drawString(180, y, row[1])
        c.drawString(240, y, row[2])
        c.drawString(410, y, row[3])
        c.drawString(510, y, row[4])
        y -= 18

    y -= 15
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(54, y, "2. Mandatory Candidate Instructions")
    y -= 18
    c.setFont("Helvetica", 10)
    instructions = [
        "1. Hall Tickets: Physical or verified digital hall ticket is strictly mandatory. No entry without University ID card.",
        "2. Seating: Seating plans will be displayed on the notice board 30 minutes before commencement.",
        "3. Late Arrival: Candidates arriving more than 15 minutes after commencement will NOT be permitted into the exam hall.",
        "4. Prohibited Items: Mobile phones, smartwatches, programmable calculators, and unauthorized papers are strictly banned.",
        "5. Malpractice: Possession of unauthorized material will lead to immediate cancellation of exam and disciplinary hearing.",
        "6. Emergency Help: Any clash in examination dates must be reported to the Exam Cell via escalation within 48 hours."
    ]
    for ins in instructions:
        c.drawString(54, y, ins)
        y -= 15

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(54, 40, "Page 1 of 1 - Examination Cell Official Notification")
    c.save()
    print("Created:", pdf_path)


def generate_os_syllabus_docx():
    docx_path = DOCS_DIR / "CS301_Operating_Systems_Syllabus_and_Deadlines.docx"
    doc = DocxDocument()
    doc.add_heading("CS301: Operating Systems - Course Syllabus & Deadlines", level=0)
    
    doc.add_paragraph("Instructor: Prof. Sharma (CSE Department) | Academic Year: 2025-2026 | Credits: 4")
    doc.add_paragraph("Course Objectives: Learn fundamental concepts of process management, threads, concurrency, deadlocks, memory management, and file systems.")

    doc.add_heading("Unit I: Process Management and CPU Scheduling", level=1)
    doc.add_paragraph("Processes, Process Control Blocks (PCB), Process States, Context Switching. CPU Scheduling algorithms: FCFS, SJF, Priority, Round Robin, Multilevel Feedback Queues. Turnaround time and waiting time analysis.")

    doc.add_heading("Unit II: Process Synchronization & Concurrency", level=1)
    doc.add_paragraph("The Critical-Section Problem, Peterson's Solution, Synchronization Hardware. Semaphores, Mutex Locks, Classic Synchronization Problems (Dining Philosophers, Bounded-Buffer, Readers-Writers).")

    doc.add_heading("Unit III: Deadlocks", level=1)
    doc.add_paragraph("Deadlock Characterization, Resource Allocation Graphs. Deadlock Prevention, Avoidance (Banker's Algorithm), Detection, and Recovery strategies.")

    doc.add_heading("Unit IV: Memory Management & Virtual Memory", level=1)
    doc.add_paragraph("Logical vs Physical Address Space, Swapping, Contiguous Memory Allocation, Paging, Segmentation. Virtual Memory, Demand Paging, Page Replacement Algorithms (FIFO, LRU, Optimal), Thrashing.")

    doc.add_heading("Important Course Deadlines & Project Requirements", level=1)
    doc.add_paragraph("1. Assignment 1 (Process Scheduling Simulator): Due Date October 20, 2026 (11:59 PM)")
    doc.add_paragraph("2. Mid-Semester Exam: October 26, 2026 (10:00 AM - 12:00 PM in Hall A)")
    doc.add_paragraph("3. Term Project (Custom Shell or Thread Pool Implementation): Due Date November 15, 2026")
    doc.add_paragraph("Late submission penalty: 10% deducted per day for up to 3 days. Submissions after 3 days receive zero marks unless approved by faculty.")

    doc.add_heading("Prescribed Textbooks", level=1)
    doc.add_paragraph("• Operating System Concepts, 10th Edition by Silberschatz, Galvin, and Gagne.")
    doc.add_paragraph("• Modern Operating Systems, 4th Edition by Andrew S. Tanenbaum.")
    
    doc.save(str(docx_path))
    print("Created:", docx_path)


def generate_dbms_syllabus_docx():
    docx_path = DOCS_DIR / "CS302_Database_Management_Systems_Notes_and_Assignments.docx"
    doc = DocxDocument()
    doc.add_heading("CS302: Database Management Systems - Syllabus & Lab Guide", level=0)
    
    doc.add_paragraph("Instructor: Dr. Anita (Data Science & CSE) | Credits: 4")

    doc.add_heading("Course Modules & Topics", level=1)
    doc.add_paragraph("Module 1: Relational Model, Entity-Relationship (ER) Modeling, Extended ER, Relational Algebra and Tuple Calculus.")
    doc.add_paragraph("Module 2: Structured Query Language (SQL), Complex Queries, Triggers, Views, and Stored Procedures.")
    doc.add_paragraph("Module 3: Relational Database Design & Normalization: 1NF, 2NF, 3NF, BCNF, 4NF. Functional dependencies, Lossless decomposition.")
    doc.add_paragraph("Module 4: Transaction Management & Concurrency Control: ACID properties, Serializability, Two-Phase Locking (2PL), Deadlocks, Write-Ahead Logging.")
    doc.add_paragraph("Module 5: Indexing and Storage: B-Trees, B+ Trees, Hashing, Query optimization.")

    doc.add_heading("Laboratory Assignments & Due Dates", level=1)
    doc.add_paragraph("• Lab Assignment 1 (Advanced SQL & Window Functions): Submission deadline October 25, 2026.")
    doc.add_paragraph("• Lab Assignment 2 (Normalization & Schema Refinement): Submission deadline November 10, 2026.")
    doc.add_paragraph("• Final Database Project: Schema design and full-stack integration demo due December 02, 2026.")

    doc.save(str(docx_path))
    print("Created:", docx_path)


def generate_lab_guidelines_txt():
    txt_path = DOCS_DIR / "Lab_Safety_and_Project_Submission_Guidelines.txt"
    content = """# CENTRAL UNIVERSITY - COMPUTER LABORATORY SAFETY & PROJECT GUIDELINES
Document ID: CUET/LAB/GUIDELINES/2026

1. GENERAL LAB PROTOCOLS
- All students must wear designated college ID badges and check in with the lab technician upon entry.
- Eating, drinking, or open beverages are strictly prohibited near terminal workstations.
- Workstations must be shut down and chairs arranged before leaving the premises.
- Standard computer lab timings: Monday to Friday, 8:30 AM to 6:30 PM. Saturday open access: 9:00 AM to 1:00 PM.

2. SOFTWARE & NETWORK USAGE POLICY
- Installing unauthorized cracked tools, peer-to-peer torrent software, or cryptocurrency miners is strictly banned.
- All lab machines are equipped with Linux Ubuntu 24.04 LTS and Windows 11 dual boot environments.
- Default developer toolchains provided: Python 3.12, Node.js v24, GCC 13, Docker Engine, PostgreSQL 16.
- Cloud cluster access for deep learning workloads requires prior approval from Dr. Anita.

3. ACADEMIC INTEGRITY & CODE PLAGIARISM PENALTIES
- All code submissions for assignments and projects are processed through automated MOSS (Measure of Software Similarity) checks.
- Similarity index exceeding 25% with peer submissions or online repositories without explicit attribution results in:
  * First offense: Zero marks for the assignment and formal warning on institutional student record.
  * Second offense: Deduction of one full letter grade in the course and escalation to the Academic Disciplinary Committee.
- GenAI assistance (ChatGPT, Gemini, GitHub Copilot) is permitted ONLY for code explanation and syntax debugging, NOT for copy-pasting entire assignment solutions.

4. PROJECT SUBMISSION CHECKLIST
- Projects must include:
  1. Complete source code repository with clean Git commit history.
  2. README.md with clear build and local execution instructions.
  3. Video walkthrough (2-4 minutes) demonstrating key capabilities.
  4. Project report in PDF format following the standard university formatting template.
"""
    txt_path.write_text(content, encoding="utf-8")
    print("Created:", txt_path)


def generate_scholarship_txt():
    txt_path = DOCS_DIR / "Scholarship_and_Fee_Structure_Bylaws.txt"
    content = """# UNIVERSITY SCHOLARSHIP AND FEE STRUCTURE BYLAWS (2025-2026)

1. MERIT SCHOLARSHIP SCHEMES
- Dean's Merit Scholarship: 50% tuition waiver for students achieving CGPA 9.5 or above with zero backlogs in the preceding academic year.
- Academic Excellence Award: 25% tuition waiver for students achieving CGPA between 9.0 and 9.49.
- Need-Cum-Merit Support: Partial financial assistance available for students whose combined family annual income is below Rs. 3,50,000.
- Application Deadline: Applications for scholarship renewals must be submitted through the student portal by November 15, 2026.

2. SEMESTER TUITION FEE SCHEDULE
- B.Tech Semester Tuition Fee: Rs. 65,000 per semester.
- Laboratory & Computing Facilities Fee: Rs. 10,000 per semester.
- Examination Fee: Rs. 2,500 per semester.
- Standard Fee Payment Deadline: August 25 for Fall Semester; January 15 for Spring Semester.

3. LATE FEE SLABS
- 1 to 10 days delay: Rs. 500 flat fine.
- 11 to 20 days delay: Rs. 1,500 fine.
- Beyond 20 days: Enrollment temporarily suspended until fee clearing and written approval from Registrar.

4. REFUND AND WITHDRAWAL POLICY
- 100% refund (minus Rs. 1,000 processing charges) if withdrawal request is formally submitted 15 days prior to semester start.
- 50% refund if withdrawal request is submitted within 15 days after commencement of classes.
- Zero tuition refund after 30 instructional days.
"""
    txt_path.write_text(content, encoding="utf-8")
    print("Created:", txt_path)


def generate_academic_calendar_csv():
    csv_path = DOCS_DIR / "Academic_Calendar_Fall_2026.csv"
    headers = ["Date", "Event_Title", "Event_Type", "Target_Audience", "Venue_or_Medium", "Remarks"]
    rows = [
        ["2026-08-10", "Fall Semester Commencement", "Instructional", "All B.Tech Students", "Main Auditorium", "Orientation and commencement of theory classes"],
        ["2026-09-05", "Teachers Day & Academic Seminar", "Cultural", "Faculty and Students", "Convention Hall", "Holiday for classroom lectures after 1:00 PM"],
        ["2026-10-15", "Mid-Semester Roster Publication", "Academic", "All Students", "Student Portal", "Check provisional attendance percentages"],
        ["2026-10-20", "CS301 Assignment 1 Submission", "Deadline", "B.Tech CSE Sem 6", "LMS Portal", "Operating systems process scheduler implementation"],
        ["2026-10-25", "CS302 DBMS Lab 1 Submission", "Deadline", "B.Tech CSE Sem 6", "LMS Portal", "Advanced SQL queries and indexing lab"],
        ["2026-10-26", "CS301 Mid-Semester Exam", "Examination", "B.Tech CSE Sem 6", "Hall A Block 2", "Operating Systems theory exam 10:00 AM - 12:00 PM"],
        ["2026-10-28", "CS302 DBMS Mid-Semester Exam", "Examination", "B.Tech CSE Sem 6", "Hall A Block 2", "Database Management Systems exam 10:00 AM - 12:00 PM"],
        ["2026-10-30", "CS303 Computer Networks Exam", "Examination", "B.Tech CSE Sem 6", "Hall B Block 2", "Computer Networks exam 10:00 AM - 12:00 PM"],
        ["2026-11-05", "Mid-Semester Break / Festival Holiday", "Holiday", "All University", "Campus Closed", "Classes resume November 09, 2026"],
        ["2026-11-15", "CS301 Capstone Project Submission", "Deadline", "B.Tech CSE Sem 6", "GitLab / LMS", "Custom shell / thread pool project submission"],
        ["2026-11-25", "Last Date for Medical Condonation", "Policy", "Students with 65-74%", "Dean Academic Office", "Submit medical certificates and fee payment receipts"],
        ["2026-12-05", "Last Instructional Working Day", "Academic", "All Students", "Classrooms", "Final attendance and internal marks consolidation"],
        ["2026-12-12", "Semester End Examinations (SEE)", "Examination", "All Students", "Exam Halls", "Comprehensive semester theory examinations"]
    ]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print("Created:", csv_path)


if __name__ == "__main__":
    generate_attendance_policy_pdf()
    generate_exam_timetable_pdf()
    generate_os_syllabus_docx()
    generate_dbms_syllabus_docx()
    generate_lab_guidelines_txt()
    generate_scholarship_txt()
    generate_academic_calendar_csv()
    print("All sample academic documents created successfully!")
