"""
CourseForge AI — Prompt Manager

Loads versioned prompt templates from disk and fills them with context variables.

Design principles (from architecture spec Section 6.1):
    - Prompts are NEVER hardcoded in service files.
    - Every prompt lives in prompts/v{N}/ as a plain text file.
    - Version is explicit — A/B testing requires adding prompts/v2/ only.
    - Templates use {variable} Python str.format() placeholders.

Usage:
    from prompts.prompt_manager import PromptManager

    manager = PromptManager(version="v1")
    prompt = manager.build("quiz_mcq", context={"topic": "Neural Networks", "chunks": "..."})

Adding a new prompt:
    1. Create prompts/v1/your_new_prompt.txt
    2. Call manager.build("your_new_prompt", context={...})
    No code changes needed.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_PROMPTS_ROOT = Path(__file__).parent


class PromptManager:
    """
    Loads and renders versioned prompt templates.

    Templates use Python str.format_map() with a context dict.
    Missing keys raise KeyError with a clear error message.
    Extra keys in context are silently ignored.

    Args:
        version: Prompt version directory name, e.g. "v1".

    Raises:
        FileNotFoundError: If the version directory does not exist.
        FileNotFoundError: If a requested prompt template does not exist.
        KeyError: If a required template variable is missing from context.
    """

    def __init__(self, version: str = "v1") -> None:
        self._version = version
        self._version_dir = _PROMPTS_ROOT / version

        if not self._version_dir.exists():
            raise FileNotFoundError(
                f"Prompt version directory not found: {self._version_dir}\n"
                f"Available versions: {[d.name for d in _PROMPTS_ROOT.iterdir() if d.is_dir()]}"
            )

        self._cache: dict[str, str] = {}
        logger.debug("PromptManager initialized.", extra={"version": version})

    def load(self, name: str) -> str:
        """
        Load a raw prompt template by name (without .txt extension).

        Results are cached in memory for the lifetime of this instance.

        Args:
            name: Template file name without extension, e.g. "quiz_mcq".

        Returns:
            Raw template string with {placeholders}.

        Raises:
            FileNotFoundError: If template file does not exist.
        """
        if name not in self._cache:
            path = self._version_dir / f"{name}.txt"
            if not path.exists():
                available = [f.stem for f in self._version_dir.glob("*.txt")]
                raise FileNotFoundError(
                    f"Prompt template '{name}' not found in {self._version_dir}.\n"
                    f"Available templates: {available}"
                )
            self._cache[name] = path.read_text(encoding="utf-8")
            logger.debug("Prompt template loaded.", extra={"name": name, "version": self._version})

        return self._cache[name]

    def build(self, name: str, context: dict[str, str]) -> str:
        """
        Load a template and fill it with context variables.

        Args:
            name:    Template name (without .txt).
            context: Dict of {placeholder: value} pairs.

        Returns:
            Fully rendered prompt string ready for LLM submission.

        Raises:
            FileNotFoundError: If template does not exist.
            KeyError: If a required placeholder is missing from context.
        """
        template = self.load(name)
        try:
            return template.format_map(context)
        except KeyError as exc:
            raise KeyError(
                f"Prompt template '{name}' requires variable {exc} "
                f"but it was not provided in context. "
                f"Provided keys: {list(context.keys())}"
            ) from exc

    def list_templates(self) -> list[str]:
        """Return all available template names for this version."""
        return [f.stem for f in self._version_dir.glob("*.txt")]
