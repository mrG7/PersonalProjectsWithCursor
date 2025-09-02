# 🎓 Course/Lecture Manager - Cursor Example Project

A minimal, runnable example that models a course with lectures/classes you can develop and manage inside Cursor. It mirrors the structure of other examples in this repo and can be used as a template for building education workflows.

## 🚀 Quick Start

```bash
cd examples/course_manager

# (Optional) Create venv and install deps
pip install -r requirements.txt

# Run demo (creates a course and prints a summary)
python -m src.main

# Output syllabus as JSON
python -m src.main --list
```

## 📁 Structure

```
📁 examples/course_manager
├── README.md
├── requirements.txt
├── course_manager.prompt
└── src
    ├── __init__.py
    ├── course_manager.py
    └── main.py
```

## ✨ Features

- **Model Courses & Lectures**: In‑memory `Course` and `Lecture` entities
- **Syllabus Demo**: Preconfigured "Intro to AI Agents with Cursor" course
- **CLI**: Create demo syllabus or print JSON for downstream tools
- **Prompt**: Agent prompt to plan, author, and iterate course materials

## 🧰 Usage in Cursor

- Open `course_manager.prompt` and run as an agent to plan or expand the syllabus
- Extend `src/course_manager.py` with storage, grading, assignments, etc.
- Use with multi‑agent orchestration to coordinate content creation and review

## 🔄 Next Steps (Ideas)

- Persistence (e.g., JSON/SQLite), assignment tracker, grading rubric generator
- Lecture slide generator (Markdown → PDF), quiz builder with item bank
- LLM‑assisted syllabus versioning and prerequisites mapping

---

Built to be small, clear, and easy to extend alongside other examples.


