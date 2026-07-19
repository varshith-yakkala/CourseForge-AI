# Contributing to CourseForge AI

Thank you for your interest in contributing to CourseForge AI!

---

## Development Workflow

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/varshith-yakkala/CourseForge-AI.git
   ```
2. Set up virtual environment & dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate # or .venv\Scripts\activate on Windows
   pip install -r backend/requirements.txt
   ```
3. Set up frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
4. Run backend tests:
   ```bash
   pytest
   ```
5. Run frontend tests & build verification:
   ```bash
   npm test
   npm run build
   ```
