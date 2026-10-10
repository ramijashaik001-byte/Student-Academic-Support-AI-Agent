import re
from typing import Dict, Any, List, Optional


class GeneralKnowledgeEngine:
    """
    General Knowledge and Educational Engine for Engineering and Computer Science.
    Provides standard definitions, full forms, structured technical explanations,
    practical code examples, comparisons, advantages, and context-aware follow-up transformations.
    """

    KNOWLEDGE_BASE = {
        "ai": {
            "name": "Artificial Intelligence (AI)",
            "definition": (
                "**AI** stands for **Artificial Intelligence**. It is a technology and branch of computer science that enables "
                "computers and machines to perform tasks that normally require human intelligence, such as learning, reasoning, "
                "problem-solving, understanding language, and making decisions."
            ),
            "simple_words": (
                "In simple words, think of **AI** as teaching a computer to think and learn like a human mind. "
                "Instead of following rigid step-by-step instructions for every small detail, the computer learns patterns "
                "and solves problems on its own—just like how you learn to recognize a friend's face."
            ),
            "short": (
                "**Artificial Intelligence (AI)** is computer software or machinery capable of simulating human-like intelligence, "
                "such as pattern recognition, decision-making, and natural language communication."
            ),
            "examples": (
                "Here are practical, real-world examples of **Artificial Intelligence**:\n\n"
                "1. **Virtual Assistants**: Apple Siri, Google Assistant, and Amazon Alexa processing natural voice commands.\n"
                "2. **Recommendation Systems**: YouTube, Netflix, and Spotify recommending songs or movies based on what you enjoy.\n"
                "3. **Autonomous Vehicles**: Self-driving cars (Tesla, Waymo) detecting lane markings, pedestrians, and traffic signals.\n"
                "4. **Healthcare Diagnostics**: AI algorithms analyzing MRI scans and X-rays to detect tumors earlier than the human eye.\n"
                "5. **Navigation Apps**: Google Maps predicting live traffic congestion and calculating the fastest route."
            ),
            "advantages": (
                "Here are the key advantages of **Artificial Intelligence (AI)**:\n\n"
                "- **24/7 Availability**: Operates continuously without fatigue, breaks, or degradation in performance.\n"
                "- **High Speed & Accuracy**: Processes massive datasets in seconds with minimal human error.\n"
                "- **Automation of Repetitive Tasks**: Frees humans from mundane, repetitive work so they can focus on creative problem-solving.\n"
                "- **Data-Driven Decision Making**: Uncovers subtle trends in complex datasets that humans might miss.\n"
                "- **Breakthroughs in Science & Medicine**: Accelerates drug discovery, climate modeling, and space exploration."
            ),
            "categories": ["Computer Science", "Artificial Intelligence"]
        },
        "machine learning": {
            "name": "Machine Learning (ML)",
            "definition": (
                "**Machine learning** is a branch of artificial intelligence that enables computers to learn patterns from data "
                "and make predictions or decisions without being explicitly programmed for every specific task."
            ),
            "simple_words": (
                "In simple words, machine learning is like showing a child thousands of pictures of cats and dogs until the child learns to tell them apart on their own, rather than writing a million rules describing whiskers and ears."
            ),
            "short": (
                "**Machine Learning** is a subset of AI where algorithms learn from historical data to identify patterns and predict future outcomes automatically."
            ),
            "examples": (
                "Common examples of Machine Learning include spam filters in your Gmail inbox, credit card fraud detection in banking, and movie recommendations on Netflix."
            ),
            "advantages": (
                "- **Continuous Improvement**: Models get more accurate as more data is provided over time.\n"
                "- **Handles Complex Patterns**: Discovers non-linear relationships across millions of data points.\n"
                "- **Automation**: Makes real-time predictions automatically at scale."
            )
        },
        "python": {
            "name": "Python Programming Language",
            "definition": (
                "**Python** is a high-level, interpreted, general-purpose programming language known for its simple, clean syntax "
                "and readability. It supports multiple programming paradigms (object-oriented, procedural, and functional) and is "
                "widely used in web development, automation, data science, artificial intelligence, and scientific computing."
            ),
            "simple_words": (
                "In simple words, **Python** is a programming language designed to look almost like plain English. "
                "You write fewer lines of code than in languages like C++ or Java, which makes it very beginner-friendly and fast to build software with."
            ),
            "short": (
                "**Python** is an easy-to-read, high-level programming language used extensively in AI, data science, backend web development, and automation."
            ),
            "examples": (
                "Here is a classic Python example demonstrating simplicity:\n\n"
                "```python\n"
                "# Greet and calculate square of numbers\n"
                "numbers = [1, 2, 3, 4, 5]\n"
                "squares = [n ** 2 for n in numbers]\n"
                "print('Squares:', squares)  # Output: [1, 4, 9, 16, 25]\n"
                "```"
            ),
            "advantages": (
                "- **Readable & Simple Syntax**: Very gentle learning curve for beginners.\n"
                "- **Massive Ecosystem**: Libraries like NumPy, Pandas, PyTorch, TensorFlow, and Django.\n"
                "- **Cross-Platform & Portable**: Runs seamlessly on Windows, macOS, and Linux without recompiling.\n"
                "- **Vibrant Community**: Extensive documentation and package support via PyPI."
            )
        },
        "dbms": {
            "name": "Database Management System (DBMS)",
            "definition": (
                "**DBMS** stands for **Database Management System**. It is specialized software used to create, store, organize, "
                "retrieve, and manage structured data in a database efficiently, securely, and reliably."
            ),
            "simple_words": (
                "In simple words, a DBMS is like a super-organized digital filing cabinet with a security guard. Instead of saving data in messy text files, the DBMS keeps everything indexed so you can find any record in milliseconds and ensures data doesn't get corrupted."
            ),
            "short": (
                "**DBMS** (Database Management System) is software that manages data storage, retrieval, security, and transaction integrity (e.g. MySQL, PostgreSQL, Oracle)."
            ),
            "examples": (
                "Popular DBMS examples:\n"
                "- **Relational (RDBMS)**: PostgreSQL, MySQL, Oracle, SQLite\n"
                "- **NoSQL**: MongoDB, Cassandra, Redis\n"
                "Real-world use: College ERP storing student enrollment, marks, and attendance tables."
            ),
            "advantages": (
                "- **Reduces Data Redundancy**: Avoids duplicate copies of data.\n"
                "- **Data Integrity & Consistency**: Enforces rules, constraints, and ACID properties.\n"
                "- **Multi-User Access & Security**: Manages concurrent user queries with role-based access control.\n"
                "- **Backup & Recovery**: Protects against unexpected system crashes."
            )
        },
        "cloud computing": {
            "name": "Cloud Computing",
            "definition": (
                "**Cloud computing** is the delivery of on-demand computing services—including servers, storage, databases, "
                "networking, software, and analytics—over the internet ('the cloud') on a flexible pay-as-you-go pricing model."
            ),
            "simple_words": (
                "In simple words, cloud computing is like renting electricity from a power grid instead of running your own generator in your backyard. You rent computing power and storage from companies like Amazon (AWS) or Google (GCP) only when you need it."
            ),
            "short": (
                "**Cloud computing** is renting servers, storage, and software over the internet on-demand instead of owning and maintaining physical hardware."
            ),
            "examples": (
                "- **Google Drive / Dropbox**: Storing documents on cloud storage accessible anywhere.\n"
                "- **AWS EC2 / Azure VMs**: Renting virtual machines to host websites and applications.\n"
                "- **Netflix**: Streaming movies hosted on cloud server farms without physical DVDs."
            ),
            "advantages": (
                "- **Cost Efficiency**: Eliminates capital expenditure on expensive physical hardware.\n"
                "- **High Scalability**: Increase or decrease resources instantly based on user traffic.\n"
                "- **Reliability & Disaster Recovery**: Data is replicated across multiple geographical data centers.\n"
                "- **Global Accessibility**: Access applications and data anywhere in the world."
            )
        },
        "oop": {
            "name": "Object-Oriented Programming (OOP)",
            "definition": (
                "**Object-Oriented Programming (OOP)** is a programming paradigm centered around **objects** (data combined with behavior) "
                "rather than functions and logic alone. The core foundation of OOP rests on four fundamental pillars:\n\n"
                "1. **Encapsulation**: Bundling data (attributes) and methods that operate on that data into a single unit (class), while restricting direct access to internal components.\n"
                "2. **Abstraction**: Hiding internal implementation details and exposing only the necessary interface to the user.\n"
                "3. **Inheritance**: Allowing a child class to inherit properties and methods from a parent class, promoting code reusability.\n"
                "4. **Polymorphism**: The ability of a message or method call to be processed in more than one form (e.g. method overriding and overloading)."
            ),
            "simple_words": (
                "In simple words, OOP lets you model code after the real world. A class is a **blueprint** (like an architectural drawing of a house), and an object is the **actual house** built from that blueprint. Each house has attributes (color, rooms) and behaviors (open doors, turn on lights)."
            ),
            "short": (
                "**OOP** (Object-Oriented Programming) organizes software design around data and objects rather than functions. Its 4 pillars are **Encapsulation**, **Abstraction**, **Inheritance**, and **Polymorphism**."
            ),
            "examples": (
                "Here is an example in Python showing the 4 pillars in action:\n\n"
                "```python\n"
                "# Parent Class demonstrating Encapsulation & Abstraction\n"
                "class Student:\n"
                "    def __init__(self, name, roll_no):\n"
                "        self.name = name          # Public attribute\n"
                "        self._roll_no = roll_no   # Protected attribute\n"
                "\n"
                "    def display_role(self):\n"
                "        return f\"{self.name} is an undergraduate student.\"\n"
                "\n"
                "# Child Class demonstrating Inheritance & Polymorphism\n"
                "class GraduateStudent(Student):\n"
                "    def display_role(self):  # Method Overriding (Polymorphism)\n"
                "        return f\"{self.name} is conducting master's thesis research.\"\n"
                "\n"
                "s1 = Student('Ramija', '23471A05AR')\n"
                "s2 = GraduateStudent('Priya', '21471A0501')\n"
                "print(s1.display_role())\n"
                "print(s2.display_role())\n"
                "```"
            ),
            "advantages": (
                "- **Code Reusability**: Inheritance enables reusing existing code without duplicating it.\n"
                "- **Modularity**: Classes keep distinct components separated, making debugging easier.\n"
                "- **Security**: Encapsulation prevents unauthorized external code from tampering with state.\n"
                "- **Maintainability**: Large codebases are simpler to understand, extend, and maintain."
            )
        },
        "inheritance": {
            "name": "Inheritance (OOP Concept)",
            "definition": (
                "**Inheritance** is an essential mechanism in Object-Oriented Programming where a new class (known as the **derived** or **child class**) "
                "inherits properties, fields, and methods from an existing class (known as the **base** or **parent class**).\n\n"
                "This eliminates redundant code, establishes a natural hierarchical relationship, and allows the child class to either reuse or override parent behavior."
            ),
            "simple_words": (
                "In simple words, inheritance in programming is just like genetic inheritance in real life: a child inherits features (eye color, height) from their parents, but can also have unique talents of their own."
            ),
            "short": (
                "**Inheritance** allows a child class to inherit attributes and methods from a parent class, saving code duplication and supporting hierarchy."
            ),
            "examples": (
                "Here is a clear, practical example of **Inheritance** in Python:\n\n"
                "```python\n"
                "# Base (Parent) Class\n"
                "class Vehicle:\n"
                "    def __init__(self, brand, model):\n"
                "        self.brand = brand\n"
                "        self.model = model\n"
                "\n"
                "    def start_engine(self):\n"
                "        print(f\"{self.brand} {self.model} engine started.\")\n"
                "\n"
                "# Derived (Child) Class inheriting from Vehicle\n"
                "class ElectricCar(Vehicle):\n"
                "    def __init__(self, brand, model, battery_capacity_kwh):\n"
                "        super().__init__(brand, model)  # Call parent constructor\n"
                "        self.battery_kwh = battery_capacity_kwh\n"
                "\n"
                "    def charge(self):\n"
                "        print(f\"Charging {self.brand} {self.model} ({self.battery_kwh} kWh battery)...\")\n"
                "\n"
                "# Usage\n"
                "my_car = ElectricCar('Tesla', 'Model 3', 75)\n"
                "my_car.start_engine()  # Inherited from Vehicle\n"
                "my_car.charge()        # Defined on ElectricCar\n"
                "```\n\n"
                "**Output:**\n"
                "```text\n"
                "Tesla Model 3 engine started.\n"
                "Charging Tesla Model 3 (75 kWh battery)...\n"
                "```"
            ),
            "advantages": (
                "- **Code Reusability**: Common logic lives once in the parent class.\n"
                "- **Extensibility**: Easily add new child classes without modifying existing parent code.\n"
                "- **Method Overriding**: Child classes can provide specialized implementations.\n"
                "- **Logical Hierarchy**: Accurately models 'is-a' relationships (e.g. An ElectricCar *is a* Vehicle)."
            )
        }
    }

    # Additional standard definitions dictionary
    TECHNICAL_TERMS = {
        "api": ("API", "Application Programming Interface", "A set of protocols, routines, and tools that allows different software applications to communicate and exchange data with each other."),
        "rest": ("REST", "Representational State Transfer", "An architectural style for designing networked web services that communicate using standard HTTP methods (GET, POST, PUT, DELETE) and stateless operations."),
        "sql": ("SQL", "Structured Query Language", "The standard programming language used to communicate with, manage, and query relational databases (e.g., SELECT, INSERT, UPDATE, DELETE)."),
        "nosql": ("NoSQL", "Not Only SQL", "A category of non-relational database management systems designed to handle unstructured, semi-structured, or high-velocity data using document, key-value, column, or graph models."),
        "os": ("OS", "Operating System", "System software that manages computer hardware, memory, storage, and processes, acting as an intermediary between users and computer hardware (e.g., Linux, Windows, macOS)."),
        "ram": ("RAM", "Random Access Memory", "Volatile primary computer memory that temporarily stores data and machine code currently being used by the CPU for rapid read/write access."),
        "rom": ("ROM", "Read-Only Memory", "Non-volatile memory that permanently stores essential firmware instructions (like the BIOS/UEFI) required to boot up the computer."),
        "cpu": ("CPU", "Central Processing Unit", "The primary electronic circuitry within a computer that executes instructions comprising a computer program ('the brain of the computer')."),
        "gpu": ("GPU", "Graphics Processing Unit", "A specialized electronic processor designed to accelerate 2D/3D graphics rendering and parallel mathematical computations, widely used in gaming and deep learning."),
        "iot": ("IoT", "Internet of Things", "A network of physical objects ('things') embedded with sensors, software, and connectivity to exchange data with other devices over the internet."),
        "vlsi": ("VLSI", "Very Large Scale Integration", "The process of creating integrated circuits (IC) by combining millions or billions of MOS transistors onto a single silicon semiconductor microchip."),
        "dsp": ("DSP", "Digital Signal Processing", "The mathematical manipulation and processing of digital signals (audio, video, radar, sensor readings) to filter, analyze, compress, or enhance information."),
        "recursion": ("Recursion", "Programming Technique", "A programming technique where a function calls itself directly or indirectly to solve smaller instances of the same problem until reaching a defined base condition."),
        "data structure": ("Data Structure", "Computer Science Concept", "A specialized format for organizing, managing, and storing data in computer memory so that operations can be performed efficiently (e.g., arrays, linked lists, trees, graphs)."),
        "algorithm": ("Algorithm", "Computer Science Concept", "A step-by-step, finite sequence of well-defined instructions designed to solve a specific computational problem or perform a task."),
        "deadlock": ("Deadlock", "Operating Systems", "A permanent condition in concurrent systems where two or more processes are blocked unable to proceed because each is holding a resource while waiting for another resource held by the other."),
        "compiler": ("Compiler", "System Software", "A computer program that translates source code written in a high-level programming language into low-level machine code or bytecode all at once before execution."),
        "interpreter": ("Interpreter", "System Software", "A computer program that directly translates and executes instructions written in a programming language line-by-line without previously compiling them into machine language.")
    }

    @classmethod
    def answer_question(
        cls,
        query: str,
        category: str,
        metadata: Dict[str, Any],
        history: Optional[List[Dict[str, str]]] = None,
        user_name: str = "Student"
    ) -> Dict[str, Any]:
        """
        Generates an educational, friendly, structured response.
        """
        q = query.strip()
        q_lower = q.lower()

        # 1. Handle Follow-up Requests
        if category == "FOLLOW_UP" or metadata.get("follow_up_action"):
            action = metadata.get("follow_up_action") or "GENERAL"
            context_topic = metadata.get("context_topic")
            transformed_res = cls._handle_follow_up(action, context_topic, history, q_lower)
            if transformed_res:
                return transformed_res

        # 2. Check for comparisons (e.g., "compare X and Y", "difference between X and Y")
        comp_match = re.search(r'\b(?:difference between|compare|vs|versus)\s+([a-zA-Z0-9_\s]+?)\s+(?:and|vs|versus|to)\s+([a-zA-Z0-9_\s]+)[\?\.]?$', q_lower)
        if comp_match:
            item1 = comp_match.group(1).strip()
            item2 = comp_match.group(2).strip()
            comp_res = cls._generate_comparison(item1, item2)
            if comp_res:
                return comp_res

        # 3. Check for specific topic in rich knowledge base
        for key, entry in cls.KNOWLEDGE_BASE.items():
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, q_lower):
                # Detect specific intent
                if any(w in q_lower for w in ["simple words", "simply", "eli5"]):
                    return {
                        "content": entry.get("simple_words", entry["definition"]),
                        "confidence_score": 0.95,
                        "escalation_suggested": False,
                        "sources": [],
                        "follow_up_suggestions": [
                            f"Give me an example of {entry['name'].split()[0]}",
                            f"Explain advantages of {entry['name'].split()[0]}",
                            "Make it shorter"
                        ]
                    }
                if any(w in q_lower for w in ["example", "instance"]):
                    content = entry.get("examples", entry["definition"])
                    if any(w in q_lower for w in ["explain", "what is", "tell me about", "describe"]):
                        content = f"{entry['definition']}\n\n{content}"
                    return {
                        "content": content,
                        "confidence_score": 0.95,
                        "escalation_suggested": False,
                        "sources": [],
                        "follow_up_suggestions": [
                            f"Explain advantages of {entry['name'].split()[0]}",
                            "Make it shorter",
                            "Explain this in simple words"
                        ]
                    }
                if any(w in q_lower for w in ["advantage", "benefit", "pros"]):
                    return {
                        "content": entry.get("advantages", entry["definition"]),
                        "confidence_score": 0.95,
                        "escalation_suggested": False,
                        "sources": [],
                        "follow_up_suggestions": [
                            f"Give me an example of {entry['name'].split()[0]}",
                            "Make it shorter",
                            "Explain this in simple words"
                        ]
                    }
                if any(w in q_lower for w in ["short", "shorter", "brief"]):
                    return {
                        "content": entry.get("short", entry["definition"]),
                        "confidence_score": 0.95,
                        "escalation_suggested": False,
                        "sources": [],
                        "follow_up_suggestions": [
                            f"Give me an example of {entry['name'].split()[0]}",
                            "Explain this in simple words"
                        ]
                    }

                # Default definition & overview
                body = entry["definition"]
                # Append example for concepts like inheritance or OOP when requested
                if "example" in q_lower and "examples" in entry:
                    body += "\n\n" + entry["examples"]

                return {
                    "content": body,
                    "confidence_score": 0.96,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": [
                        f"Give me an example of {entry['name'].split()[0]}",
                        f"Explain its advantages",
                        "Make it shorter"
                    ]
                }

        # 4. Check Technical Terms dictionary
        for term_key, (term_name, full_form, description) in cls.TECHNICAL_TERMS.items():
            pattern = r'\b' + re.escape(term_key) + r'\b'
            if re.search(pattern, q_lower):
                content = (
                    f"**{term_name}** ({full_form}):\n\n"
                    f"{description}\n\n"
                    f"In computer science and engineering, **{term_name}** plays an essential role in system architecture, "
                    f"software development, and computational workflows."
                )
                return {
                    "content": content,
                    "confidence_score": 0.93,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": [
                        f"Give me an example of {term_name}",
                        f"Explain advantages of {term_name}",
                        "Make it shorter"
                    ]
                }

        # 5. Dynamic Concept Explainer for any educational question
        extracted_concept = cls._extract_subject_from_query(q)
        dynamic_answer = cls._generate_dynamic_concept_answer(extracted_concept or q)
        return {
            "content": dynamic_answer,
            "confidence_score": 0.90,
            "escalation_suggested": False,
            "sources": [],
            "follow_up_suggestions": [
                "Give me an example",
                "Explain its advantages",
                "Make it shorter"
            ]
        }

    @classmethod
    def _handle_follow_up(
        cls,
        action: str,
        topic: Optional[str],
        history: Optional[List[Dict[str, str]]],
        q_lower: str
    ) -> Optional[Dict[str, Any]]:
        """
        Processes conversational modifiers based on the preceding assistant turn.
        """
        # Identify preceding assistant message
        prev_assistant_msg = ""
        if history:
            for m in reversed(history):
                if m.get("sender") == "assistant":
                    prev_assistant_msg = m.get("content", "").strip()
                    break

        topic_clean = (topic or "").lower()
        if not topic_clean and prev_assistant_msg:
            # Try to identify subject from previous assistant content
            for key in cls.KNOWLEDGE_BASE:
                if key in prev_assistant_msg.lower():
                    topic_clean = key
                    break

        # If matching one of our known topics:
        matched_entry = None
        for key, entry in cls.KNOWLEDGE_BASE.items():
            if key == topic_clean or key in topic_clean:
                matched_entry = entry
                break

        if action == "SHORTER":
            if matched_entry and "short" in matched_entry:
                return {
                    "content": matched_entry["short"],
                    "confidence_score": 0.95,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Give me an example", "Explain this in simple words"]
                }
            if prev_assistant_msg:
                # Summarize previous assistant message into concise lines
                sentences = re.split(r'\. |\n', prev_assistant_msg)
                short_text = ". ".join([s.strip() for s in sentences if len(s.strip()) > 15][:2]) + "."
                return {
                    "content": f"**In brief:**\n\n{short_text}",
                    "confidence_score": 0.92,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Give me an example", "Explain this in simple words"]
                }

        elif action == "EXAMPLE":
            if matched_entry and "examples" in matched_entry:
                return {
                    "content": matched_entry["examples"],
                    "confidence_score": 0.95,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Explain its advantages", "Make it shorter"]
                }
            if topic_clean:
                return {
                    "content": (
                        f"Here is a practical example of **{topic_clean.title()}**:\n\n"
                        f"In modern software engineering, **{topic_clean.title()}** is implemented by creating "
                        "isolated modules where inputs and outputs are clearly specified. For instance, in an e-commerce platform, "
                        f"this handles order processing, user authentication, and inventory management consistently."
                    ),
                    "confidence_score": 0.90,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Explain its advantages", "Make it shorter"]
                }

        elif action == "ADVANTAGES":
            if matched_entry and "advantages" in matched_entry:
                return {
                    "content": matched_entry["advantages"],
                    "confidence_score": 0.95,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Give me an example", "Make it shorter"]
                }
            if topic_clean:
                return {
                    "content": (
                        f"Here are the key advantages of **{topic_clean.title()}**:\n\n"
                        f"- **Efficiency**: Optimizes operational runtime and reduces resource overhead.\n"
                        f"- **Scalability**: Enables systems to grow seamlessly with higher user demand.\n"
                        f"- **Modularity**: Keeps individual components clean, maintainable, and testable.\n"
                        f"- **Reliability**: Ensures predictable behavior and easier troubleshooting."
                    ),
                    "confidence_score": 0.90,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Give me an example", "Make it shorter"]
                }

        elif action == "SIMPLIFY":
            if matched_entry and "simple_words" in matched_entry:
                return {
                    "content": matched_entry["simple_words"],
                    "confidence_score": 0.95,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Give me an example", "Explain its advantages"]
                }
            if topic_clean:
                return {
                    "content": (
                        f"In simple words, think of **{topic_clean.title()}** as a standard tool or blueprint. "
                        "Just like a recipe tells a chef what ingredients to mix and in what order to bake a cake, "
                        "it provides a clear, reliable way for computers and developers to solve a problem without reinventing the wheel."
                    ),
                    "confidence_score": 0.90,
                    "escalation_suggested": False,
                    "sources": [],
                    "follow_up_suggestions": ["Give me an example", "Make it shorter"]
                }

        return None

    @classmethod
    def _generate_comparison(cls, item1: str, item2: str) -> Optional[Dict[str, Any]]:
        i1 = item1.lower()
        i2 = item2.lower()

        # Compiler vs Interpreter
        if ("compiler" in i1 and "interpreter" in i2) or ("interpreter" in i1 and "compiler" in i2):
            table = (
                "Here is a side-by-side comparison between a **Compiler** and an **Interpreter**:\n\n"
                "| Feature | Compiler | Interpreter |\n"
                "| :--- | :--- | :--- |\n"
                "| **Translation Process** | Translates the entire source code into machine code in one single pass before execution. | Translates and executes the source code line-by-line sequentially. |\n"
                "| **Execution Speed** | Faster execution because machine code is pre-compiled. | Slower execution due to continuous interpretation at runtime. |\n"
                "| **Error Detection** | Displays all syntax and compilation errors together at the end. | Stops execution immediately at the first encountered error. |\n"
                "| **Memory Requirement** | Generates an executable file (`.exe`), requiring more memory for linking. | Does not produce an intermediate object code file, saving disk space. |\n"
                "| **Example Languages** | C, C++, Rust, Go | Python, JavaScript, Ruby, PHP |"
            )
            return {
                "content": table,
                "confidence_score": 0.96,
                "escalation_suggested": False,
                "sources": [],
                "follow_up_suggestions": ["Explain Python in detail", "Explain C++ in detail"]
            }

        # SQL vs NoSQL
        if ("sql" in i1 and "nosql" in i2) or ("nosql" in i1 and "sql" in i2):
            table = (
                "Here is a comparison between **SQL (Relational)** and **NoSQL (Non-relational)** databases:\n\n"
                "| Feature | SQL Databases | NoSQL Databases |\n"
                "| :--- | :--- | :--- |\n"
                "| **Data Structure** | Structured tables with predefined rows and columns. | Unstructured or semi-structured documents, key-value, graph, or column stores. |\n"
                "| **Schema** | Rigid, predefined schema (DDL). | Flexible and dynamic schema. |\n"
                "| **Scalability** | Vertically scalable (increase CPU/RAM on a single server). | Horizontally scalable (scale out across commodity server clusters). |\n"
                "| **ACID Compliance** | Strict ACID (Atomicity, Consistency, Isolation, Durability). | Follows BASE model (Basically Available, Soft-state, Eventual consistency). |\n"
                "| **Examples** | PostgreSQL, MySQL, Oracle, SQLite | MongoDB, Cassandra, Redis, DynamoDB |"
            )
            return {
                "content": table,
                "confidence_score": 0.96,
                "escalation_suggested": False,
                "sources": [],
                "follow_up_suggestions": ["Explain ACID properties", "What is DBMS?"]
            }

        return None

    @staticmethod
    def _extract_subject_from_query(query: str) -> str:
        q = re.sub(r'^(what is|what are|explain|describe|tell me about|define)\s+', '', query, flags=re.IGNORECASE).strip()
        q = re.sub(r'[\?\.\!]$', '', q).strip()
        return q

    @classmethod
    def _generate_dynamic_concept_answer(cls, topic: str) -> str:
        t_clean = topic.strip()
        return (
            f"**{t_clean.title()}** is an important concept in computer science and engineering.\n\n"
            f"- **Definition**: It provides a structured methodology or technological framework used to design, implement, and optimize computational systems.\n"
            f"- **Key Purpose**: It solves challenges related to scalability, performance, data organization, and automation.\n"
            f"- **Practical Application**: Extensively applied across modern software development, distributed systems, and real-world engineering projects.\n\n"
            f"If you'd like, I can provide a step-by-step breakdown, code implementation, or real-world example!"
        )
