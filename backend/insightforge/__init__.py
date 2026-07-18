"""
CourseForge AI — InsightForge Adapter Package

This package is the ONLY point of contact between CourseForge and InsightForge-AI.

All CourseForge services that need AI capabilities (RAG, embeddings, retrieval)
import exclusively from this package. They never import InsightForge internals directly.

Architecture:
    engine.py   — InsightForgeEngine class (the public adapter)
    adapter.py  — Low-level InsightForge import shim + namespace-aware query adapter
    config.py   — InsightForge-specific configuration

Usage:
    from insightforge.engine import InsightForgeEngine
    engine = InsightForgeEngine()
    result = engine.query("What is machine learning?", doc_ids=["abc-123"])
"""
