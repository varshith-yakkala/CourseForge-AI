# Future Roadmap

This document outlines the planned trajectory for CourseForge post-v0.6.0.

## Phase 7: AI Course Generation (Layer 2)
- Implement Just-In-Time (JIT) content generation for individual lessons.
- Ensure the AI tutor maintains the persona of a domain expert.
- Cache the generated content in the database to optimize LLM API costs.

## Phase 8: Interactive Quizzes & Flashcards
- Generate dynamic multiple-choice quizzes per lesson.
- Generate spaced-repetition flashcards based on Topic `key_terms`.
- Track user attempts and scores.

## Phase 9: AI Tutor & Chat Integration
- Introduce an interactive chat session for each course/lesson.
- Allow users to ask follow-up questions, relying on the InsightForge context window for accurate RAG answers.

## Phase 10: Gamification & Analytics
- Track granular user progress (time spent, completion percentage).
- Issue verifiable certificates upon course completion.
- Provide a platform-wide admin dashboard.
