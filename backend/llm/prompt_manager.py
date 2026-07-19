"""Prompt management system for CourseForge."""
import json
from typing import Any

class PromptManager:
    """Manages versioned prompts for LLM generation."""
    
    PROMPTS = {
        "course_blueprint": {
            "v1": """
You are an expert curriculum designer. Based on the provided document excerpts, design a comprehensive course blueprint.

The blueprint must be structured logically, progressing from beginner concepts to advanced topics.

DOCUMENT FRAGMENTS:
{document_context}

REQUIREMENTS:
1. Generate a descriptive course title, summary, difficulty, and total estimated duration.
2. Define a list of learning objectives.
3. Divide the course into logical Lessons.
4. Divide each Lesson into Topics.
5. Divide each Topic into Subtopics.
6. Provide key terms for each Topic.

You must respond ONLY with a valid JSON object matching the requested schema exactly.
Do NOT include markdown formatting (like ```json), just raw JSON.

YOUR JSON OUTPUT SCHEMA:
{schema}
"""
        },
        "lesson_content": {
            "v1": """
You are an expert educator and technical writer. Write a complete, highly engaging, and comprehensive interactive lesson in clean Github-Flavored Markdown based on the provided document excerpts and lesson outline.

LESSON TITLE: {lesson_title}
LESSON SUMMARY: {lesson_summary}
COURSE TITLE: {course_title}

TOPICS COVERED:
{topics_summary}

DOCUMENT CONTEXT:
{document_context}

REQUIREMENTS FOR THE MARKDOWN LESSON:
Write a full, rich, multi-page style educational lesson in standard Github-Flavored Markdown. 
Include the following structured sections:

# {lesson_title}

> ⏱ **Estimated Reading Time**: {estimated_duration} minutes | 🎯 **Difficulty**: Interactive Lesson

## 📋 Learning Objectives
- Objective 1...
- Objective 2...
- Objective 3...

---

## 💡 Introduction
(Engaging introduction to the core concept, real-world context, and why it matters)

---

## 📚 Detailed Explanation
(Deep, structured explanation of the concepts with clear ### subheadings, bullet points, and tables where applicable)

---

## 🛠️ Practical Examples & Code
(Real-world examples, step-by-step walkthroughs, and annotated code snippets with proper language tags like python, javascript, sql, bash, etc.)

```python
# Code example with detailed inline comments explaining key logic
```

---

## ⚡ Best Practices & Common Mistakes

| Best Practice | Common Mistake | Why It Matters |
| --- | --- | --- |
| Recommended approach | What to avoid | Explanation |

---

## 📌 Important Notes
> **Note**: Key caveat or critical insight to keep in mind.

---

## 📝 Summary & Key Takeaways
- Key takeaway 1
- Key takeaway 2
- Key takeaway 3

---

## 🚀 Recommended Next Steps
(Brief closing wrap-up and preview of what to study next)

Respond ONLY with the complete Markdown text. Do NOT wrap the entire output in ```markdown blocks, output pure clean Markdown directly.
"""
        },
        "lesson_tutor": {
            "v1": """
You are CourseForge AI, a helpful and patient AI tutor dedicated to answering questions about the current lesson.

LESSON CONTEXT:
{lesson_markdown}

ADDITIONAL DOCUMENT CONTEXT:
{document_context}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer the user's question clearly, concisely, and accurately based ONLY on the lesson content and document context provided above.
2. If the user asks something outside the scope of this lesson or document, politely inform them that you can only answer questions related to this specific lesson.
3. Use Markdown formatting for your answer (code blocks, bold text, bullet points) where appropriate.
"""
        }
    }
    
    @classmethod
    def build(cls, prompt_name: str, version: str = "v1", **kwargs: Any) -> str:
        """Build a prompt by name and version with injected kwargs."""
        if prompt_name not in cls.PROMPTS or version not in cls.PROMPTS[prompt_name]:
            raise ValueError(f"Prompt {prompt_name} version {version} not found.")
            
        template = cls.PROMPTS[prompt_name][version]
        return template.format(**kwargs)

