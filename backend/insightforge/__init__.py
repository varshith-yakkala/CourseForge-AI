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
import sys
from pathlib import Path

# Ensure project root and backend directory are in sys.path automatically regardless of execution directory
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
project_root = backend_dir.parent

for p in (str(project_root), str(backend_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Ensure module aliases resolve cleanly
current_mod = sys.modules.get(__name__)
if current_mod:
    sys.modules.setdefault("backend.insightforge", current_mod)
    sys.modules.setdefault("insightforge", current_mod)

