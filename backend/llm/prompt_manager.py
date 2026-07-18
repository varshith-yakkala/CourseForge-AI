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
        }
    }
    
    @classmethod
    def build(cls, prompt_name: str, version: str = "v1", **kwargs: Any) -> str:
        """Build a prompt by name and version with injected kwargs."""
        if prompt_name not in cls.PROMPTS or version not in cls.PROMPTS[prompt_name]:
            raise ValueError(f"Prompt {prompt_name} version {version} not found.")
            
        template = cls.PROMPTS[prompt_name][version]
        return template.format(**kwargs)
