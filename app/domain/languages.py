"""Every language a course can teach, and how each external platform names it.

The course catalog references languages by `id`; tutorial providers translate that id into
their own vocabulary (Stack Overflow tags, DEV tags, search phrases).
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageInfo:
    id: str
    name: str
    stackoverflow_tag: str
    devto_tag: str
    # Appended to Wikipedia searches; Wikipedia titles pages like "Closure (computer programming)",
    # so for general-purpose languages "programming" finds more than the language name does.
    wikipedia_context: str
    # The language's track on Exercism (exercism.org), which supplies its practice exercises.
    exercism_track: str


LANGUAGES: dict[str, LanguageInfo] = {
    lang.id: lang
    for lang in (
        LanguageInfo("python", "Python", "python", "python", "programming", "python"),
        LanguageInfo("javascript", "JavaScript", "javascript", "javascript", "JavaScript", "javascript"),
        LanguageInfo("sql", "SQL", "sql", "sql", "SQL", "sqlite"),
        LanguageInfo("typescript", "TypeScript", "typescript", "typescript", "TypeScript", "typescript"),
        LanguageInfo("java", "Java", "java", "java", "Java", "java"),
        LanguageInfo("csharp", "C#", "c#", "csharp", "C#", "csharp"),
        LanguageInfo("cpp", "C++", "c++", "cpp", "C++", "cpp"),
        LanguageInfo("c", "C", "c", "c", "C programming language", "c"),
        LanguageInfo("php", "PHP", "php", "php", "PHP", "php"),
        LanguageInfo("go", "Go", "go", "go", "Go programming language", "go"),
        LanguageInfo("rust", "Rust", "rust", "rust", "Rust programming language", "rust"),
        LanguageInfo("kotlin", "Kotlin", "kotlin", "kotlin", "Kotlin", "kotlin"),
        LanguageInfo("swift", "Swift", "swift", "swift", "Swift programming language", "swift"),
    )
}


def language(language_id: str | None) -> LanguageInfo | None:
    return LANGUAGES.get(language_id or "")


# Content about these is still useful for the other (a superset, or a close sibling).
_RELATED = {
    "typescript": {"javascript"},
    "javascript": {"typescript"},
    "cpp": {"c"},
    "c": {"cpp"},
    "kotlin": {"java"},
    "java": {"kotlin"},
}


def _name_pattern(name: str) -> re.Pattern[str]:
    # "C" must not match inside "C#"/"C++", and "Java" must not match inside "JavaScript".
    return re.compile(rf"(?<![\w#+]){re.escape(name)}(?![\w#+])")


_PATTERNS = {lang.id: _name_pattern(lang.name) for lang in LANGUAGES.values()}


def mentions_language(language_id: str, text: str) -> bool:
    """Whether the text names the language (case-sensitive, so "Go" isn't the verb "go")."""
    pattern = _PATTERNS.get(language_id)
    return bool(pattern and pattern.search(text))


def names_other_language(language_id: str, text: str) -> bool:
    """Whether the text is about a different, unrelated language — e.g. a "C data types" page for a C# lesson."""
    allowed = {language_id, *_RELATED.get(language_id, set())}
    return any(pattern.search(text) for lid, pattern in _PATTERNS.items() if lid not in allowed)
